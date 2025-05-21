from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Protocol

from django.conf import settings
from django.db import transaction

from reservations.models import Reservation, ReservationStatus
from restaurant.models import Restaurant, Table


@dataclass
class BookingRequest:
    restaurant: Restaurant
    user: settings.AUTH_USER_MODEL
    num_people: int
    reservation_time: datetime
    duration_hours: int = 2


class PricingStrategy(Protocol):
    def calculate_cost(self, request: BookingRequest, table: Table) -> Decimal: ...


class DefaultPricingStrategy:
    """
    Charges X per seat, but booking an entire table costs (seats - 1) * X.
    Also enforces rounding up odd requests to even or full table size.
    """

    def __init__(self, price_per_seat: Decimal):
        self.price_per_seat = price_per_seat

    def calculate_cost(self, request: BookingRequest, table: Table) -> Decimal:
        seats_requested = request.num_people
        M = table.seats
        # Round odd to next even, unless equals full table size
        if seats_requested % 2 == 1 and seats_requested != M:
            seats_requested += 1
        # Cap at table size
        seats_to_book = min(seats_requested, M)
        # Cost per logic
        if seats_to_book == M:
            cost = (M - 1) * self.price_per_seat
        else:
            cost = seats_to_book * self.price_per_seat
        return cost


class ReservationService:
    """
    Service to handle bookings and cancellations.
    """

    def __init__(
        self, pricing_strategy: PricingStrategy, default_duration_hours: int = 2
    ):
        self.pricing_strategy = pricing_strategy
        self.default_duration_hours = default_duration_hours

    def book(self, request: BookingRequest) -> Reservation:
        """
        Attempts to book the cheapest available table for the given request.
        """
        start = request.reservation_time
        end = start + timedelta(hours=request.duration_hours)
        tables = request.restaurant.get_available_tables(start, end)
        # Filter tables that have enough seats
        candidates = [t for t in tables if t.seats >= request.num_people]
        if not candidates:
            raise ValueError(
                "No tables available for the requested party size and time."
            )
        # Evaluate cost
        costs = [
            (t, self.pricing_strategy.calculate_cost(request, t)) for t in candidates
        ]
        table, cost = min(costs, key=lambda x: x[1])
        # Create reservation atomically
        with transaction.atomic():
            reservation = Reservation.objects.create(
                user=request.user,
                table=table,
                num_seats=request.num_people,
                cost=cost,
                status=ReservationStatus.PENDING,
                reservation_time=request.reservation_time,
            )
        return reservation

    def cancel(self, reservation: Reservation) -> None:
        """
        Cancels an existing reservation if possible.
        """
        if reservation.status == ReservationStatus.CANCELLED:
            return
        reservation.status = ReservationStatus.CANCELLED
        reservation.save()

from decimal import Decimal

from django.conf import settings
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from reservations.models import Reservation
from reservations.serializers import (
    BookingRequestSerializer,
    CancelReservationSerializer,
    ReservationSerializer,
)
from reservations.services import (
    BookingRequest,
    DefaultPricingStrategy,
    ReservationService,
)
from restaurant.models import Restaurant


class BookReservationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = BookingRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        print("inja1")
        restaurant = Restaurant.objects.get(id=data["restaurant_id"])
        user = request.user
        num_people = data["num_people"]
        reservation_time = data["reservation_time"]
        duration = data.get("duration_hours", 2)

        price_per_seat = getattr(settings, "PRICE_PER_SEAT", Decimal("10.00"))
        strategy = DefaultPricingStrategy(price_per_seat=price_per_seat)
        service = ReservationService(pricing_strategy=strategy)

        booking_req = BookingRequest(
            restaurant=restaurant,
            user=user,
            num_people=num_people,
            reservation_time=reservation_time,
            duration_hours=duration,
        )
        try:
            reservation = service.book(booking_req)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        output = ReservationSerializer(reservation)
        return Response(output.data, status=status.HTTP_201_CREATED)


class CancelReservationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CancelReservationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reservation = Reservation.objects.get(
            id=serializer.validated_data["reservation_id"]
        )

        service = ReservationService(
            pricing_strategy=DefaultPricingStrategy(Decimal("0"))
        )
        service.cancel(reservation)

        return Response({"detail": "Reservation cancelled."}, status=status.HTTP_200_OK)

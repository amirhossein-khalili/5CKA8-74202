from datetime import datetime
from typing import List

from reservations.models import Reservation


class ReservationRepo:
    """
    Repository for Reservation model .
    """

    @staticmethod
    def findByRestaurantAndInterval(
        restaurant_id: int,
        start_dt: datetime,
        end_dt: datetime,
    ) -> List[Reservation]:
        return list(
            Reservation.objects.filter(
                table__restaurant_id=restaurant_id,
                reservation_time__lt=end_dt,
                end_time__gt=start_dt,
            )
        )

    @staticmethod
    def createReservation(
        user,
        table,
        num_seats: int,
        cost,
        start_dt: datetime,
        end_dt: datetime,
    ) -> Reservation:
        reservation = Reservation(
            user=user,
            table=table,
            num_seats=num_seats,
            cost=cost,
            reservation_time=start_dt,
            end_time=end_dt,
        )
        reservation.save()
        return reservation

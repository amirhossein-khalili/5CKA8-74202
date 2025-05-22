from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone as dj_timezone

from restaurant.models import Table

class ReservationStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    CONFIRMED = "CONFIRMED", "Confirmed"
    CANCELLED = "CANCELLED", "Cancelled"


class Reservation(models.Model):
    """
    Represents a reservation made by a user for a specific table.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reservations"
    )
    table = models.ForeignKey(
        Table, on_delete=models.PROTECT, related_name="reservations"
    )
    num_seats = models.PositiveIntegerField(help_text="Number of seats reserved")
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=10,
        choices=ReservationStatus.choices,
        default=ReservationStatus.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    reservation_time = models.DateTimeField(help_text="Start time of the reservation")
    end_time = models.DateTimeField(help_text="End time of the reservation")

    class Meta:
        ordering = ["-reservation_time", "table"]

    def __str__(self) -> str:
        return (
            f"Reservation {self.id} by {self.user} for Table {self.table.number} "
            f"({self.status})"
        )

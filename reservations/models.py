from django.conf import settings
from django.db import models

from restaurant.models import Table


class ReservationStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    CONFIRMED = "CONFIRMED", "Confirmed"
    CANCELLED = "CANCELLED", "Cancelled"


class Reservation(models.Model):
    """
    Represents a reservation made by a user for a specific table.
    Status uses TextChoices for predefined statuses.
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

    class Meta:
        ordering = ["-reservation_time", "table"]

    def __str__(self):
        return f"Reservation {self.id} by {self.user} for Table {self.table.number} ({self.status})"

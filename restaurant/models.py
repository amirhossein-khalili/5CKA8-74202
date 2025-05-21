from datetime import datetime

from django.apps import apps
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Restaurant(models.Model):
    """
    Represents a restaurant, which can have multiple tables.
    Provides method to fetch available tables for a given time window.
    """

    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    def get_available_tables(self, start_time: datetime, end_time: datetime):
        """
        Returns a queryset of Tables without conflicting reservations in the given window.
        """
        return (
            self.tables.filter(
                reservations__reservation_time__gte=start_time,
                reservations__reservation_time__lt=end_time,
            )
            .distinct()
            .exclude(
                reservations__status=apps.get_model(
                    "reservations", "ReservationStatus"
                ).CANCELLED
            )
        )


class Table(models.Model):
    """
    Represents a table within a restaurant.
    Each table has a number and a fixed number of seats (4 to 10).
    Provides method to check availability for a given time window.
    """

    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name="tables"
    )
    number = models.PositiveIntegerField(help_text="Table number or identifier")
    seats = models.PositiveIntegerField(
        validators=[MinValueValidator(4), MaxValueValidator(10)],
        help_text="Number of seats at this table (min 4, max 10)",
    )

    class Meta:
        unique_together = ("restaurant", "number")
        ordering = ["restaurant", "number"]

    def __str__(self):
        return f"{self.restaurant.name} - Table {self.number} ({self.seats} seats)"

    def is_available(self, start_time: datetime, end_time: datetime) -> bool:
        """
        Returns True if no active (non-cancelled) reservations exist that overlap the window.
        """
        Reservation = apps.get_model("reservations", "Reservation")
        ReservationStatus = apps.get_model("reservations", "ReservationStatus")
        conflicts = Reservation.objects.filter(
            table=self, reservation_time__gte=start_time, reservation_time__lt=end_time
        ).exclude(status=ReservationStatus.CANCELLED)
        return not conflicts.exists()

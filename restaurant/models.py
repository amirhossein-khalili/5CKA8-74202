from datetime import datetime

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
        # from reservations.models import Reservation

        return self.tables.filter(is_available=True)


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
    is_available = models.BooleanField(
        default=True, help_text="Is the table available for booking?"
    )

    class Meta:
        unique_together = ("restaurant", "number")
        ordering = ["restaurant", "number"]

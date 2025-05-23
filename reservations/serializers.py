import datetime
from decimal import Decimal, InvalidOperation

from rest_framework import serializers

from reservations.models import Reservation
from restaurant.models import Restaurant


class CancelReservationSerializer(serializers.Serializer):
    reservation_id = serializers.IntegerField()

    def validate_reservation_id(self, value):
        if not Reservation.objects.filter(id=value).exists():
            raise serializers.ValidationError("Reservation does not exist.")
        return value


class ReservationRequestSerializer(serializers.Serializer):
    restaurant_id = serializers.IntegerField()
    reservation_date = serializers.DateField()
    reservation_time = serializers.TimeField()
    duration_hours = serializers.DecimalField(
        max_digits=2,
        decimal_places=1,
        min_value=Decimal("0.5"),
        max_value=Decimal("3.0"),
        default=Decimal("1"),
    )
    party_size = serializers.IntegerField(min_value=1)

    def validate_party_size(self, value: int) -> int:
        if value <= 0:
            raise serializers.ValidationError("party_size must be greater than zero.")
        return value

    def validate_duration_hours(self, value: Decimal) -> Decimal:
        """
        - Must not exceed 3.0 hours.
        - Must be at least 0.5 hours.
        - Must be in 0.5-hour increments.
        """
        try:
            half_hours = (value * 2).to_integral_value()
        except (InvalidOperation, AttributeError):
            raise serializers.ValidationError("Invalid duration_hours value.")

        if half_hours != value * 2:
            raise serializers.ValidationError(
                "duration_hours must be in 0.5-hour increments (e.g., 1.0, 1.5, 2.0)."
            )

        if value > Decimal("3.0"):
            raise serializers.ValidationError("duration_hours cannot exceed 3.0 hours.")
        if value < Decimal("0.5"):
            raise serializers.ValidationError(
                "duration_hours must be at least 0.5 hours."
            )

        return value

    def validate(self, attrs):
        """
        Check that the reservation date and time are not in the past.
        Assumes USE_TZ = False, so all datetimes are naive and local to the server.
        """
        reservation_date = attrs.get("reservation_date")
        reservation_time = attrs.get("reservation_time")

        if reservation_date and reservation_time:
            reservation_datetime = datetime.datetime.combine(
                reservation_date, reservation_time
            )
            now = datetime.datetime.now()

            if reservation_datetime <= now:
                raise serializers.ValidationError(
                    "Reservation date and time cannot be in the past or exactly now. Please choose a future time."
                )

        return attrs

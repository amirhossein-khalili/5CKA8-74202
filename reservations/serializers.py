from decimal import Decimal, InvalidOperation

from rest_framework import serializers

from reservations.models import Reservation
from restaurant.models import Restaurant


class BookingRequestSerializer(serializers.Serializer):
    restaurant_id = serializers.IntegerField()
    num_people = serializers.IntegerField(min_value=1)
    reservation_time = serializers.DateTimeField()
    duration_hours = serializers.IntegerField(required=False, default=2, min_value=1)

    def validate_restaurant_id(self, value):
        if not Restaurant.objects.filter(id=value).exists():
            raise serializers.ValidationError("Restaurant does not exist.")
        return value


class CancelReservationSerializer(serializers.Serializer):
    reservation_id = serializers.IntegerField()

    def validate_reservation_id(self, value):
        if not Reservation.objects.filter(id=value).exists():
            raise serializers.ValidationError("Reservation does not exist.")
        return value


class ReservationSerializer(serializers.ModelSerializer):
    table_number = serializers.IntegerField(source="table.number")
    restaurant = serializers.CharField(source="table.restaurant.name")

    class Meta:
        model = Reservation
        fields = [
            "id",
            "restaurant",
            "table_number",
            "num_seats",
            "cost",
            "status",
            "reservation_time",
        ]


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
        # Ensure it's a multiple of 0.5
        try:
            half_hours = (value * 2).to_integral_value()
        except (InvalidOperation, AttributeError):
            raise serializers.ValidationError("Invalid duration_hours value.")

        if half_hours != value * 2:
            raise serializers.ValidationError(
                "duration_hours must be in 0.5-hour increments (e.g., 1.0, 1.5, 2.0)."
            )

        # Bound checks are already enforced by DecimalField’s min_value/max_value,
        # but you can add extra guard if desired:
        if value > Decimal("3.0"):
            raise serializers.ValidationError("duration_hours cannot exceed 3.0 hours.")
        if value < Decimal("0.5"):
            raise serializers.ValidationError(
                "duration_hours must be at least 0.5 hours."
            )

        return value

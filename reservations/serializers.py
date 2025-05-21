from datetime import datetime

from rest_framework import serializers

from reservations.models import Reservation
from restaurant.models import Restaurant, Table


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

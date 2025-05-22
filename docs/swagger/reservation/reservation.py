# docs/swagger_schemas.py
from drf_yasg import openapi

from reservations.serializers import ReservationRequestSerializer

# Re-use your serializer as the request body
BookReservationRequest = ReservationRequestSerializer

# Build the response schema here
BookReservationResponse = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "detail": openapi.Schema(type=openapi.TYPE_STRING),
        "restaurant": openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                "name": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        "payload": openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "restaurant_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                "reservation_date": openapi.Schema(
                    type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
                ),
                "reservation_time": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format="time",
                ),
                "duration_hours": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Hours (0.5–3.0, in 0.5 increments)",
                ),
                "party_size": openapi.Schema(type=openapi.TYPE_INTEGER),
            },
        ),
    },
    required=["detail", "restaurant", "payload"],
)

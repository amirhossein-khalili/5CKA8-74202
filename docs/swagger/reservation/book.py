from drf_yasg import openapi
from rest_framework import status

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
                    type=openapi.TYPE_NUMBER,
                    description="Hours (0.5–3.0, in 0.5 increments)",
                ),
                "party_size": openapi.Schema(type=openapi.TYPE_INTEGER),
            },
        ),
    },
    required=["detail", "restaurant", "payload"],
)


BOOK_RESERVATION_VIEW_SCHEMA = {
    "operation_id": "book_reservation",
    "operation_summary": "Book a reservation",
    "operation_description": (
        "Allows an authenticated user to book a table at a restaurant. "
        "Provide restaurant ID, date, time, party size, and duration."
    ),
    "request_body": openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "restaurant_id": openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description="ID of the restaurant for the reservation.",
                example=1,
            ),
            "reservation_date": openapi.Schema(
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                description="Desired date for the reservation (YYYY-MM-DD).",
                example="2025-06-26",
            ),
            "reservation_time": openapi.Schema(
                type=openapi.TYPE_STRING,
                format="time",
                description="Desired time for the reservation (HH:MM in 24-hour format).",
                example="19:30",
            ),
            "party_size": openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description="Number of guests for the reservation.",
                example=1,
            ),
            "duration_hours": openapi.Schema(
                type=openapi.TYPE_NUMBER,
                description="Duration of the reservation in hours (e.g., 1, 1.5, 2.0).",
                example=2,
            ),
        },
        required=[
            "restaurant_id",
            "reservation_date",
            "reservation_time",
            "party_size",
            "duration_hours",
        ],
        examples={
            "application/json": {
                "restaurant_id": 1,
                "reservation_date": "2025-06-26",
                "reservation_time": "19:30",
                "party_size": 1,
                "duration_hours": 2.0,
            }
        },
    ),
    "responses": {
        status.HTTP_200_OK: openapi.Response(
            description="Reservation booked successfully or processed. See details in response.",
            schema=BookReservationResponse,  # Referencing the schema defined above
        ),
        status.HTTP_400_BAD_REQUEST: openapi.Response(
            description="Bad Request - Invalid input data or validation error.",
            examples={
                "application/json": {"field_name": ["Error message for this field."]}
            },
        ),
        status.HTTP_401_UNAUTHORIZED: openapi.Response(
            description="Unauthorized - Authentication credentials were not provided or are invalid.",
            examples={
                "application/json": {
                    "detail": "Authentication credentials were not provided."
                }
            },
        ),
        status.HTTP_404_NOT_FOUND: openapi.Response(
            description="Not Found - The specified restaurant or a suitable table could not be found.",
            examples={"application/json": {"detail": "Restaurant not found."}},
        ),
    },
    "tags": ["Reservations"],
}

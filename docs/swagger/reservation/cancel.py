from drf_yasg import openapi
from rest_framework import status

from reservations.serializers import CancelReservationSerializer

CANCEL_RESERVATION_VIEW_SCHEMA = {
    "operation_summary": "Cancel a reservation",
    "request_body": CancelReservationSerializer,
    "responses": {
        status.HTTP_200_OK: openapi.Response(
            description="Reservation cancelled successfully or status update (e.g., already cancelled)",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "detail": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Cancellation status message.",
                    )
                },
                required=["detail"],
                examples={
                    "application/json": {
                        "detail": "Your reservation has been successfully cancelled."
                    }
                },
            ),
        ),
        status.HTTP_400_BAD_REQUEST: openapi.Response(
            description="Bad request (e.g., invalid reservation ID format, or other validation error from serializer)",
            examples={
                "application/json": {"reservation_id": ["This field is required."]}
            },
        ),
        status.HTTP_401_UNAUTHORIZED: openapi.Response(
            description="Unauthorized (user not authenticated)",
            examples={
                "application/json": {
                    "detail": "Authentication credentials were not provided."
                }
            },
        ),
        status.HTTP_403_FORBIDDEN: openapi.Response(
            description="Forbidden (user does not own the reservation or cancellation not allowed by policy)",
            examples={
                "application/json": {
                    "detail": "You do not have permission to cancel this reservation."
                }
            },
        ),
        status.HTTP_404_NOT_FOUND: openapi.Response(
            description="Reservation not found",
            examples={"application/json": {"detail": "Reservation not found."}},
        ),
    },
    "tags": ["Reservations"],
}

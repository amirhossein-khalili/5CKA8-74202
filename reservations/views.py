from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from docs.swagger.reservation.reservation import (
    BookReservationRequest,
    BookReservationResponse,
)
from reservations.services.facade import ReservationFacadeService

_facade = ReservationFacadeService()


class BookReservationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Book a reservation",
        request_body=BookReservationRequest,
        responses={
            200: openapi.Response("Reservation booked", schema=BookReservationResponse),
            400: "Bad request",
            401: "Unauthorized",
            404: "Restaurant or table not found",
        },
    )
    def post(self, request, *args, **kwargs):
        result = _facade.book(request.data, request.user, context={"request": request})
        return Response(result, status=status.HTTP_200_OK)


# class CancelReservationView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request):
#         serializer = CancelReservationSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         reservation = Reservation.objects.get(
#             id=serializer.validated_data["reservation_id"]
#         )

#         service = ReservationService(
#             # pricing_strategy=DefaultPricingStrategy(Decimal("0"))
#         )
#         service.cancel(reservation)

#         return Response({"detail": "Reservation cancelled."}, status=status.HTTP_200_OK)

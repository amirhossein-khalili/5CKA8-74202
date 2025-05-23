from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from docs.swagger.reservation.book import BOOK_RESERVATION_VIEW_SCHEMA
from docs.swagger.reservation.cancel import CANCEL_RESERVATION_VIEW_SCHEMA
from reservations.models import Reservation
from reservations.serializers import CancelReservationSerializer
from reservations.services.facade import ReservationFacadeService

_facade = ReservationFacadeService()


class BookReservationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(**BOOK_RESERVATION_VIEW_SCHEMA)
    def post(self, request, *args, **kwargs):
        result = _facade.book(request.data, request.user, context={"request": request})
        return Response(result, status=status.HTTP_200_OK)


class CancelReservationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(**CANCEL_RESERVATION_VIEW_SCHEMA)
    def post(self, request, *args, **kwargs):
        serializer = CancelReservationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reservation_id = serializer.validated_data["reservation_id"]

        try:
            message = _facade.cancel_reservation(
                reservation_id=reservation_id, user=request.user
            )
            return Response({"detail": message}, status=status.HTTP_200_OK)
        except Reservation.DoesNotExist:

            raise NotFound(detail="Reservation not found.")
        except PermissionDenied as e:
            raise PermissionDenied(detail=str(e))

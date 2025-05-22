from rest_framework import permissions, status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from reservations.repos.repository import ReservationRepo
from reservations.serializers import ReservationRequestSerializer
from restaurant.repos.repository import RestaurantRepo
from restaurant.services.price_policy import DefaultPricingPolicy
from restaurant.services.table_selection import DefaultTableSelectionStrategy
from utils.build_reservation_datetimes import build_reservation_datetimes


class BookReservationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):

        ### ------> serilize and validate data
        serializer = ReservationRequestSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data

        ### ------> check resturaunt and its existence
        try:
            restaurant = RestaurantRepo.findById(payload["restaurant_id"])
            if restaurant is None:
                raise NotFound("Restaurant not found.")
        except NotFound as e:
            raise e

        ### ------> converting time
        start_dt, end_dt = build_reservation_datetimes(
            request.data["reservation_date"],
            request.data["reservation_time"],
            float(request.data["duration_hours"]),
        )

        selection = DefaultTableSelectionStrategy(repo=ReservationRepo())
        pricing = DefaultPricingPolicy(seat_price=10)

        table = selection.find_by_restaurant_and_time(
            payload["restaurant_id"], start_dt, end_dt, payload["party_size"]
        )
        if not table:
            raise NotFound("Table not found.")

        cost = pricing.calculate(table, payload["party_size"])
        res = ReservationRepo.createReservation(
            request.user, table, payload["party_size"], cost, start_dt, end_dt
        )

        return Response(
            {
                "detail": "res",
                "restaurant": {
                    "id": restaurant.id,
                    "name": restaurant.name,
                },
                "payload": payload,
            },
            status=status.HTTP_200_OK,
        )


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

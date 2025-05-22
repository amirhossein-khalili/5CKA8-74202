from rest_framework.exceptions import NotFound

from reservations.repos.repository import ReservationRepo
from reservations.serializers import ReservationRequestSerializer
from restaurant.repos.repository import RestaurantRepo
from restaurant.services.price_policy import DefaultPricingPolicy
from restaurant.services.table_selection import DefaultTableSelectionStrategy
from utils.build_reservation_datetimes import build_reservation_datetimes


class ReservationFacadeService:
    """
    High-level API to handle reservation booking end-to-end.
    """

    serializer_class = ReservationRequestSerializer

    def __init__(
        self,
        reservation_repo=None,
        restaurant_repo=None,
        table_selector=None,
        pricing_policy=None,
    ):
        self.res_repo = reservation_repo or ReservationRepo()
        self.rest_repo = restaurant_repo or RestaurantRepo()
        self.table_selector = table_selector or DefaultTableSelectionStrategy(
            repo=self.res_repo
        )
        self.pricing = pricing_policy or DefaultPricingPolicy(seat_price=10)

    def book(self, data, user, context=None):
        # 1) validate input
        serializer = self.serializer_class(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data

        # 2) find restaurant
        restaurant = self.rest_repo.findById(payload["restaurant_id"])
        if not restaurant:
            raise NotFound("Restaurant not found.")

        # 3) compute start/end datetimes
        start_dt, end_dt = build_reservation_datetimes(
            data["reservation_date"],
            data["reservation_time"],
            float(data["duration_hours"]),
        )

        # 4) pick a table
        table = self.table_selector.find_by_restaurant_and_time(
            payload["restaurant_id"],
            start_dt,
            end_dt,
            payload["party_size"],
        )
        if not table:
            raise NotFound("Table not found.")

        # 5) compute cost and persist
        cost = self.pricing.calculate(table, payload["party_size"])
        reservation = self.res_repo.createReservation(
            user, table, payload["party_size"], cost, start_dt, end_dt
        )

        # 6) return whatever your view wants to show
        return {
            "detail": f"you reserved table {reservation.table.id} successfully.",
            "restaurant": {"id": restaurant.id, "name": restaurant.name},
        }

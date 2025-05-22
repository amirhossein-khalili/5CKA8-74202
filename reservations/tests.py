from datetime import date, datetime, time, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from reservations.models import Reservation
from reservations.repos.repository import ReservationRepo
from reservations.serializers import ReservationRequestSerializer
from reservations.views import BookReservationView
from restaurant.models import Restaurant, Table
from restaurant.services.price_policy import DefaultPricingPolicy

User = get_user_model()


class ReservationRequestSerializerTests(TestCase):
    def test_valid_data_passes(self):
        data = {
            "restaurant_id": 1,
            "reservation_date": date.today().isoformat(),
            "reservation_time": time(12, 30).isoformat(),
            "duration_hours": "1.5",
            "party_size": 2,
        }
        serializer = ReservationRequestSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_party_size_must_be_positive(self):
        data = {
            "restaurant_id": 1,
            "reservation_date": date.today().isoformat(),
            "reservation_time": time(12).isoformat(),
            "duration_hours": "1.0",
            "party_size": 0,
        }
        serializer = ReservationRequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("party_size", serializer.errors)
        # uses min_value=1
        self.assertIn("greater than or equal to 1", serializer.errors["party_size"][0])

    def test_duration_must_be_half_hour_steps(self):
        data = {
            "restaurant_id": 1,
            "reservation_date": date.today().isoformat(),
            "reservation_time": time(12).isoformat(),
            "duration_hours": "1.3",
            "party_size": 2,
        }
        serializer = ReservationRequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("duration_hours", serializer.errors)
        self.assertIn("0.5-hour increments", str(serializer.errors["duration_hours"]))

    def test_duration_cannot_exceed_max(self):
        data = {
            "restaurant_id": 1,
            "reservation_date": date.today().isoformat(),
            "reservation_time": time(12).isoformat(),
            "duration_hours": "4.0",
            "party_size": 2,
        }
        serializer = ReservationRequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("duration_hours", serializer.errors)


class ReservationRepoTests(TestCase):
    def setUp(self):
        # user, restaurant, and one table
        self.user = User.objects.create_user(username="u", password="p")
        self.rest = Restaurant.objects.create(name="Resto")
        self.table = Table.objects.create(restaurant=self.rest, seats=4, number=101)

        # reference window
        self.start = datetime.now()
        self.end = self.start + timedelta(hours=2)

        # reservation fully before window
        Reservation.objects.create(
            user=self.user,
            table=self.table,
            num_seats=2,
            cost=20,
            reservation_time=self.start - timedelta(hours=3),
            end_time=self.start - timedelta(hours=1),
        )

        # reservation overlapping window ⇒ should be returned
        self.overlap = Reservation.objects.create(
            user=self.user,
            table=self.table,
            num_seats=2,
            cost=20,
            reservation_time=self.start + timedelta(hours=0.5),
            end_time=self.start + timedelta(hours=1.5),
        )

        # reservation fully after window
        Reservation.objects.create(
            user=self.user,
            table=self.table,
            num_seats=2,
            cost=20,
            reservation_time=self.end + timedelta(hours=1),
            end_time=self.end + timedelta(hours=2),
        )

    def test_find_by_interval_only_overlaps(self):
        results = ReservationRepo.findByRestaurantAndInterval(
            self.rest.id, self.start, self.end
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], self.overlap)


class BookReservationViewTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(username="alice", password="pw")
        # one restaurant and two tables
        self.rest = Restaurant.objects.create(name="Testaurant")
        self.t2 = Table.objects.create(restaurant=self.rest, seats=2, number=1)
        self.t4 = Table.objects.create(restaurant=self.rest, seats=4, number=2)

        self.view = BookReservationView.as_view()
        self.url = "/book/"  # purely informative for factory

        # choose tomorrow at 18:00
        tomorrow = date.today() + timedelta(days=1)
        self.payload = {
            "restaurant_id": self.rest.id,
            "reservation_date": tomorrow.isoformat(),
            "reservation_time": "18:00",
            "duration_hours": "2",  # required by view’s builder
            "party_size": 2,
        }

    def _call(self, data, user=None):
        req = self.factory.post(self.url, data, format="json")
        if user:
            force_authenticate(req, user=user)
        return self.view(req)

    def test_success_creates_reservation(self):
        resp = self._call(self.payload, user=self.user)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # one reservation in DB
        self.assertEqual(Reservation.objects.count(), 1)
        res = Reservation.objects.first()

        # correct linkage
        self.assertEqual(res.user, self.user)
        self.assertEqual(res.table.restaurant, self.rest)
        self.assertEqual(res.num_seats, 2)

        # pricing: seat_price=10, party=2 ⇒ 2 * 10
        expected = DefaultPricingPolicy(seat_price=10).calculate(res.table, 2)
        self.assertEqual(res.cost, expected)

        # check response body
        body = resp.data
        self.assertEqual(body["restaurant"]["id"], self.rest.id)
        self.assertEqual(body["restaurant"]["name"], self.rest.name)

    def test_invalid_restaurant_gives_404(self):
        bad = self.payload.copy()
        bad["restaurant_id"] = 9999
        resp = self._call(bad, user=self.user)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(resp.data.get("detail"), "Restaurant not found.")

    def test_no_table_available_gives_404(self):
        # make a new restaurant with no tables
        empty_rest = Restaurant.objects.create(name="Empty")
        bad = self.payload.copy()
        bad["restaurant_id"] = empty_rest.id
        resp = self._call(bad, user=self.user)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(resp.data.get("detail"), "Table not found.")

    def test_unauthenticated_gets_401(self):
        resp = self._call(self.payload, user=None)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_bad_payload_returns_400(self):
        bad = self.payload.copy()
        bad.pop("party_size")
        resp = self._call(bad, user=self.user)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("party_size", resp.data)

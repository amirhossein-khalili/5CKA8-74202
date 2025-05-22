from django.test import TestCase

from restaurant.models import Restaurant, Table
from restaurant.repos.repository import RestaurantRepo
from restaurant.services.price_policy import DefaultPricingPolicy
from restaurant.services.table_selection import DefaultTableSelectionStrategy


class RestaurantRepoTests(TestCase):
    def test_find_by_id_returns_instance(self):
        # Adjust 'name' field if your Restaurant model differs
        restaurant = Restaurant.objects.create(name="Chez Django")
        found = RestaurantRepo.findById(restaurant.id)
        self.assertIsNotNone(found)
        self.assertEqual(found.pk, restaurant.pk)
        self.assertEqual(found.name, "Chez Django")

    def test_find_by_id_nonexistent_returns_none(self):
        # Pick an ID that (almost certainly) doesn't exist
        self.assertIsNone(RestaurantRepo.findById(9999))


class DefaultPricingPolicyTests(TestCase):
    def setUp(self):
        self.seat_price = 10.0
        self.policy = DefaultPricingPolicy(seat_price=self.seat_price)

        # We'll use a simple dummy with a 'seats' attribute
        class DummyTable:
            def __init__(self, seats):
                self.seats = seats

        self.Table = DummyTable

    def test_charge_per_person_when_party_smaller_than_table(self):
        table = self.Table(seats=6)
        price = self.policy.calculate(table, party_size=4)
        self.assertEqual(price, 4 * self.seat_price)

    def test_charge_full_table_minus_one_when_party_fills_table(self):
        table = self.Table(seats=4)
        price = self.policy.calculate(table, party_size=4)
        # billing_units = 4 - 1 = 3
        self.assertEqual(price, 3 * self.seat_price)

    def test_charge_full_table_minus_one_when_party_exceeds_capacity(self):
        table = self.Table(seats=5)
        price = self.policy.calculate(table, party_size=10)
        # party_size >= table.seats → billing_units = seats - 1
        self.assertEqual(price, (5 - 1) * self.seat_price)


class DefaultTableSelectionStrategyTests(TestCase):

    def setUp(self):
        self.restaurant = Restaurant.objects.create(name="Testaurant")
        self.t2 = Table.objects.create(restaurant=self.restaurant, seats=2, number=1)
        self.t3 = Table.objects.create(restaurant=self.restaurant, seats=3, number=2)
        self.t4 = Table.objects.create(restaurant=self.restaurant, seats=4, number=3)
        self.t6 = Table.objects.create(restaurant=self.restaurant, seats=6, number=4)

        from datetime import datetime, timedelta

        self.start = datetime.now()
        self.end = self.start + timedelta(hours=2)

    class _FakeRepo:
        """
        A fake ReservationRepo that can be told which table_ids are currently occupied.
        """

        def __init__(self, occupied_ids):
            self.occupied_ids = set(occupied_ids)

        def findByRestaurantAndInterval(self, restaurant_id, start_dt, end_dt):
            # Return objects with a .table_id attribute
            return [type("R", (), {"table_id": tid})() for tid in self.occupied_ids]

    def test_selects_smallest_table_without_odd_padding(self):
        """
        party_size=2 → required=2, picks t2
        """
        svc = DefaultTableSelectionStrategy(repo=self._FakeRepo([]))
        chosen = svc.find_by_restaurant_and_time(
            self.restaurant.id, self.start, self.end, party_size=2
        )
        self.assertEqual(chosen, self.t2)

    def test_rounds_odd_up_unless_exact_match(self):
        """
        party_size=3
         - there is an exact t3, so pick t3 (no rounding)
        """
        svc = DefaultTableSelectionStrategy(repo=self._FakeRepo([]))
        chosen = svc.find_by_restaurant_and_time(
            self.restaurant.id, self.start, self.end, party_size=3
        )
        self.assertEqual(chosen, self.t3)

    def test_rounds_odd_up_when_no_exact_odd_table(self):
        """
        Remove the t3 table to force rounding:
         party_size=3 → required=4 → picks t4
        """
        # delete the exact-3-seater
        self.t3.delete()

        svc = DefaultTableSelectionStrategy(repo=self._FakeRepo([]))
        chosen = svc.find_by_restaurant_and_time(
            self.restaurant.id, self.start, self.end, party_size=3
        )
        self.assertEqual(chosen.seats, 4)

    # NOTE : check this test
    def test_ignores_occupied_tables(self):
        """
        If the 2-seater is occupied, party_size=2 → next smallest is t4
        """
        svc = DefaultTableSelectionStrategy(repo=self._FakeRepo([self.t2.id]))
        chosen = svc.find_by_restaurant_and_time(
            self.restaurant.id, self.start, self.end, party_size=2
        )
        self.assertEqual(chosen, self.t4)

    def test_returns_none_when_no_table_available(self):
        """
        Occupy all tables → no table can be found
        """
        all_ids = [self.t2.id, self.t3.id, self.t4.id, self.t6.id]
        svc = DefaultTableSelectionStrategy(repo=self._FakeRepo(all_ids))
        chosen = svc.find_by_restaurant_and_time(
            self.restaurant.id, self.start, self.end, party_size=2
        )
        self.assertIsNone(chosen)

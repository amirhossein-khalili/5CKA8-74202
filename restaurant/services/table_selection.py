from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from reservations.repos.repository import ReservationRepo
from restaurant.models import Table


class TableSelectionStrategy(ABC):
    """
    Strategy interface for selecting a table given a restaurant and time slot.
    """

    @abstractmethod
    def find_by_restaurant_and_time(
        self,
        restaurant_id: int,
        start_dt: datetime,
        end_dt: datetime,
        party_size: int,
    ) -> Optional[Table]:
        """
        Return a suitable Table or None if no table is available.
        """
        pass


class DefaultTableSelectionStrategy(TableSelectionStrategy):
    """
    Selects the smallest table that can accommodate the party,
    applying RULE1: no odd seats unless party_size equals table capacity.
    """

    def __init__(self, repo: ReservationRepo):
        self.repo = repo

    def find_by_restaurant_and_time(
        self,
        restaurant_id: int,
        start_dt: datetime,
        end_dt: datetime,
        party_size: int,
    ) -> Optional[Table]:
        # fetch all tables in restaurant
        all_tables = Table.objects.filter(restaurant_id=restaurant_id)
        # fetch occupied tables in interval
        occupied = self.repo.findByRestaurantAndInterval(
            restaurant_id, start_dt, end_dt
        )
        occupied_ids = {r.table_id for r in occupied}

        # candidates are free tables
        candidates = [t for t in all_tables if t.id not in occupied_ids]

        # apply RULE1: adjust required seats
        required = party_size
        # if odd and not equal to any table size exactly, round up to next even
        if party_size % 2 == 1:
            # see if any table has exact odd capacity == party_size
            if not any(t.seats == party_size for t in candidates):
                required += 1

        # pick smallest table with capacity >= required
        suitable = [t for t in candidates if t.seats >= required]
        if not suitable:
            return None

        return min(suitable, key=lambda t: t.seats)

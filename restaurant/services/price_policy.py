from abc import ABC, abstractmethod

from restaurant.models import Table


class PricingPolicy(ABC):
    """
    Interface to calculate cost for a given table and party size.
    """

    @abstractmethod
    def calculate(self, table: Table, party_size: int) -> float:
        """
        Return the total price for booking.
        """
        pass


class DefaultPricingPolicy(PricingPolicy):
    """
    Implements RULE2: each seat costs `seat_price`,
    but booking entire table costs (table.seats - 1) * seat_price.
    """

    def __init__(self, seat_price: float):
        self.seat_price = seat_price

    def calculate(self, table: Table, party_size: int) -> float:
        return (int(table.seats) - 1) * self.seat_price

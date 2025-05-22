from typing import Optional

from django.db import models

from restaurant.models import Restaurant


class RestaurantRepo:
    """
    Repository for Restaurant model.
    """

    @staticmethod
    def findById(restaurant_id: int) -> Optional[Restaurant]:
        """
        Retrieve a Restaurant by its primary key.

        Args:
            restaurant_id: The ID of the restaurant to retrieve.

        Returns:
            The Restaurant instance if found, otherwise None.
        """
        try:
            return Restaurant.objects.get(pk=restaurant_id)
        except Restaurant.DoesNotExist:
            return None

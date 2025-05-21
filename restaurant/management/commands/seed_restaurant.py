from django.core.management.base import BaseCommand

from restaurant.models import Restaurant, Table


class Command(BaseCommand):
    help = "Seeds the database with one restaurant and 10 tables."

    def handle(self, *args, **options):
        restaurant, created = Restaurant.objects.get_or_create(
            name="Example Restaurant"
        )

        for i in range(1, 11):
            Table.objects.get_or_create(
                restaurant=restaurant,
                number=i,
                seats=4 + (i % 7),  # Distributes seat count between 4 and 10
            )

        self.stdout.write(
            self.style.SUCCESS("Successfully seeded restaurant and tables.")
        )

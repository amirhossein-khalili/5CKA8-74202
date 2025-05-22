# your_app_name/admin.py

from django.contrib import admin

from .models import Restaurant, Table


class TableInline(admin.TabularInline):  # Or admin.StackedInline for a different layout
    """
    Allows editing Tables directly within the Restaurant admin page.
    """

    model = Table
    extra = 1  # Number of empty forms to display for adding new tables
    fields = ("number", "seats", "is_available")
    # You can customize readonly_fields, etc. if needed


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Restaurant model.
    """

    list_display = ("name", "get_table_count")
    search_fields = ("name",)
    inlines = [TableInline]

    def get_table_count(self, obj):
        """
        Custom method to display the number of tables for a restaurant.
        """
        return obj.tables.count()

    get_table_count.short_description = "Number of Tables"


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Table model.
    """

    list_display = ("restaurant", "number", "seats", "is_available")
    list_filter = ("restaurant", "is_available", "seats")
    search_fields = ("restaurant__name", "number")
    list_editable = ("is_available", "seats")
    ordering = ("restaurant", "number")

    fieldsets = (
        (None, {"fields": ("restaurant", "number", "seats")}),
        (
            "Availability",
            {
                "fields": ("is_available",),
            },
        ),
    )

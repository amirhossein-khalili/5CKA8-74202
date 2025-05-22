from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Restuarant Reservation",
        default_version="v1",
        description="API documentation for Restuarant Reservation",
        # terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="amir1378khalili@gmail.com"),
        # license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

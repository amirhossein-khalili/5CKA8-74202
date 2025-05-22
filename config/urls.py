from django.contrib import admin
from django.urls import include, path, re_path

from docs.swagger.swagger_config import schema_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/accounts/", include("accounts.urls", namespace="accounts")),
    path("api/reservations/", include("reservations.urls", namespace="reservations")),
    # Swagger UI
    re_path(
        r"^swagger/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
]

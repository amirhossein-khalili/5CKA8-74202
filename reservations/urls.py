from django.urls import path

from reservations.views import BookReservationView, CancelReservationView

app_name = "reservations"
urlpatterns = [
    path("book/", BookReservationView.as_view(), name="book_reservation"),
    path("cancel/", CancelReservationView.as_view(), name="cancel_reservation"),
]

from rest_framework import routers
from django.urls import path

from .views import HotelView, RoomView, ReservationView, AvailableRoom, DownloadBookedRoomsView

router = routers.DefaultRouter()
router.register(r'hotel', HotelView)
router.register(r'reservation', ReservationView)

urlpatterns = router.urls + [
    path(
        'hotel/<hotel_id>/room/',
        RoomView.as_view({'get': 'list', 'post': 'create'})
    ),
    path(
        'hotel/<hotel_id>/room/<pk>/',
        RoomView.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'})
    ),
    path(
        'available_rooms/',
        AvailableRoom.as_view()
    ),
    path(
        'booked_rooms/',
        DownloadBookedRoomsView.as_view()
    )
]
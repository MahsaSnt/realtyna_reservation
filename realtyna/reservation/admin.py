from django.contrib import admin

from .models import Hotel, Room, Reservation

admin.site.register((Hotel, Room, Reservation,))

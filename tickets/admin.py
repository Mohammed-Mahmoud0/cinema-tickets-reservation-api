from django.contrib import admin
from .models import Guest, Movie, Reservation

admin.site.register(Guest)
admin.site.register(Movie)
admin.site.register(Reservation)
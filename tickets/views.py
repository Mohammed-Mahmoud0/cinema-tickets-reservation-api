from django.http import JsonResponse
from django.shortcuts import render
from .models import Guest, Movie, Reservation
from rest_framework.decorators import api_view
from .serializers import GuestSerializer, MovieSerializer, ReservationSerializer
from rest_framework import status, filters
from rest_framework.response import Response

# Create your views here.


# 1 without REST and no models query FBV
def no_rest_no_model(request):
    guest = [
        {"id": 1, "name": "John", "mobile": "1234567890"},
        {"id": 2, "name": "Doe", "mobile": "0987654321"},
    ]
    return JsonResponse(guest, safe=False)


# 2 model data default django without rest
def no_rest_from_model(request):
    data = Guest.objects.all()
    response = {"guests": list(data.values("name", "mobile"))}
    return JsonResponse(response)

# List == GET
# Create == POST
# PK query == GET
# Update == PUT
# Delete == DELETE

# 3 function based views
# 3.1 GET POST
@api_view(["GET", "POST"])
def FBV_List(request):
  # GET
  if request.method == "GET":
    guests = Guest.objects.all()
    serializer = GuestSerializer(guests, many=True)
    return Response(serializer.data)
  # POST
  elif request.method == "POST":
    serializer = GuestSerializer(data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

# 3.1 GET UPDATE DELETE
# @api_view()
# def
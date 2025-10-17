from django.http import JsonResponse
from django.shortcuts import render
from .models import Guest, Movie, Reservation
from rest_framework.decorators import api_view
from .serializers import GuestSerializer, MovieSerializer, ReservationSerializer
from rest_framework import status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import Http404

# Create your views here.


# 1 without REST and no models query FBV
def no_rest_no_model(request):
    guest = [
        {"id": 1, "name": "John", "mobile": "1234567890"},
        {"id": 2, "name": "Doe", "mobile": "0987654321"},
        {"id": 3, "name": "moh", "mobile": "151588"},
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
@api_view(["GET", "PUT", "DELETE"])
def FBV_PK(request, pk):
    try:
        guest = Guest.objects.get(pk=pk)
    except Guest.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    # GET
    if request.method == "GET":
        serializer = GuestSerializer(guest)
        return Response(serializer.data)
    # Put
    elif request.method == "PUT":
        serializer = GuestSerializer(guest, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    # DELETE
    if request.method == "DELETE":
        guest.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# CBV class based views
# 4.1 list and create == GET and POST
class CBV_List(APIView):
    def get(self, request):
        guests = Guest.objects.all()
        serializer = GuestSerializer(guests, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = GuestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 4.2 put update delete class based view  pk
class CBV_PK(APIView):
    def get_object(self, pk):
        try:
            return Guest.objects.get(pk=pk)
        except:
            raise Http404

    def get(self, request, pk):
        guest = self.get_object(pk)
        serializer = GuestSerializer(guest)
        return Response(serializer.data)

    def put(self, request, pk):
        guest = self.get_object(pk)
        serializer = GuestSerializer(guest, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        guest = self.get_object(pk)
        guest.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

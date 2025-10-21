from django.http import JsonResponse
from django.shortcuts import render
from .models import Guest, Movie, Reservation
from rest_framework.decorators import api_view
from .serializers import GuestSerializer, MovieSerializer, ReservationSerializer
from rest_framework import status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import Http404
from rest_framework import generics, mixins, viewsets
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated


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


# 5 mixins list
class mixins_list(
    mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView
):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer

    def get(self, request):
        return self.list(request)

    def post(self, request):
        return self.create(request)


class mixins_pk(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView,
):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer

    def get(self, request, pk):
        return self.retrieve(request)

    def put(self, request, pk):
        return self.update(request)

    def delete(self, request, pk):
        return self.destroy(request)


# 6 generics
# 6.1 get and post
class generics_list(generics.ListCreateAPIView):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]


# 6.2 get put delete
class generics_pk(generics.RetrieveUpdateDestroyAPIView):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]


# 7 viewsets


class viewsets_guest(viewsets.ModelViewSet):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer


class viewsets_movie(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["movie"]


class viewsets_reservation(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer


# 8 find movie (here we can use any customization of endpoints we need using fbv i think we can use cbv also)
@api_view(["GET"])
def find_movie(request):
    movies = Movie.objects.filter(
        hall=request.data["hall"],
        movie=request.data["movie"],
    )
    serializer = MovieSerializer(movies, many=True)
    return Response(serializer.data)


# 9 create new reservation
@api_view(["POST"])
def new_reservation(request):
    movie = Movie.objects.get(hall=request.data["hall"], movie=request.data["movie"])

    guest = Guest()
    guest.name = request.data["name"]
    guest.mobile = request.data["mobile"]
    guest.save()

    reservation = Reservation()
    reservation.guest = guest
    reservation.movie = movie
    reservation.save()

    return Response(status=status.HTTP_201_CREATED)

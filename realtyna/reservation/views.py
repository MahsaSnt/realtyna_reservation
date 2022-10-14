from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, filters, generics
from rest_framework.response import Response
from django.http import FileResponse
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend

from .models import Hotel, Room, Reservation
from .serializers import(
    HotelSerializer,
    RoomSerializer,
    GetReservationSerializer,
    CreateReservationSerializer,
    GetRoomSerializer,
    AvailableRoomSerializer,
    BookedRoomsSerializer,
)


class HotelView(viewsets.ModelViewSet):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    filter_backends = (
        filters.SearchFilter,
        filters.OrderingFilter,
    )
    search_fields = ('title', )
    ordering_fields = ('title',)


class RoomView(viewsets.ModelViewSet):
    serializer_class = RoomSerializer
    filter_backends = (
        filters.OrderingFilter,
        DjangoFilterBackend,
    )
    ordering_fields = ('floor', 'cost',)
    filterset_fields = ('floor',)

    def get_queryset(self):
        hotel_id = self.request.parser_context['kwargs'].get('hotel_id')
        return Room.objects.filter(hotel_id=hotel_id)

    def create(self, request, *args, **kwargs):
        hotel_id = request.parser_context['kwargs'].get('hotel_id')
        get_object_or_404(Hotel, id=hotel_id)
        return super().create(request, *args, **kwargs)


class ReservationView(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = GetReservationSerializer
    http_method_names = (
        'get',
        'post',
    )
    filter_backends = (
        filters.OrderingFilter,
        filters.SearchFilter,
        DjangoFilterBackend,
    )
    search_fields = ('room__hotel__title', 'customer',)
    ordering_fields = ('start_date', 'end_date','room_id', 'room__hotel_id',)
    filterset_fields = ('room_id', 'room__hotel_id', 'customer',)

    def create(self, request, *args, **kwargs):
        serializer = CreateReservationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = self.serializer_class(instance=serializer.instance).data
        return Response(
            data=response,
            status=status.HTTP_201_CREATED
        )

    def get_serializer_class(self):
        if self.http_method_names == 'post':
            return CreateReservationSerializer
        else:
            return GetReservationSerializer


class AvailableRoom(generics.ListAPIView):
    serializer_class = GetRoomSerializer
    queryset = Room.objects.all()
    http_method_names = ('post',)
    filter_backends = (
        filters.OrderingFilter,
        DjangoFilterBackend,
    )
    filterset_fields = ('id','hotel_id',)

    def post(self, request, *args, **kwargs):
        serializer = AvailableRoomSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        booked_rooms_id = serializer.get_booked_rooms()
        self.queryset = Room.objects.exclude(id__in=booked_rooms_id)
        return super().list(self, request, *args, **kwargs)


class DownloadBookedRoomsView(APIView):
    def get(self, request, *args, **kwargs):
        serializer = BookedRoomsSerializer(context={'request':request})
        file_info = serializer.write_in_file()
        file_path = file_info['file_path']
        file_name = file_info['file_name']
        with open(file_path, 'r') as f:
            file_data = f.read()
        response = FileResponse(file_data, as_attachment=True, filename=file_name, content_type='application/html')
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response

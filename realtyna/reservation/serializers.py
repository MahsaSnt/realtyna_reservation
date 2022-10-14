from rest_framework import serializers
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
import json

from .models import Hotel, Room, Reservation
from .exceptions import (
    ExistRoomException,
    StartDateAfterEndDateException,
    StartDateBeforeNowException,
    ReservedBeforeException,
)


class HotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = '__all__'


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ('number', 'floor')

    def validate(self, data):
        request = self.context.get('request')
        if request.method == 'post':
            self.hotel_id = request.parser_context['kwargs'].get('hotel_id')
            if Room.objects.filter(hotel_id=self.hotel_id, number=data['number'], floor=data['floor']):
                raise ExistRoomException()
        return data

    def create(self, validated_data):
        validated_data['hotel_id'] = self.hotel_id
        room = Room.objects.create(**validated_data)
        return room


class GetRoomSerializer(serializers.ModelSerializer):
    hotel = HotelSerializer()

    class Meta:
        model = Room
        fields = '__all__'


class GetReservationSerializer(serializers.ModelSerializer):
    room = GetRoomSerializer()

    class Meta:
        model = Reservation
        fields = '__all__'


class AbstractReservationSeializer(serializers.Serializer):
    class Meta:
        abstract = True

    def validate_start_end_date(self, start_date, end_date):
        if start_date > end_date:
            raise StartDateAfterEndDateException()
        if start_date < timezone.now().date():
            raise StartDateBeforeNowException()

    def available_room_condition(self, start_date, end_date):
        return (
                    Q(start_date__lte=start_date) & Q(end_date__gt=start_date)
            ) | (
                    Q(start_date__lt=end_date) & Q(end_date__gte=end_date)
            )


class CreateReservationSerializer(AbstractReservationSeializer):
    customer = serializers.CharField(max_length=100)
    room_id = serializers.IntegerField(min_value=1)
    start_date = serializers.DateField()
    end_date = serializers.DateField()

    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        room_id = data.get('room_id')

        get_object_or_404(Room, id=room_id)
        self.validate_start_end_date(start_date, end_date)

        reserved_in_specific_time = Reservation.objects.filter(room_id=room_id).filter(
            self.available_room_condition(start_date, end_date)
        ).distinct()
        if reserved_in_specific_time:
            raise ReservedBeforeException()
        return data

    def create(self, validated_date):
        return Reservation.objects.create(**validated_date)


class AvailableRoomSerializer(AbstractReservationSeializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()

    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        self.validate_start_end_date(start_date, end_date)
        return data

    def get_booked_rooms(self):
        start_date = self.validated_data.get('start_date')
        end_date = self.validated_data.get('end_date')
        booked_rooms_id = Reservation.objects.filter(
            self.available_room_condition(start_date, end_date)
            ).distinct().values_list('room_id', flat=True)
        return booked_rooms_id


class BookedRoomsSerializer(serializers.Serializer):
    def get_queryset(self):
        query_params = self.context.get('request').query_params
        filters = {}
        required_rooms_id = [room_id for room_id in query_params.get('rooms_id').split(',')]
        if required_rooms_id:
            filters['room_id__in'] = required_rooms_id
        start_date = query_params.get('start_date')
        if start_date:
            filters['end_date__gt'] = start_date
        end_date = query_params.get('end_date')
        if end_date:
            filters['start_date__lt'] = end_date

        return Reservation.objects.filter(**filters).distinct()

    def write_in_file(self):
        queryset = self.get_queryset()
        response = GetReservationSerializer(queryset, many=True).data
        file_name = 'booked_rooms_report.txt'
        file_place = 'media'
        file_path = file_place + '/' + file_name
        file = open(file_path, 'w')
        for item in response:
            file.write(json.dumps(item))
            file.write('\n\n')
        file.close()
        return {'file_name': file_name, 'file_path': file_path}

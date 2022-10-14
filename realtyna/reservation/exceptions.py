from rest_framework import status
from rest_framework.exceptions import APIException


class ExistRoomException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'this room already exists.'


class StartDateAfterEndDateException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'start_date must be before end_date.'


class StartDateBeforeNowException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'start_date must be after today.'


class ReservedBeforeException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'This room is not available in the time.'

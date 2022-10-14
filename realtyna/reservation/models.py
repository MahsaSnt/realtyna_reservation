from django.db import models


class Hotel(models.Model):
    title = models.CharField(
        max_length=100
    )

    def __str__(self):
        return self.title


class Room(models.Model):
    number = models.PositiveSmallIntegerField()
    floor = models.PositiveSmallIntegerField()
    hotel = models.ForeignKey(
        Hotel,
        on_delete=models.CASCADE,
        related_name="room",
    )

    def __str__(self):
        return f"id: {self.id}, hotel: {self.hotel}, floor: {self.floor}, number: {self.number}"

    class Meta:
        unique_together = ("number", "floor", "hotel",)


class Reservation(models.Model):
    room = models.ForeignKey(
        Room,
        on_delete=models.DO_NOTHING,
        related_name='reservation',
    )
    customer = models.CharField(
        max_length=100,
    )
    start_date = models.DateField()
    end_date = models.DateField()


def get_file_upload_path():
    return f'media/file'

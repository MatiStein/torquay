from django.urls import reverse
from subprocess import check_output
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_save
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import Visitor
from django.utils import timezone



class Floor(models.Model):

    floor_choices = enumerate([0,1,2,3,4])
    number = models.IntegerField(choices=floor_choices, primary_key=True)

class Room(models.Model):
    # NO id
    number = models.BigIntegerField(primary_key=True, blank=True)
    beds = models.IntegerField(default=2, validators=[MinValueValidator(2), MaxValueValidator(6)])
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE, related_name='rooms')
    
    @property
    def price(self):
        return 15 * self.beds * self.floor.number

    def __str__(self):
        return f"{self.number}"

    def get_absolute_url(self):
        return reverse('room_detail', args=[self.number]) 

def pre_room_save(sender, instance, *args, **kwargs):
    print('PRE SAVE')
    try:
        instance.full_clean()
        if not instance.number:
            # 1
            floor = instance.floor
            if floor.rooms.all().exists():
                # 100 = 100 + 1 -> 101... 102 ... 103
                new_room_number = floor.rooms.last().number + 1
            else:
                # 1 * 100 = 100
                new_room_number = floor.number * 100
            instance.number = new_room_number
    except:
        raise ValidationError("Number of beds exceeds limit")


pre_save.connect(receiver=pre_room_save, sender=Room)

# 1) Create reservation. 
# 2) Create function calculate_price.

class Reservation(models.Model):
    check_in = models.DateField()
    check_out = models.DateField()
    active = models.BooleanField()
    rooms = models.ManyToManyField(Room, related_name='reservations')
    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE)

    def clean(self):
        if self.check_out <= self.check_in:
            raise ValidationError("Invalid date")

    @property
    def price(self):
        total_price = 0
        for room in self.rooms.all():
            delta = self.check_out - self.check_in
            days = delta.days
            total_price += days * room.price

        return total_price

    def get_absolute_url(self):
        return reverse('reservation_detail', args = [self.id] )
    def __str__(self):
        return f"CHECKIN {self.check_in} | CHECKOUT {self.check_out}"
        

from django import forms
from .models import ( Reservation )
from datetime import date

class ReservationForm(forms.ModelForm):
    
    ROOM_SIZES = ((2,'Small'),(3,'Medium'),(4,'Large'),(5,'XLarge'),(6,'XXLarge'))

    class Meta:
        model = Reservation
        fields = ['check_in', 'check_out']
        labels = {'check_in' :'check_in', 'check_out' : 'check_out'}
        widgets = {
            'check_in' : forms.SelectDateWidget(),
            'check_out' : forms.SelectDateWidget()
        }

    room_size = forms.ChoiceField(choices=ROOM_SIZES)

    def clean(self):
        date_in = self.cleaned_data['check_in']
        date_out = self.cleaned_data['check_out']

        if date_in < date.today():
            raise forms.ValidationError("Past Date!")

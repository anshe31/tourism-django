import datetime
from django.utils import timezone
from django import forms
from django.forms import ModelForm, fields
from .models import Order, Package
from django.forms.widgets import DateInput
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


class NewUserForm(UserCreationForm):
    '''Registration Page - NewUserForm inheriting from Django's predefined UserCreationForm and 
    adding email,first_name and last_name field as mandatory fiels'''
    
    email = forms.EmailField(required=True)
    first_name = forms.CharField(label='First Name', max_length=50,required=True)
    last_name = forms.CharField(label='Last Name',max_length=50,required=True)

    class Meta:
        model = User
        # Fields to be shown in Registration page
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")

    

    def save(self, commit=True):
        '''Overriding save method of UserCreationForm to add email,first_name and last_name fields'''
        # with commit=False,it will return an object that hasn't yet been saved to the database. In this case,we save() on the resulting model instance after adding other fields.
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

class OrderForm(ModelForm):
    '''Form to input required Order Details- mapped with Order table'''
    # package = forms.ModelChoiceField(queryset=Package.objects.all())
    
    class Meta:
        model = Order
        fields = ['id','package', 'no_of_people', 'travel_date']
        widgets = {
            'travel_date': DateInput(attrs={'type': 'date'})
        }
    
    def clean_no_of_people(self):
        ''' Validate that no of people must be 1 at least'''
        count = self.cleaned_data['no_of_people']
        if count <= 0:
            raise ValidationError("No. of People Must be greater than or equal to 1.")
        return count
    
    def clean_travel_date(self):
        ''' Validate that travel date must be from next day onwards'''

        travel_date = self.cleaned_data['travel_date']
        tomorrow_date = timezone.now() + datetime.timedelta(days=1)

        if travel_date < tomorrow_date:
            raise ValidationError("Travel date must be from 24 hours+ onwards. Please donot select today's or past dates.")
        return travel_date
    

    
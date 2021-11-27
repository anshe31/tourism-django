from django import forms
from django.forms import ModelForm, fields
from .models import Order, Package
from django.forms.widgets import DateInput
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# https://ordinarycoders.com/blog/article/django-user-register-login-logout
class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(label='First Name', max_length=50)
    last_name = forms.CharField(label='Last Name',max_length=50)


    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")
        
    def save(self, commit=True):
        # with commit=False , then it will return an object that hasn't yet been saved to the database. In this case, it's up to you to call save() on the resulting model instance.
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class OrderForm(ModelForm):
    
    # package = forms.ModelChoiceField(queryset=Package.objects.all())
    
    class Meta:
        model = Order
        fields = ['id','package', 'no_of_people', 'travel_date']
        widgets = {
            'travel_date': DateInput(attrs={'type': 'date'})
        }

    # fname = forms.CharField(label='First Name', max_length=50)
    # lname = forms.CharField(label='Last Name', max_length=50)
    # dob = forms.DateField(label='Date of Birth')
    # contact = forms.IntegerField(label='Mobile No',max_value=9999999999)
    # email = forms.EmailField(label='Email', max_length=50)
    # no_of_people = forms.IntegerField(label='No. of People', max_value=30)
    # travel_date = forms.DateTimeField()
    # package = Foreign key
    
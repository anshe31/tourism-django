from django.db import models
from django.contrib.auth.models import User

# # Create your models here.
# class Person(models.Model):
#     fname = models.CharField(max_length=50)
#     lname = models.CharField(max_length=50)
#     dob = models.DateField()
#     contact = models.IntegerField()
#     email = models.EmailField()
    
#     def __str__(self):
#         return '{},{},{},{},{}'.format(self.fname, self.lname, self.dob, self.contact, self.email)

class Package(models.Model):
    package_name = models.CharField(max_length=50, primary_key=True)
    days = models.IntegerField(default=3)
    baseprice = models.FloatField()
    
    def __str__(self):
        return '{},{} days, ${}'.format(self.package_name, self.days, self.baseprice)

class Order(models.Model):
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    # person = models.ForeignKey(Person, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    no_of_people = models.IntegerField()
    order_price = models.FloatField()
    order_create_date = models.DateTimeField(auto_now_add=True)
    order_update_date = models.DateTimeField(auto_now=True)
    travel_date = models.DateTimeField()
    
    def __str__(self):
         return '{},{},{},{},{}'.format(self.user, self.package, self.no_of_people, self.order_price, self.travel_date)
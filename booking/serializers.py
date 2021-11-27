from django.db.models import fields
from booking import models
from rest_framework import serializers

        

class PackageSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.Package
        fields = '__all__'
        
class OrderSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.Order
        fields = '__all__'
        
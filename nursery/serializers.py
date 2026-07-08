from rest_framework import serializers
from .models import Plant, Pot, Customer, Order, OrderItem, Fertilizer
from django.contrib.auth.models import User

class PlantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plant
        fields = '__all__'

class PotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pot
        fields = '__all__'

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'  
        
class OrderItemSerializer(serializers.ModelSerializer):
    price = serializers.ReadOnlyField()
    class Meta:
        model = OrderItem
        fields = '__all__'

class FertilizerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fertilizer
        fields = "__all__"    

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email"] 

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
from rest_framework import serializers
from .models import Plant, Pot, Customer, Order, OrderItem, Fertilizer, Admin, UserProfile
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

class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = "__all__"

class AdminLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    role = serializers.CharField()

class UserSerializer(serializers.ModelSerializer):
    mobile = serializers.CharField(write_only=True)
    role = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
            'mobile',
            'role'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        mobile = validated_data.pop('mobile')
        role = validated_data.pop('role')

        user = User.objects.create_user(**validated_data)

        UserProfile.objects.create(
            user=user,
            mobile=mobile,
            role=role
        )

        return user
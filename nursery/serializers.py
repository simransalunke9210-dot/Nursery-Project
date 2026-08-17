from rest_framework import serializers
from .models import Plant, Pot, Customer, Order, OrderItem, Fertilizer, Admin, UserProfile, OrderRating
from django.contrib.auth.models import User
from .models import PlantImage


class PlantSerializer(serializers.ModelSerializer):

    class Meta:
        model = Plant
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)

        request = self.context.get('request')

        if instance.image:
            if request:
                data['image'] = request.build_absolute_uri(instance.image.url)
            else:
                data['image'] = instance.image.url
        else:
            data['image'] = None

        return data

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

from rest_framework import serializers
from .models import Cart, CartItem


class AddToCartSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    plant_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1)

class PlantImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = PlantImage
        fields = ['id', 'image']

    def to_representation(self, instance):
        data = super().to_representation(instance)

        request = self.context.get('request')

        if instance.image:
            if request:
                data['image'] = request.build_absolute_uri(
                    instance.image.url
                )
            else:
                data['image'] = instance.image.url

        return data

class OrderItemSerializer(serializers.ModelSerializer):

    plant_name = serializers.CharField(
        source='plant.name',
        read_only=True
    )

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'plant',
            'plant_name',
            'quantity',
            'price'
        ]

class OrderSerializer(serializers.ModelSerializer):

    items = OrderItemSerializer(
        source='orderitem_set',
        many=True,
        read_only=True
    )

    class Meta:
        model = Order
        fields = [
            'id',
            'customer',
            'date',
            'total_amount',
            'status',
            'shipping_address',
            'expected_delivery',
            'items'
        ]

class OrderRatingSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderRating
        fields = [
            'id',
            'order',
            'customer',
            'rating',
            'review',
            'created_at'
        ]

    def validate_rating(self, value):

        if value < 1 or value > 5:
            raise serializers.ValidationError(
                "Rating must be between 1 and 5."
            )

        return value


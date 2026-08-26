from rest_framework import serializers
from .models import Plant, Pot, Customer, Order, OrderItem, Fertilizer, Admin, UserProfile, OrderRating,Settings
from django.contrib.auth.models import User
from .models import PlantImage, PotImage, FertilizerImage

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

class PlantSerializer(serializers.ModelSerializer):

    images = PlantImageSerializer(
        source='plant_images',
        many=True,
        read_only=True
    )

    class Meta:
        model = Plant
        fields = [
            'id',
            'name',
            'category',
            'description',
            'price',
            'quantity',
            'images'
        ]

class PotImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = PotImage
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

class PotSerializer(serializers.ModelSerializer):

    images = PotImageSerializer(
        source='pot_images',
        many=True,
        read_only=True
    )

    class Meta:
        model = Pot
        fields = [
            'id',
            'name',
            'category',
            'price',
            'stock',
            'description',
            'images'
        ]

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

class FertilizerImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = FertilizerImage
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

class FertilizerSerializer(serializers.ModelSerializer):

    images = FertilizerImageSerializer(
        source='fertilizer_images',
        many=True,
        read_only=True
    )

    class Meta:
        model = Fertilizer
        fields = [
            'id',
            'name',
            'price',
            'quantity',
            'description',
            'images'
        ]   

class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = [
            'id',
            'name',
            'email',
            'password',
            'mobile',
            'role'
        ]

class AdminLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    role = serializers.CharField()

class UserSerializer(serializers.ModelSerializer):
    mobile = serializers.CharField(write_only=True)

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
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        mobile = validated_data.pop('mobile')

        user = User.objects.create_user(**validated_data)

        UserProfile.objects.create(
            user=user,
            mobile=mobile,
            role='Customer'
        )

        return user

from rest_framework import serializers
from .models import Cart, CartItem


class AddToCartSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()

    product_type = serializers.ChoiceField(
        choices=['plant', 'pot', 'fertilizer']
    )

    product_id = serializers.IntegerField()

    quantity = serializers.IntegerField(default=1)

class AddToWishlistSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()

    product_type = serializers.ChoiceField(
        choices=['plant', 'pot', 'fertilizer']
    )

    product_id = serializers.IntegerField()


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

class ReportSerializer(serializers.Serializer):
    total_plants = serializers.IntegerField()
    total_customers = serializers.IntegerField()
    total_orders = serializers.IntegerField()
    total_revenue = serializers.FloatField()
    pending_orders = serializers.IntegerField()
    delivered_orders = serializers.IntegerField()
    cancelled_orders = serializers.IntegerField()
    total_items_sold = serializers.IntegerField()
    total_ratings = serializers.IntegerField()
    average_rating = serializers.FloatField()


class SettingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Settings
        fields = [
            'id',
            'website_name',
            'phone',
            'email',
            'address',
            'logo',
            'delivery_charge',
            'free_delivery_above',
            'currency',
            'admin_name',
            'new_password',
            'facebook_url',
            'instagram_url',
            'contact_phone',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


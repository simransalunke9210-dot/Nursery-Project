from rest_framework import serializers
from .models import Plant, Customer, Order, OrderItem, Cart, CartItem

class PlantSerializer(serializers.ModelSerializer):

    class Meta:
        model = Plant
        fields = '__all__'

class CartItemSerializer(serializers.ModelSerializer):
    plant_name = serializers.CharField(source='plant.name', read_only=True)
    plant_price = serializers.FloatField(source='plant.price', read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            'id',
            'plant',
            'plant_name',
            'plant_price',
            'quantity',
            'subtotal'
        ]

    def get_subtotal(self, obj):
        return obj.plant.price * obj.quantity


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [
            'id',
            'user',
            'items',
            'total_amount',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'user',
            'items',
            'total_amount',
            'created_at',
            'updated_at'
        ]

    def get_total_amount(self, obj):
        return sum(
            item.plant.price * item.quantity
            for item in obj.items.all()
        )
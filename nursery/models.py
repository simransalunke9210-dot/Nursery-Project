from django.db import models

from django.db import models
from django.contrib.auth.models import User

class Plant(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    price = models.FloatField()
    quantity = models.IntegerField()
    image = models.ImageField(upload_to='plants/', null=True, blank=True)

    def __str__(self):
        return self.name

    def __str__(self):
        return self.name

class PlantImage(models.Model):
    plant = models.ForeignKey(
        Plant,
        on_delete=models.CASCADE,
        related_name='plant_images'
    )
    image = models.ImageField(upload_to='plants/')

    def __str__(self):
        return f"{self.plant.name} Image"

class Customer(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    password = models.CharField(max_length=100, blank=True, null=True)
    role = models.CharField(max_length=20, default="Customer")

    def __str__(self):
        return self.name
    
class Order(models.Model):

    STATUS_CHOICES = (
        ('ORDER_PLACED', 'Order Placed'),
        ('PACKED', 'Packed'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='orders'
    )

    date = models.DateField(auto_now_add=True)

    total_amount = models.FloatField(default=0)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ORDER_PLACED'
    )

    shipping_address = models.TextField(
        blank=True,
        null=True
    )

    expected_delivery = models.DateField(
        blank=True,
        null=True
    )

    cancelled_at = models.DateTimeField(
        blank=True,
        null=True
    )

    def __str__(self):
        return f"Order {self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.FloatField()

    def save(self, *args, **kwargs):
        self.price = self.plant.price * self.quantity
        super().save(*args, **kwargs)   

class Pot(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    description = models.TextField()
    image = models.ImageField(upload_to='pots/', null=True, blank=True)    

    def __str__(self):
        return self.name   

class Fertilizer(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='fertilizers/', null=True, blank=True)

    def __str__(self):
        return self.name  
class Admin(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15)
    password = models.CharField(max_length=100)
    role = models.CharField(max_length=20, default="Admin")

    def __str__(self):
        return self.name
    
class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('Customer', 'Customer'),
        ('Admin', 'Admin'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile = models.CharField(max_length=10)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Customer')

    def __str__(self):
        return self.user.username

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    plant = models.ForeignKey(
        Plant,
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['cart', 'plant'],
                name='unique_cart_plant'
            )
        ]

    def __str__(self):
        return f"{self.plant.name} x {self.quantity}"

class Wishlist(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='wishlist'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Wishlist"


class WishlistItem(models.Model):
    wishlist = models.ForeignKey(
        Wishlist,
        on_delete=models.CASCADE,
        related_name='items'
    )
    plant = models.ForeignKey(
        Plant,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['wishlist', 'plant'],
                name='unique_wishlist_plant'
            )
        ]

    def __str__(self):
        return f"{self.plant.name} - {self.wishlist.user.username}"

class OrderRating(models.Model):

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='rating'
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE
    )

    rating = models.PositiveIntegerField()

    review = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Rating for Order {self.order.id}"
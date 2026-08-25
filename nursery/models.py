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
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    plant = models.ForeignKey(
        Plant,
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField()
    price = models.FloatField(default=0)

    def save(self, *args, **kwargs):
        # ALWAYS get price from database
        self.price = float(self.plant.price) * self.quantity

        super().save(*args, **kwargs)

        # Recalculate complete order total
        total = sum(
            item.price
            for item in self.order.items.all()
        )

        self.order.total_amount = total
        self.order.save(update_fields=['total_amount'])

    def delete(self, *args, **kwargs):
        order = self.order

        super().delete(*args, **kwargs)

        # Recalculate total after deleting item
        total = sum(
            item.price
            for item in order.items.all()
        )

        order.total_amount = total
        order.save(update_fields=['total_amount'])   


class Pot(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    description = models.TextField()

    def __str__(self):
        return self.name


class PotImage(models.Model):
    pot = models.ForeignKey(
        Pot,
        on_delete=models.CASCADE,
        related_name='pot_images'
    )
    image = models.ImageField(upload_to='pots/')

    def __str__(self):
        return f"{self.pot.name} Image"


class Fertilizer(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    description = models.TextField(
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name


class FertilizerImage(models.Model):
    fertilizer = models.ForeignKey(
        Fertilizer,
        on_delete=models.CASCADE,
        related_name='fertilizer_images'
    )
    image = models.ImageField(upload_to='fertilizers/')

    def __str__(self):
        return f"{self.fertilizer.name} Image"

  
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

    product_type = models.CharField(
        max_length=20,
        choices=[
            ('plant', 'Plant'),
            ('pot', 'Pot'),
            ('fertilizer', 'Fertilizer'),
        ],
        null=True,
        blank=True
    )

    product_id = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['cart', 'product_type', 'product_id'],
                name='unique_cart_product'
            )
        ]

    def __str__(self):
        return f"{self.product_type} #{self.product_id} x {self.quantity}"


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

    product_type = models.CharField(
        max_length=20,
        choices=[
            ('plant', 'Plant'),
            ('pot', 'Pot'),
            ('fertilizer', 'Fertilizer'),
        ],
        null=True,
        blank=True
    )

    product_id = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['wishlist', 'product_type', 'product_id'],
                name='unique_wishlist_product'
            )
        ]

    def __str__(self):
        return (
            f"{self.product_type} #{self.product_id} - "
            f"{self.wishlist.user.username}"
        )

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


class Settings(models.Model):
    # Website Information
    website_name = models.CharField(max_length=200, default="Nursery")
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    # Logo
    logo = models.ImageField(
        upload_to='settings/',
        blank=True,
        null=True
    )

    # Store Settings
    delivery_charge = models.FloatField(default=0)
    free_delivery_above = models.FloatField(default=0)
    currency = models.CharField(max_length=10, default="INR")

    # Admin Settings
    admin_name = models.CharField(max_length=100, blank=True, null=True)
    new_password = models.CharField(max_length=255, blank=True, null=True)

    # Social Media
    facebook_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.website_name

from django.db import models

from django.db import models
from django.contrib.auth.models import User

class Plant(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    price = models.FloatField()
    quantity = models.IntegerField()
    image = models.ImageField(upload_to='plants/', null=True, blank=True)

    def __str__(self):
        return self.name

class Customer(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    password = models.CharField(max_length=100, blank=True, null=True)
    role = models.CharField(max_length=20, default="Customer")

    def __str__(self):
        return self.name
    
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    total_amount = models.FloatField(default=0)

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
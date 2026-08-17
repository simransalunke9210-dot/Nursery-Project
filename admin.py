# from django.contrib import admin

# from django.contrib import admin

# admin.site.site_header = "Nursery Management System"
# admin.site.site_title = "Nursery Admin"
# admin.site.index_title = "Welcome to Nursery Dashboard"

# from .models import Plant

# admin.site.register(Plant)

# from .models import Customer
# admin.site.register(Customer)

# from .models import Order, OrderItem

# admin.site.register(Order)
# admin.site.register(OrderItem)

from django.contrib import admin
from .models import Plant, Customer, Order, OrderItem

admin.site.site_header = "Nursery Management System"
admin.site.site_title = "Nursery Admin"
admin.site.index_title = "Welcome to Nursery Dashboard"

admin.site.register(Plant)
admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(OrderItem)
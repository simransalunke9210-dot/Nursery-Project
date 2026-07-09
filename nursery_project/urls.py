from django.contrib import admin
from django.urls import path
from nursery import views
from django.conf import settings
from django.conf.urls.static import static
from nursery.views import FertilizerView, FertilizerDetailView, AdminView, AdminDetailView
from nursery.views import (
    add_plant,
    plant_list,
    # dashboard,
    edit_plant,
    delete_plant,

    add_pot,
    pot_list,
    edit_pot,
    delete_pot,
)

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Nursery API",
      default_version='v1',
      description="Nursery Management System API",
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)


urlpatterns = [
    path('admin/', admin.site.urls),

    # 🌿 Home page
    # path('', plant_list, name='plant_list'),
    path('', views.home),

    # 🌿 Add plant
    path('add-plant/', add_plant, name='add_plant'),

    # 🌿 Plant list (optional duplicate safe)
    path('plants/', plant_list, name='plant_list'),

    # ✏️ Edit plant (MISSING FIX)
    path('edit/<int:id>/', edit_plant, name='edit_plant'),

    # ❌ Delete plant (MISSING FIX)
    path('delete/<int:id>/', delete_plant, name='delete_plant'),

    path('api/plant/allPlants/', views.get_plants),
    path('api/plant/addPlant/', views.add_plant_api),
    path('api/plant/updatePlant/<int:id>/', views.update_plant_api),
    path('api/plant/deletePlant/<int:id>/', views.delete_plant_api),

    path('api/pot/allPots/', views.get_pots),
    path('api/pot/addPot/', views.add_pot_api),
    path('api/pot/updatePot/<int:id>/', views.update_pot_api),
    path('api/pot/deletePot/<int:id>/', views.delete_pot_api),

    path('api/customer/allCustomers/', views.get_customers),
    path('api/customer/addCustomer/', views.add_customer_api),
    path('api/customer/updateCustomer/<int:id>/', views.update_customer_api),
    path('api/customer/deleteCustomer/<int:id>/', views.delete_customer_api),

    path('api/order/allOrders/', views.get_orders),
    path('api/order/addOrder/', views.add_order_api),
    path('api/order/updateOrder/<int:id>/', views.update_order_api),
    path('api/order/deleteOrder/<int:id>/', views.delete_order_api),

    path('api/orderitem/allOrderItems/', views.get_order_items),
    path('api/orderitem/addOrderItem/', views.add_order_item_api),
    path('api/orderitem/updateOrderItem/<int:id>/', views.update_order_item_api),
    path('api/orderitem/deleteOrderItem/<int:id>/', views.delete_order_item_api),

    path('api/fertilizer/allFertilizers/', FertilizerView.as_view()),
    path('api/fertilizer/updateFertilizer/<int:id>/', FertilizerDetailView.as_view()),

    path('api/admins/', AdminView.as_view()),
    path('api/admins/<int:id>/', AdminDetailView.as_view()),
    path('api/admins/login/', views.login_api),

    path('api/users/', views.UserView.as_view()),
    path('api/users/register/', views.register_user),
    path('api/users/login/', views.user_login),

    path(
    'swagger/',
    schema_view.with_ui('swagger', cache_timeout=0),
    name='schema-swagger-ui'
),
path(
    'redoc/',
    schema_view.with_ui('redoc', cache_timeout=0),
    name='schema-redoc'
),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
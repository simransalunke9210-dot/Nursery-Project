from django.contrib import admin
from django.urls import path,include
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
    track_order_api,
    download_invoice_api,
    order_again_api,
    cancel_order_api,
    rate_order_api,
)


from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings
from django.conf.urls.static import static

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

    path('api/users/', views.UserView.as_view()),
    path('api/users/register/', views.register_user),
    path('api/users/update/<int:id>/', views.update_user),
    path('api/users/delete/<int:id>/', views.delete_user),
    
    path('api/login/', views.login),
    path('api/cart/add/', views.add_to_cart, name='add_to_cart'),
    path('api/cart/', views.view_cart, name='view_cart'),
    path('api/wishlist/add/', views.add_to_wishlist, name='add_to_wishlist'),
    path('api/wishlist/', views.view_wishlist, name='view_wishlist'),
    path('api/wishlist/remove/',views.remove_from_wishlist,name='remove_from_wishlist'),
    path('api/cart/remove/',views.remove_from_cart,name='remove_from_cart'),
    path('api/cart/update/',views.update_cart_quantity,name='update_cart_quantity'),
    path('orders/<int:order_id>/track/',views.track_order_api,name='track-order'),
    path('orders/<int:order_id>/invoice/',views.download_invoice_api,name='download-invoice'),
    path('orders/<int:order_id>/order-again/',views.order_again_api,name='order-again'),
    path('orders/<int:order_id>/cancel/',views.cancel_order_api,name='cancel-order'),
    path('orders/<int:order_id>/rating/',views.rate_order_api,name='rate-order'),
    path('reports/',views.ReportsView.as_view(),name='reports'),
    path('api/settings/',views.SettingsView.as_view(),name='settings'),

    path('swagger/',schema_view.with_ui('swagger', cache_timeout=0),name='schema-swagger-ui'),
    path('redoc/',schema_view.with_ui('redoc', cache_timeout=0),name='schema-redoc'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
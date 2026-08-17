from django.shortcuts import render, redirect, get_object_or_404
from .models import Plant, Pot, Customer, Order, OrderItem, Fertilizer, Admin, PlantImage,OrderRating
from .forms import PlantForm, PotForm

from django.contrib.auth import authenticate
from .models import UserProfile

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response 
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import PlantSerializer, PotSerializer, CustomerSerializer, OrderSerializer, OrderItemSerializer, FertilizerSerializer, UserSerializer, AdminSerializer, AdminLoginSerializer
from django.contrib.auth.models import User
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import api_view
from reportlab.pdfgen import canvas

def home(request):
    return HttpResponse("Welcome to Nursery Management System")

def dashboard(request):
    return render(request, 'dashboard.html')


def plant_list(request):
    plants = Plant.objects.all()
    return render(request, 'plant_list.html', {'plants': plants})


def add_plant(request):
    form = PlantForm()

    if request.method == "POST":
        form = PlantForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('plant_list')

    return render(request, 'add_plant.html', {'form': form})

def edit_plant(request, id):
    plant = get_object_or_404(Plant, id=id)
    form = PlantForm(instance=plant)

    if request.method == "POST":
        form = PlantForm(request.POST, instance=plant)
        if form.is_valid():
            form.save()
            return redirect('plant_list')

    return render(request, 'edit_plant.html', {'form': form})

def delete_plant(request, id):
    plant = get_object_or_404(Plant, id=id)
    plant.delete()
    return redirect('plant_list')



@swagger_auto_schema(
    method='get',
    tags=['plant']
)
@api_view(['GET'])
def get_plants(request):

    plants = Plant.objects.all()

    serializer = PlantSerializer(plants, many=True)

    return Response({
        "status": "success",
        "code": 200,
        "message": "All plants fetched",
        "data": serializer.data
    })


@swagger_auto_schema(
    method='post',
    manual_parameters=[
        openapi.Parameter(
            'name',
            openapi.IN_FORM,
            description='Plant name',
            type=openapi.TYPE_STRING,
            required=True
        ),
        openapi.Parameter(
            'category',
            openapi.IN_FORM,
            description='Plant category',
            type=openapi.TYPE_STRING,
            required=True
        ),
        openapi.Parameter(
            'description',
            openapi.IN_FORM,
            description='Plant description',
            type=openapi.TYPE_STRING,
            required=False
        ),
        openapi.Parameter(
            'price',
            openapi.IN_FORM,
            description='Plant price',
            type=openapi.TYPE_NUMBER,
            required=True
        ),
        openapi.Parameter(
            'quantity',
            openapi.IN_FORM,
            description='Plant quantity',
            type=openapi.TYPE_INTEGER,
            required=True
        ),
        openapi.Parameter(
            'image1',
            openapi.IN_FORM,
            description='First plant image',
            type=openapi.TYPE_FILE,
            required=True
        ),
        openapi.Parameter(
            'image2',
            openapi.IN_FORM,
            description='Second plant image - optional',
            type=openapi.TYPE_FILE,
            required=False
        ),
        openapi.Parameter(
            'image3',
            openapi.IN_FORM,
            description='Third plant image - optional',
            type=openapi.TYPE_FILE,
            required=False
        ),
    ],
    consumes=['multipart/form-data'],
    tags=['plant']
)
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def add_plant_api(request):

    # Get plant data
    plant_data = {
    'name': request.data.get('name'),
    'category': request.data.get('category'),
    'description': request.data.get('description'),
    'price': request.data.get('price'),
    'quantity': request.data.get('quantity'),
}

    # Create plant
    plant_serializer = PlantSerializer(
        data=plant_data,
        context={'request': request}
    )

    if not plant_serializer.is_valid():
        return Response({
            "status": "failed",
            "code": 400,
            "message": "Plant addition failed",
            "errors": plant_serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    plant = plant_serializer.save()

    # Get uploaded images
    images = []

    image1 = request.FILES.get('image1')
    image2 = request.FILES.get('image2')
    image3 = request.FILES.get('image3')

    if image1:
        images.append(image1)

    if image2:
        images.append(image2)

    if image3:
        images.append(image3)

    # At least one image is required
    if len(images) == 0:

        plant.delete()

        return Response({
            "status": "failed",
            "code": 400,
            "message": "At least one image is required"
        }, status=status.HTTP_400_BAD_REQUEST)

    # Maximum 3 images
    if len(images) > 3:

        plant.delete()

        return Response({
            "status": "failed",
            "code": 400,
            "message": "Maximum 3 images are allowed"
        }, status=status.HTTP_400_BAD_REQUEST)

    # Save images
    for image in images:

        PlantImage.objects.create(
            plant=plant,
            image=image
        )

    # Create image URLs
    image_urls = []

    for plant_image in plant.plant_images.all():

        image_urls.append(
            request.build_absolute_uri(
                plant_image.image.url
            )
        )

    return Response({
        "status": "success",
        "code": 201,
        "message": "Plant added successfully",
        "data": {
            "id": plant.id,
            "name": plant.name,
            "category": plant.category,
            "description": plant.description,
            "price": plant.price,
            "quantity": plant.quantity,
            "images": image_urls
        }
    }, status=status.HTTP_201_CREATED)

@api_view(['PUT'])
@swagger_auto_schema(
    request_body=PlantSerializer,
    tags=['plant']
)
def update_plant_api(request, id):

    plant = get_object_or_404(Plant, id=id)

    serializer = PlantSerializer(
        plant,
        data=request.data,
        partial=True
    )

    if serializer.is_valid():

        serializer.save()

        return Response({
            "status": "success",
            "code": 200,
            "message": "Plant updated successfully",
            "data": serializer.data
        })

    return Response({
        "status": "failed",
        "code": 400,
        "message": "Update failed",
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@swagger_auto_schema(
    tags=['plant']
)
def delete_plant_api(request, id):

    plant = get_object_or_404(Plant, id=id)

    plant.delete()

    return Response({
        "status": "success",
        "code": 200,
        "message": "Plant deleted successfully"
    })

def pot_list(request):
    pots = Pot.objects.all()
    return render(request, 'pot_list.html', {'pots': pots})

def add_pot(request):
    form = PotForm()

    if request.method == "POST":
        form = PotForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            return redirect('pot_list')

    return render(request, 'add_pot.html', {'form': form})

def edit_pot(request, id):
    pot = get_object_or_404(Pot, id=id)
    form = PotForm(instance=pot)

    if request.method == "POST":
        form = PotForm(request.POST, request.FILES, instance=pot)

        if form.is_valid():
            form.save()
            return redirect('pot_list')

    return render(request, 'edit_pot.html', {'form': form})

def delete_pot(request, id):
    pot = get_object_or_404(Pot, id=id)
    pot.delete()
    return redirect('pot_list')

@swagger_auto_schema(
    method='get',
    tags=['Pots'],

)
@api_view(['GET'])
def get_pots(request):

    pots = Pot.objects.all()

    serializer = PotSerializer(pots, many=True)

    return Response({
        "status": "success",
        "code": 200,
        "message": "All pots fetched",
        "data": serializer.data
    })

@swagger_auto_schema(
    method='post',
    tags=['Pots'],
    request_body=PotSerializer
)

@api_view(['POST'])
def add_pot_api(request):

    serializer = PotSerializer(
        data=request.data
    )

    if serializer.is_valid():

        serializer.save()

        return Response({
            "status": "success",
            "code": 200,
            "message": "Pot added successfully",
            "data": serializer.data
        })

    return Response({
        "status": "failed",
        "code": 400,
        "errors": serializer.errors
    })

@swagger_auto_schema(
    method='put',
    tags=['Pots'],
)

@api_view(['PUT'])
def update_pot_api(request, id):

    pot = Pot.objects.get(id=id)

    serializer = PotSerializer(
        pot,
        data=request.data,
        partial=True
    )

    if serializer.is_valid():

        serializer.save()

        return Response({
            "status": "success",
            "code": 200,
            "message": "Pot updated successfully",
            "data": serializer.data
        })

    return Response({
        "status": "failed",
        "code": 400,
        "errors": serializer.errors
    })

@swagger_auto_schema(
    method='delete',
    tags=['Pots'])

@api_view(['DELETE'])
def delete_pot_api(request, id):

    pot = Pot.objects.get(id=id)

    pot.delete()

    return Response({
        "status": "success",
        "code": 200,
        "message": "Pot deleted successfully"
    })

@swagger_auto_schema(
    method='get',
    tags=['Customers']
)

@api_view(['GET'])
def get_customers(request):

    customers = Customer.objects.all()

    serializer = CustomerSerializer(customers, many=True)

    return Response({
        "status": "success",
        "code": 200,
        "message": "All customers fetched",
        "data": serializer.data
    })

@swagger_auto_schema(
    method='post',
    tags=['Customers'],
    request_body=CustomerSerializer
)
@api_view(['POST'])
def add_customer_api(request):

    serializer = CustomerSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()

        return Response({
            "status": "success",
            "code": 200,
            "message": "Customer added successfully",
            "data": serializer.data
        })

    return Response({
        "status": "failed",
        "code": 400,
        "errors": serializer.errors
    })

@swagger_auto_schema(
    method='put',
    tags=['Customers']
)

@api_view(['PUT'])
def update_customer_api(request, id):

    customer = Customer.objects.get(id=id)

    serializer = CustomerSerializer(
        customer,
        data=request.data
    )

    if serializer.is_valid():

        serializer.save()

        return Response({
            "status": "success",
            "code": 200,
            "message": "Customer updated successfully",
            "data": serializer.data
        })

    return Response({
        "status": "failed",
        "code": 400,
        "errors": serializer.errors
    })

@swagger_auto_schema(
    method='delete',
    tags=['Customers']
)

@api_view(['DELETE'])
def delete_customer_api(request, id):

    customer = Customer.objects.get(id=id)

    customer.delete()

    return Response({
        "status": "success",
        "code": 200,
        "message": "Customer deleted successfully"
    })

@swagger_auto_schema(
    method='get',
    tags=['Orders']
)

@api_view(['GET'])
def get_orders(request):

    orders = Order.objects.all()

    serializer = OrderSerializer(orders, many=True)

    return Response({
        "status": "success",
        "code": 200,
        "message": "All orders fetched",
        "data": serializer.data
    })

@swagger_auto_schema(
    method='post',
    tags=['Orders'],
    request_body=OrderSerializer
)
@api_view(['POST'])
def add_order_api(request):

    serializer = OrderSerializer(data=request.data)

    if serializer.is_valid():

        serializer.save()

        return Response({
            "status": "success",
            "code": 200,
            "message": "Order added successfully",
            "data": serializer.data
        })

    return Response({
        "status": "failed",
        "code": 400,
        "errors": serializer.errors
    })

@swagger_auto_schema(
    method='put',
    tags=['Orders']
)

@api_view(['PUT'])
def update_order_api(request, id):

    order = Order.objects.get(id=id)

    serializer = OrderSerializer(
        order,
        data=request.data
    )

    if serializer.is_valid():

        serializer.save()

        return Response({
            "status": "success",
            "code": 200,
            "message": "Order updated successfully",
            "data": serializer.data
        })

    return Response({
        "status": "failed",
        "code": 400,
        "errors": serializer.errors
    })

@swagger_auto_schema(
    method='delete',
    tags=['Orders']
)

@api_view(['DELETE'])
def delete_order_api(request, id):

    order = Order.objects.get(id=id)

    order.delete()

    return Response({
        "status": "success",
        "code": 200,
        "message": "Order deleted successfully"
    })

@swagger_auto_schema(
    method='get',
    tags=['order_items']
)

@api_view(['GET'])
def get_order_items(request):

    order_items = OrderItem.objects.all()

    serializer = OrderItemSerializer(order_items, many=True)

    return Response({
        "status": "success",
        "code": 200,
        "message": "All order items fetched",
        "data": serializer.data
    })

@swagger_auto_schema(
    method='post',
    tags=['order_items'],
    request_body=OrderItemSerializer
)
@api_view(['POST'])
def add_order_item_api(request):

    serializer = OrderItemSerializer(data=request.data)

    if serializer.is_valid():

        serializer.save()

        return Response({
            "status": "success",
            "code": 200,
            "message": "Order item added successfully",
            "data": serializer.data
        })

    return Response({
        "status": "failed",
        "code": 400,
        "errors": serializer.errors
    })

@swagger_auto_schema(
    method='put',
    tags=['order_items']
)

@api_view(['PUT'])
def update_order_item_api(request, id):

    order_item = OrderItem.objects.get(id=id)

    serializer = OrderItemSerializer(
        order_item,
        data=request.data
    )

    if serializer.is_valid():

        serializer.save()

        return Response({
            "status": "success",
            "code": 200,
            "message": "Order item updated successfully",
            "data": serializer.data
        })

    return Response({
        "status": "failed",
        "code": 400,
        "errors": serializer.errors
    })

@swagger_auto_schema(
    method='delete',
    tags=['order_items']
)

@api_view(['DELETE'])
def delete_order_item_api(request, id):

    order_item = OrderItem.objects.get(id=id)

    order_item.delete()

    return Response({
        "status": "success",
        "code": 200,
        "message": "Order item deleted successfully"
    })

from rest_framework.views import APIView
# from rest_framework.response import Response
from .models import Fertilizer
from .serializers import FertilizerSerializer

from drf_yasg.utils import swagger_auto_schema
class FertilizerView(APIView):

    def get(self, request):
        fertilizers = Fertilizer.objects.all()
        serializer = FertilizerSerializer(fertilizers, many=True)

        return Response({
            "status": "success",
            "code": 200,
            "message": "All fertilizers fetched",
            "data": serializer.data
        })
    
    @swagger_auto_schema(request_body=FertilizerSerializer)
    def post(self, request):
        serializer = FertilizerSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "success",
                "code": 201,
                "message": "Fertilizer added successfully",
                "data": serializer.data
            })

        return Response({
            "status": "failed",
            "code": 400,
            "errors": serializer.errors
        })
    
class FertilizerDetailView(APIView):

    @swagger_auto_schema(request_body=FertilizerSerializer)
    def put(self, request, id):
        fert = get_object_or_404(Fertilizer, id=id)
        serializer = FertilizerSerializer(fert, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "success",
                "message": "Updated successfully",
                "data": serializer.data
            })

        return Response({
            "status": "failed",
            "errors": serializer.errors
        })

    def delete(self, request, id):
        fert = get_object_or_404(Fertilizer, id=id)
        fert.delete()

        return Response({
            "status": "success",
            "message": "Deleted successfully"
        })
    
class AdminView(APIView):

    @swagger_auto_schema(
        tags=['admins']
    )
    def get(self, request):
        admins = Admin.objects.all()
        serializer = AdminSerializer(admins, many=True)

        return Response({
            "status": "success",
            "code": 200,
            "message": "All admins fetched successfully",
            "data": serializer.data
        })

    @swagger_auto_schema(
        request_body=AdminSerializer,
        tags=['admins']
    )
    def post(self, request):
        serializer = AdminSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response({
                "status": "success",
                "code": 201,
                "message": "Admin added successfully",
                "data": serializer.data
            })

        return Response({
            "status": "failed",
            "code": 400,
            "errors": serializer.errors
        })
    

class AdminDetailView(APIView):

    @swagger_auto_schema(
        request_body=AdminSerializer,
        tags=['admins']
    )
    def put(self, request, id):
        admin = get_object_or_404(Admin, id=id)
        serializer = AdminSerializer(admin, data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response({
                "status": "success",
                "code": 200,
                "message": "Admin updated successfully",
                "data": serializer.data
            })

        return Response({
            "status": "failed",
            "code": 400,
            "errors": serializer.errors
        })

    @swagger_auto_schema(
        tags=['admins']
    )
    def delete(self, request, id):
        admin = get_object_or_404(Admin, id=id)
        admin.delete()

        return Response({
            "status": "success",
            "code": 200,
            "message": "Admin deleted successfully"
        })
    
from rest_framework.views import APIView

class UserView(APIView):

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)

        return Response({
            "status": "success",
            "code": 200,
            "message": "All users fetched successfully",
            "data": serializer.data
        })
    
@swagger_auto_schema(
    method='post',
    request_body=UserSerializer,
    tags=['users']
)
@api_view(['POST'])
def register_user(request):

    serializer = UserSerializer(data=request.data)

    if serializer.is_valid():

        serializer.save()

        return Response({
            "status": "success",
            "code": 201,
            "message": "User registered successfully",
            "data": serializer.data
        })

    return Response({
        "status": "failed",
        "code": 400,
        "errors": serializer.errors
    })

@swagger_auto_schema(
    method='put',
    request_body=UserSerializer,
    tags=['users']
)
@api_view(['PUT'])
def update_user(request, id):

    user = get_object_or_404(User, id=id)

    serializer = UserSerializer(user, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

        profile = UserProfile.objects.get(user=user)
        profile.mobile = request.data.get("mobile", profile.mobile)
        profile.role = request.data.get("role", profile.role)
        profile.save()

        return Response({
            "status": "success",
            "message": "User updated successfully",
            "data": serializer.data
        })

    return Response({
        "status": "failed",
        "errors": serializer.errors
    }, status=400)


@api_view(['DELETE'])
def delete_user(request, id):

    user = get_object_or_404(User, id=id)
    user.delete()

    return Response({
        "status": "success",
        "message": "User deleted successfully"
    })

@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['email', 'password'],
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING),
            'password': openapi.Schema(type=openapi.TYPE_STRING),
        },
    ),
    tags=['Login']
)

@api_view(['POST'])
def login(request):

    email = request.data.get("email")
    password = request.data.get("password")

    # Check Admin table first
    try:
        admin = Admin.objects.get(email=email, password=password)

        return Response({
            "status": "success",
            "message": "Admin Login Successful",
            "data": {
                "id": admin.id,
                "name": admin.name,
                "email": admin.email,
                "mobile": admin.mobile,
                "role": "Admin"
            }
        })

    except Admin.DoesNotExist:
        pass

    # Check User table
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({
            "status": "failed",
            "message": "Invalid Email or Password"
        }, status=401)

    user = authenticate(username=user.username, password=password)

    if user:
        profile = UserProfile.objects.get(user=user)

        return Response({
            "status": "success",
            "message": "User Login Successful",
            "data": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "mobile": profile.mobile,
                "role": profile.role
            }
        })

    return Response({
        "status": "failed",
        "message": "Invalid Email or Password"
    }, status=401)

    return Response({
        "status": "failed",
        "code": 400,
        "errors": serializer.errors
    })

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User

from .models import Cart, CartItem, Plant


@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['user_id', 'plant_id'],
        properties={
            'user_id': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description='User ID'
            ),
            'plant_id': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description='Plant ID'
            ),
            'quantity': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description='Quantity',
                default=1
            ),
        }
    ),
    tags=['cart']
)
@api_view(['POST'])
def add_to_cart(request):

    user_id = request.data.get('user_id')
    plant_id = request.data.get('plant_id')
    quantity = request.data.get('quantity', 1)

    if not user_id:
        return Response({
            "status": "failed",
            "message": "user_id is required"
        }, status=status.HTTP_400_BAD_REQUEST)

    if not plant_id:
        return Response({
            "status": "failed",
            "message": "plant_id is required"
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        quantity = int(quantity)

        if quantity <= 0:
            return Response({
                "status": "failed",
                "message": "quantity must be greater than 0"
            }, status=status.HTTP_400_BAD_REQUEST)

    except (ValueError, TypeError):
        return Response({
            "status": "failed",
            "message": "quantity must be a valid number"
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({
            "status": "failed",
            "message": "User not found"
        }, status=status.HTTP_404_NOT_FOUND)

    try:
        plant = Plant.objects.get(id=plant_id)
    except Plant.DoesNotExist:
        return Response({
            "status": "failed",
            "message": "Plant not found"
        }, status=status.HTTP_404_NOT_FOUND)

    cart, created = Cart.objects.get_or_create(user=user)

    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart,
        plant=plant,
        defaults={
            "quantity": quantity
        }
    )

    if not item_created:
        cart_item.quantity += quantity
        cart_item.save()

    return Response({
        "status": "success",
        "message": "Plant added to cart successfully",
        "cart_id": cart.id,
        "plant_id": plant.id,
        "plant_name": plant.name,
        "quantity": cart_item.quantity,
        "price": plant.price
    }, status=status.HTTP_201_CREATED)


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'user_id',
            openapi.IN_QUERY,
            description='User ID',
            type=openapi.TYPE_INTEGER,
            required=True
        )
    ],
    tags=['cart']
)
@api_view(['GET'])
def view_cart(request):

    user_id = request.GET.get('user_id')

    if not user_id:
        return Response({
            "status": "failed",
            "message": "user_id is required"
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({
            "status": "failed",
            "message": "User not found"
        }, status=status.HTTP_404_NOT_FOUND)

    cart, created = Cart.objects.get_or_create(user=user)

    items = []
    total_amount = 0

    for item in cart.items.all():

        item_total = item.plant.price * item.quantity
        total_amount += item_total

        items.append({
            "plant_id": item.plant.id,
            "plant_name": item.plant.name,
            "price": item.plant.price,
            "quantity": item.quantity,
            "item_total": item_total
        })

    return Response({
        "status": "success",
        "cart_id": cart.id,
        "user_id": user.id,
        "items": items,
        "total_amount": total_amount
    }, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='delete',
    manual_parameters=[
        openapi.Parameter(
            'user_id',
            openapi.IN_QUERY,
            description='User ID',
            type=openapi.TYPE_INTEGER,
            required=True
        ),
        openapi.Parameter(
            'plant_id',
            openapi.IN_QUERY,
            description='Plant ID',
            type=openapi.TYPE_INTEGER,
            required=True
        ),
    ],
    tags=['cart']
)
@api_view(['DELETE'])
def remove_from_cart(request):

    user_id = request.GET.get('user_id')
    plant_id = request.GET.get('plant_id')

    if not user_id:
        return Response(
            {
                "status": "failed",
                "message": "user_id is required"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    if not plant_id:
        return Response(
            {
                "status": "failed",
                "message": "plant_id is required"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        cart = Cart.objects.get(user_id=user_id)
    except Cart.DoesNotExist:
        return Response(
            {
                "status": "failed",
                "message": "Cart not found"
            },
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        cart_item = CartItem.objects.get(
            cart=cart,
            plant_id=plant_id
        )
    except CartItem.DoesNotExist:
        return Response(
            {
                "status": "failed",
                "message": "Plant not found in cart"
            },
            status=status.HTTP_404_NOT_FOUND
        )

    cart_item.delete()

    return Response(
        {
            "status": "success",
            "message": "Plant removed from cart successfully"
        },
        status=status.HTTP_200_OK
    )

@swagger_auto_schema(
    method='put',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['user_id', 'plant_id', 'quantity'],
        properties={
            'user_id': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description='User ID'
            ),
            'plant_id': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description='Plant ID'
            ),
            'quantity': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description='New quantity',
                minimum=1
            ),
        },
    ),
    tags=['cart']
)
@api_view(['PUT'])
def update_cart_quantity(request):

    user_id = request.data.get('user_id')
    plant_id = request.data.get('plant_id')
    quantity = request.data.get('quantity')

    if not user_id:
        return Response(
            {
                "status": "failed",
                "message": "user_id is required"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    if not plant_id:
        return Response(
            {
                "status": "failed",
                "message": "plant_id is required"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    if quantity is None:
        return Response(
            {
                "status": "failed",
                "message": "quantity is required"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        quantity = int(quantity)

        if quantity <= 0:
            return Response(
                {
                    "status": "failed",
                    "message": "quantity must be greater than 0"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    except (ValueError, TypeError):
        return Response(
            {
                "status": "failed",
                "message": "quantity must be a valid number"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        cart = Cart.objects.get(user_id=user_id)
    except Cart.DoesNotExist:
        return Response(
            {
                "status": "failed",
                "message": "Cart not found"
            },
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        cart_item = CartItem.objects.get(
            cart=cart,
            plant_id=plant_id
        )
    except CartItem.DoesNotExist:
        return Response(
            {
                "status": "failed",
                "message": "Plant not found in cart"
            },
            status=status.HTTP_404_NOT_FOUND
        )

    cart_item.quantity = quantity
    cart_item.save()

    item_total = cart_item.plant.price * cart_item.quantity

    return Response(
        {
            "status": "success",
            "message": "Cart quantity updated successfully",
            "cart_id": cart.id,
            "plant_id": cart_item.plant.id,
            "plant_name": cart_item.plant.name,
            "quantity": cart_item.quantity,
            "price": cart_item.plant.price,
            "item_total": item_total
        },
        status=status.HTTP_200_OK
    )

from .models import Wishlist, WishlistItem

@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['user_id', 'plant_id'],
        properties={
            'user_id': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description='User ID'
            ),
            'plant_id': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description='Plant ID'
            ),
        },
    ),
    tags=['wishlist']
)

@api_view(['POST'])
def add_to_wishlist(request):

    user_id = request.data.get('user_id')
    plant_id = request.data.get('plant_id')

    if not user_id:
        return Response(
            {
                "status": "failed",
                "message": "user_id is required"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    if not plant_id:
        return Response(
            {
                "status": "failed",
                "message": "plant_id is required"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {
                "status": "failed",
                "message": "User not found"
            },
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        plant = Plant.objects.get(id=plant_id)
    except Plant.DoesNotExist:
        return Response(
            {
                "status": "failed",
                "message": "Plant not found"
            },
            status=status.HTTP_404_NOT_FOUND
        )

    wishlist, created = Wishlist.objects.get_or_create(user=user)

    wishlist_item, item_created = WishlistItem.objects.get_or_create(
        wishlist=wishlist,
        plant=plant
    )

    if not item_created:
        return Response(
            {
                "status": "failed",
                "message": "Plant already exists in wishlist"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    return Response(
        {
            "status": "success",
            "message": "Plant added to wishlist successfully",
            "wishlist_id": wishlist.id,
            "plant_id": plant.id,
            "plant_name": plant.name,
            "price": plant.price
        },
        status=status.HTTP_201_CREATED
    )

@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'user_id',
            openapi.IN_QUERY,
            description='User ID',
            type=openapi.TYPE_INTEGER,
            required=True
        )
    ],
    tags=['wishlist']
)

@api_view(['GET'])
def view_wishlist(request):

    user_id = request.GET.get('user_id')

    if not user_id:
        return Response(
            {
                "status": "failed",
                "message": "user_id is required"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {
                "status": "failed",
                "message": "User not found"
            },
            status=status.HTTP_404_NOT_FOUND
        )

    wishlist, created = Wishlist.objects.get_or_create(user=user)

    items = []

    for item in wishlist.items.all():
        items.append(
            {
                "plant_id": item.plant.id,
                "plant_name": item.plant.name,
                "price": item.plant.price,
                "created_at": item.created_at
            }
        )

    return Response(
        {
            "status": "success",
            "wishlist_id": wishlist.id,
            "user_id": user.id,
            "items": items
        },
        status=status.HTTP_200_OK
    )

@swagger_auto_schema(
    method='delete',
    manual_parameters=[
        openapi.Parameter(
            'user_id',
            openapi.IN_QUERY,
            description='User ID',
            type=openapi.TYPE_INTEGER,
            required=True
        ),
        openapi.Parameter(
            'plant_id',
            openapi.IN_QUERY,
            description='Plant ID',
            type=openapi.TYPE_INTEGER,
            required=True
        ),
    ],
    tags=['wishlist']
)
@api_view(['DELETE'])
def remove_from_wishlist(request):

    user_id = request.GET.get('user_id')
    plant_id = request.GET.get('plant_id')

    if not user_id:
        return Response(
            {
                "status": "failed",
                "message": "user_id is required"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    if not plant_id:
        return Response(
            {
                "status": "failed",
                "message": "plant_id is required"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        wishlist = Wishlist.objects.get(user_id=user_id)
    except Wishlist.DoesNotExist:
        return Response(
            {
                "status": "failed",
                "message": "Wishlist not found"
            },
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        wishlist_item = WishlistItem.objects.get(
            wishlist=wishlist,
            plant_id=plant_id
        )
    except WishlistItem.DoesNotExist:
        return Response(
            {
                "status": "failed",
                "message": "Plant not found in wishlist"
            },
            status=status.HTTP_404_NOT_FOUND
        )

    wishlist_item.delete()

    return Response(
        {
            "status": "success",
            "message": "Plant removed from wishlist successfully"
        },
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
def track_order_api(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id
    )

    return Response({
        "order_id": order.id,
        "status": order.status,
        "status_display": order.get_status_display(),
        "order_date": order.date,
        "expected_delivery": order.expected_delivery,
        "shipping_address": order.shipping_address,

        "tracking": [
            {
                "name": "Order Placed",
                "completed": True
            },
            {
                "name": "Packed",
                "completed": order.status in [
                    'PACKED',
                    'SHIPPED',
                    'DELIVERED'
                ]
            },
            {
                "name": "Shipped",
                "completed": order.status in [
                    'SHIPPED',
                    'DELIVERED'
                ]
            },
            {
                "name": "Delivered",
                "completed": order.status == 'DELIVERED'
            }
        ]
    })

@api_view(['POST'])
def cancel_order_api(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id
    )

    if order.status in ['SHIPPED', 'DELIVERED']:
        return Response(
            {
                "message": "Order cannot be cancelled after shipping."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    if order.status == 'CANCELLED':
        return Response(
            {
                "message": "Order is already cancelled."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    order.status = 'CANCELLED'
    order.cancelled_at = timezone.now()
    order.save()

    return Response({
        "message": "Order cancelled successfully.",
        "order_id": order.id,
        "status": order.status
    })

@api_view(['POST'])
def order_again_api(request, order_id):

    old_order = get_object_or_404(
        Order,
        id=order_id
    )

    new_order = Order.objects.create(
        customer=old_order.customer,
        shipping_address=old_order.shipping_address,
        expected_delivery=timezone.now().date() + timedelta(days=5),
        status='ORDER_PLACED',
        total_amount=0
    )

    total = 0

    for old_item in OrderItem.objects.filter(order=old_order):

        if old_item.plant.quantity < old_item.quantity:
            new_order.delete()

            return Response(
                {
                    "message": f"Not enough stock for {old_item.plant.name}."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        OrderItem.objects.create(
            order=new_order,
            plant=old_item.plant,
            quantity=old_item.quantity,
            price=old_item.plant.price * old_item.quantity
        )

        old_item.plant.quantity -= old_item.quantity
        old_item.plant.save()

        total += old_item.plant.price * old_item.quantity

    new_order.total_amount = total
    new_order.save()

    return Response({
        "message": "Order placed again successfully.",
        "old_order_id": old_order.id,
        "new_order_id": new_order.id,
        "total_amount": total,
        "status": new_order.status
    })

@api_view(['GET'])
def download_invoice_api(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id
    )

    response = HttpResponse(
        content_type='application/pdf'
    )

    response[
        'Content-Disposition'
    ] = f'attachment; filename="invoice_order_{order.id}.pdf"'

    pdf = canvas.Canvas(response)

    pdf.setTitle(
        f"Invoice Order {order.id}"
    )

    # Header
    pdf.setFont("Helvetica-Bold", 20)

    pdf.drawString(
        50,
        800,
        "NurseryKart"
    )

    pdf.setFont("Helvetica", 11)

    pdf.drawString(
        50,
        780,
        "Plants to Brighten Every Space"
    )

    # Invoice details
    pdf.setFont("Helvetica-Bold", 14)

    pdf.drawString(
        50,
        740,
        f"Invoice - Order #{order.id}"
    )

    pdf.setFont("Helvetica", 11)

    pdf.drawString(
        50,
        715,
        f"Customer: {order.customer.name}"
    )

    pdf.drawString(
        50,
        695,
        f"Email: {order.customer.email or 'N/A'}"
    )

    pdf.drawString(
        50,
        675,
        f"Order Date: {order.date}"
    )

    pdf.drawString(
        50,
        655,
        f"Status: {order.get_status_display()}"
    )

    # Shipping address
    pdf.drawString(
        50,
        625,
        "Shipping Address:"
    )

    pdf.drawString(
        50,
        605,
        order.shipping_address or "N/A"
    )

    # Table heading
    y = 560

    pdf.setFont(
        "Helvetica-Bold",
        11
    )

    pdf.drawString(50, y, "Plant")
    pdf.drawString(280, y, "Quantity")
    pdf.drawString(380, y, "Price")

    y -= 25

    pdf.setFont(
        "Helvetica",
        11
    )

    items = OrderItem.objects.filter(
        order=order
    )

    for item in items:

        pdf.drawString(
            50,
            y,
            item.plant.name
        )

        pdf.drawString(
            280,
            y,
            str(item.quantity)
        )

        pdf.drawString(
            380,
            y,
            f"Rs. {item.price:.2f}"
        )

        y -= 25

    # Total
    y -= 20

    pdf.setFont(
        "Helvetica-Bold",
        13
    )

    pdf.drawString(
        280,
        y,
        "Total:"
    )

    pdf.drawString(
        380,
        y,
        f"Rs. {order.total_amount:.2f}"
    )

    pdf.save()

    return response

@api_view(['POST'])
def rate_order_api(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id
    )

    if order.status != 'DELIVERED':
        return Response(
            {
                "message": "You can rate an order only after it is delivered."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    rating = request.data.get('rating')
    review = request.data.get('review', '')

    if not rating:
        return Response(
            {
                "message": "Rating is required."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        rating = int(rating)
    except ValueError:
        return Response(
            {
                "message": "Rating must be a number."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    if rating < 1 or rating > 5:
        return Response(
            {
                "message": "Rating must be between 1 and 5."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    OrderRating.objects.update_or_create(
        order=order,
        defaults={
            'customer': order.customer,
            'rating': rating,
            'review': review
        }
    )

    return Response({
        "message": "Thank you for rating your order!",
        "order_id": order.id,
        "rating": rating,
        "review": review
    })


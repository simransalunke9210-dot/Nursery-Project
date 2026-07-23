from django.shortcuts import render, redirect, get_object_or_404
from .models import Plant, Pot, Customer, Order, OrderItem, Fertilizer, Admin
from .forms import PlantForm, PotForm

from django.contrib.auth import authenticate
from .models import UserProfile

from django.http import HttpResponse

from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response 
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import PlantSerializer, PotSerializer, CustomerSerializer, OrderSerializer, OrderItemSerializer, FertilizerSerializer, UserSerializer, AdminSerializer, AdminLoginSerializer
from django.contrib.auth.models import User
from rest_framework import status

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
    request_body=PlantSerializer,
    tags=['plant']
)
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def add_plant_api(request):

    serializer = PlantSerializer(data=request.data)

    if serializer.is_valid():

        serializer.save()

        return Response({
    "status": "success",
    "code": 200,
    "message": "Plant added successfully",
    "data": serializer.data
})

    return Response({
    "status": "failed",
    "code": 400,
    "message": "Validation error",
    "errors": serializer.errors
})

@swagger_auto_schema(
    method='put',
    request_body=PlantSerializer,
    tags=['plant']
)
@api_view(['PUT'])
def update_plant_api(request, id):

    plant = Plant.objects.get(id=id)

    serializer = PlantSerializer(
        plant,
        data=request.data
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
    })

@swagger_auto_schema(
    method='delete',
    tags=['plant']
)
@api_view(['DELETE'])
def delete_plant_api(request, id):

    plant = Plant.objects.get(id=id)

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

@api_view(['DELETE'])
def delete_pot_api(request, id):

    pot = Pot.objects.get(id=id)

    pot.delete()

    return Response({
        "status": "success",
        "code": 200,
        "message": "Pot deleted successfully"
    })

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

@api_view(['DELETE'])
def delete_customer_api(request, id):

    customer = Customer.objects.get(id=id)

    customer.delete()

    return Response({
        "status": "success",
        "code": 200,
        "message": "Customer deleted successfully"
    })

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

@api_view(['DELETE'])
def delete_order_api(request, id):

    order = Order.objects.get(id=id)

    order.delete()

    return Response({
        "status": "success",
        "code": 200,
        "message": "Order deleted successfully"
    })

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

        user = serializer.save()

        UserProfile.objects.create(
            user=user,
            mobile=request.data.get("mobile"),
            role=request.data.get("role")
        )

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


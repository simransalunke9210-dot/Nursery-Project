from django.shortcuts import render, redirect, get_object_or_404
from .models import Plant, Pot, Customer, Order, OrderItem, Fertilizer, Admin, PlantImage, PotImage, FertilizerImage, OrderRating,Settings
from .forms import PlantForm, PotForm
from .permissions import IsAdminUser
from django.contrib.auth import authenticate
from .models import UserProfile
from django.db import transaction

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response 
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import PlantSerializer, PotSerializer, CustomerSerializer, OrderSerializer, OrderItemSerializer, FertilizerSerializer, UserSerializer, AdminSerializer, AdminLoginSerializer,ReportSerializer,SettingsSerializer
from django.contrib.auth.models import User
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import api_view,permission_classes
from reportlab.pdfgen import canvas
from django.db.models import Sum, Count, Avg
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    message = "Only admin users can access this API."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        try:
            profile = UserProfile.objects.get(user=request.user)
            return profile.role == "Admin"
        except UserProfile.DoesNotExist:
            return False

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
@permission_classes([AllowAny])
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
@permission_classes([IsAdminUser])
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
@permission_classes([IsAdminUser])
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
@permission_classes([IsAdminUser])
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
    tags=['Pots']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_pots(request):

    pots = Pot.objects.all()

    serializer = PotSerializer(
        pots,
        many=True,
        context={'request': request}
    )

    return Response({
        "status": "success",
        "code": 200,
        "message": "All pots fetched",
        "data": serializer.data
    })


@swagger_auto_schema(
    method='post',
    tags=['Pots'],
    manual_parameters=[
        openapi.Parameter(
            'name',
            openapi.IN_FORM,
            type=openapi.TYPE_STRING,
            required=True
        ),
        openapi.Parameter(
            'category',
            openapi.IN_FORM,
            type=openapi.TYPE_STRING,
            required=True
        ),
        openapi.Parameter(
            'price',
            openapi.IN_FORM,
            type=openapi.TYPE_NUMBER,
            required=True
        ),
        openapi.Parameter(
            'stock',
            openapi.IN_FORM,
            type=openapi.TYPE_INTEGER,
            required=True
        ),
        openapi.Parameter(
            'description',
            openapi.IN_FORM,
            type=openapi.TYPE_STRING,
            required=True
        ),
        openapi.Parameter(
            'image1',
            openapi.IN_FORM,
            type=openapi.TYPE_FILE,
            required=True
        ),
        openapi.Parameter(
            'image2',
            openapi.IN_FORM,
            type=openapi.TYPE_FILE,
            required=False
        ),
        openapi.Parameter(
            'image3',
            openapi.IN_FORM,
            type=openapi.TYPE_FILE,
            required=False
        ),
    ],
    consumes=['multipart/form-data']
)
@api_view(['POST'])
@permission_classes([IsAdminUser])
@parser_classes([MultiPartParser, FormParser])
def add_pot_api(request):

    pot_data = {
        'name': request.data.get('name'),
        'category': request.data.get('category'),
        'price': request.data.get('price'),
        'stock': request.data.get('stock'),
        'description': request.data.get('description'),
    }

    serializer = PotSerializer(
        data=pot_data,
        context={'request': request}
    )

    if not serializer.is_valid():

        return Response({
            "status": "failed",
            "code": 400,
            "message": "Pot addition failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    pot = serializer.save()

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

    # At least one image
    if len(images) == 0:

        pot.delete()

        return Response({
            "status": "failed",
            "code": 400,
            "message": "At least one image is required"
        }, status=status.HTTP_400_BAD_REQUEST)

    # Maximum 3 images
    if len(images) > 3:

        pot.delete()

        return Response({
            "status": "failed",
            "code": 400,
            "message": "Maximum 3 images are allowed"
        }, status=status.HTTP_400_BAD_REQUEST)

    # Save images
    for image in images:

        PotImage.objects.create(
            pot=pot,
            image=image
        )

    return Response({
        "status": "success",
        "code": 201,
        "message": "Pot added successfully",
        "data": PotSerializer(
            pot,
            context={'request': request}
        ).data
    }, status=status.HTTP_201_CREATED)


@swagger_auto_schema(
    method='put',
    tags=['Pots'],
    manual_parameters=[
        openapi.Parameter(
            'name',
            openapi.IN_FORM,
            type=openapi.TYPE_STRING,
            required=False
        ),
        openapi.Parameter(
            'category',
            openapi.IN_FORM,
            type=openapi.TYPE_STRING,
            required=False
        ),
        openapi.Parameter(
            'price',
            openapi.IN_FORM,
            type=openapi.TYPE_NUMBER,
            required=False
        ),
        openapi.Parameter(
            'stock',
            openapi.IN_FORM,
            type=openapi.TYPE_INTEGER,
            required=False
        ),
        openapi.Parameter(
            'description',
            openapi.IN_FORM,
            type=openapi.TYPE_STRING,
            required=False
        ),
        openapi.Parameter(
            'image1',
            openapi.IN_FORM,
            type=openapi.TYPE_FILE,
            required=False
        ),
        openapi.Parameter(
            'image2',
            openapi.IN_FORM,
            type=openapi.TYPE_FILE,
            required=False
        ),
        openapi.Parameter(
            'image3',
            openapi.IN_FORM,
            type=openapi.TYPE_FILE,
            required=False
        ),
    ],
    consumes=['multipart/form-data']
)
@api_view(['PUT'])
@permission_classes([IsAdminUser])
@parser_classes([MultiPartParser, FormParser])
def update_pot_api(request, id):

    pot = get_object_or_404(Pot, id=id)

    pot_data = {
        'name': request.data.get('name', pot.name),
        'category': request.data.get('category', pot.category),
        'price': request.data.get('price', pot.price),
        'stock': request.data.get('stock', pot.stock),
        'description': request.data.get(
            'description',
            pot.description
        ),
    }

    serializer = PotSerializer(
        pot,
        data=pot_data,
        partial=True,
        context={'request': request}
    )

    if not serializer.is_valid():

        return Response({
            "status": "failed",
            "code": 400,
            "message": "Pot update failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    pot = serializer.save()

    # If new images are sent, replace old images
    new_images = []

    for field in ['image1', 'image2', 'image3']:

        image = request.FILES.get(field)

        if image:
            new_images.append(image)

    if new_images:

        # Delete old images
        pot.pot_images.all().delete()

        # Save new images
        for image in new_images:

            PotImage.objects.create(
                pot=pot,
                image=image
            )

    return Response({
        "status": "success",
        "code": 200,
        "message": "Pot updated successfully",
        "data": PotSerializer(
            pot,
            context={'request': request}
        ).data
    })


@swagger_auto_schema(
    method='delete',
    tags=['Pots']
)
@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_pot_api(request, id):

    pot = get_object_or_404(Pot, id=id)

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
@permission_classes([IsAdminUser])
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
@permission_classes([IsAuthenticated])
def add_order_api(request):

    user = request.user

    # Find Customer using the logged-in Django user's email
    customer = Customer.objects.filter(
        email__iexact=user.email
    ).first()

    # If Customer does not exist, create one automatically
    if not customer:

        mobile = ''

        # Get mobile from UserProfile if available
        try:
            mobile = user.userprofile.mobile
        except UserProfile.DoesNotExist:
            mobile = ''

        customer = Customer.objects.create(
            name=user.get_full_name() or user.username,
            phone=mobile,
            email=user.email,
            role='Customer'
        )

    data = request.data.copy()

    # Never accept customer or total_amount from frontend
    data.pop('customer', None)
    data.pop('total_amount', None)

    serializer = OrderSerializer(data=data)

    if serializer.is_valid():

        order = serializer.save(
            customer=customer,
            total_amount=0
        )

        return Response(
            {
                "status": "success",
                "code": 201,
                "message": "Order added successfully",
                "data": OrderSerializer(order).data
            },
            status=status.HTTP_201_CREATED
        )

    return Response(
        {
            "status": "failed",
            "code": 400,
            "errors": serializer.errors
        },
        status=status.HTTP_400_BAD_REQUEST
    )

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
    request_body=OrderItemSerializer,
    tags=['Order Items']
)
@api_view(['POST'])
def add_order_item_api(request):

    serializer = OrderItemSerializer(data=request.data)

    if serializer.is_valid():

        order_item = serializer.save()

        return Response({
            "status": "success",
            "code": 201,
            "message": "Order item added successfully",
            "data": OrderItemSerializer(order_item).data,
            "order_total": order_item.order.total_amount
        }, status=201)

    return Response({
        "status": "failed",
        "code": 400,
        "errors": serializer.errors
    }, status=400)

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
class FertilizerListView(APIView):

    permission_classes = [AllowAny]

    @swagger_auto_schema(
        tags=['fertilizer']
    )
    def get(self, request):

        fertilizers = Fertilizer.objects.all()

        serializer = FertilizerSerializer(
            fertilizers,
            many=True,
            context={'request': request}
        )

        return Response({
            "status": "success",
            "code": 200,
            "message": "All fertilizers fetched",
            "data": serializer.data
        })


class FertilizerAddView(APIView):
    @permission_classes([IsAdminUser])

    @swagger_auto_schema(
        tags=['fertilizer'],
        manual_parameters=[
            openapi.Parameter(
                'name',
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'price',
                openapi.IN_FORM,
                type=openapi.TYPE_NUMBER,
                required=True
            ),
            openapi.Parameter(
                'quantity',
                openapi.IN_FORM,
                type=openapi.TYPE_INTEGER,
                required=True
            ),
            openapi.Parameter(
                'description',
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'image1',
                openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True
            ),
            openapi.Parameter(
                'image2',
                openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=False
            ),
            openapi.Parameter(
                'image3',
                openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=False
            ),
        ],
        consumes=['multipart/form-data']
    )
    def post(self, request):

        fertilizer_data = {
            'name': request.data.get('name'),
            'price': request.data.get('price'),
            'quantity': request.data.get('quantity'),
            'description': request.data.get('description'),
        }

        serializer = FertilizerSerializer(
            data=fertilizer_data,
            context={'request': request}
        )

        if not serializer.is_valid():

            return Response({
                "status": "failed",
                "code": 400,
                "message": "Fertilizer addition failed",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        fertilizer = serializer.save()

        # Get images
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

        # At least one image
        if len(images) == 0:

            fertilizer.delete()

            return Response({
                "status": "failed",
                "code": 400,
                "message": "At least one image is required"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Maximum 3 images
        if len(images) > 3:

            fertilizer.delete()

            return Response({
                "status": "failed",
                "code": 400,
                "message": "Maximum 3 images are allowed"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Save images
        for image in images:

            FertilizerImage.objects.create(
                fertilizer=fertilizer,
                image=image
            )

        return Response({
            "status": "success",
            "code": 201,
            "message": "Fertilizer added successfully",
            "data": FertilizerSerializer(
                fertilizer,
                context={'request': request}
            ).data
        }, status=status.HTTP_201_CREATED)


class FertilizerUpdateView(APIView):
    @permission_classes([IsAdminUser])

    @swagger_auto_schema(
        tags=['fertilizer'],
        manual_parameters=[
            openapi.Parameter(
                'name',
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'price',
                openapi.IN_FORM,
                type=openapi.TYPE_NUMBER,
                required=False
            ),
            openapi.Parameter(
                'quantity',
                openapi.IN_FORM,
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                'description',
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'image1',
                openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=False
            ),
            openapi.Parameter(
                'image2',
                openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=False
            ),
            openapi.Parameter(
                'image3',
                openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=False
            ),
        ],
        consumes=['multipart/form-data']
    )
    def put(self, request, id):

        fertilizer = get_object_or_404(
            Fertilizer,
            id=id
        )

        fertilizer_data = {
            'name': request.data.get(
                'name',
                fertilizer.name
            ),
            'price': request.data.get(
                'price',
                fertilizer.price
            ),
            'quantity': request.data.get(
                'quantity',
                fertilizer.quantity
            ),
            'description': request.data.get(
                'description',
                fertilizer.description
            ),
        }

        serializer = FertilizerSerializer(
            fertilizer,
            data=fertilizer_data,
            partial=True,
            context={'request': request}
        )

        if not serializer.is_valid():

            return Response({
                "status": "failed",
                "code": 400,
                "message": "Fertilizer update failed",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        fertilizer = serializer.save()

        # Check whether new images were uploaded
        new_images = []

        for field in ['image1', 'image2', 'image3']:

            image = request.FILES.get(field)

            if image:
                new_images.append(image)

        if new_images:

            # Remove old images
            fertilizer.fertilizer_images.all().delete()

            # Save new images
            for image in new_images:

                FertilizerImage.objects.create(
                    fertilizer=fertilizer,
                    image=image
                )

        return Response({
            "status": "success",
            "code": 200,
            "message": "Fertilizer updated successfully",
            "data": FertilizerSerializer(
                fertilizer,
                context={'request': request}
            ).data
        })


class FertilizerDeleteView(APIView):
    @permission_classes([IsAdminUser])

    @swagger_auto_schema(
        tags=['fertilizer']
    )
    def delete(self, request, id):

        fertilizer = get_object_or_404(
            Fertilizer,
            id=id
        )

        fertilizer.delete()

        return Response({
            "status": "success",
            "code": 200,
            "message": "Fertilizer deleted successfully"
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

    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        request_body=AdminSerializer,
        tags=['admins']
    )
    def put(self, request, id):

        admin = get_object_or_404(Admin, id=id)

        # Find the Django User connected to this Admin
        try:
            admin_user = User.objects.get(email=admin.email)
        except User.DoesNotExist:
            return Response({
                "status": "failed",
                "code": 404,
                "message": "Django User account not found for this admin"
            }, status=status.HTTP_404_NOT_FOUND)

        # Find UserProfile
        try:
            profile = UserProfile.objects.get(user=admin_user)
        except UserProfile.DoesNotExist:
            return Response({
                "status": "failed",
                "code": 404,
                "message": "UserProfile not found for this admin"
            }, status=status.HTTP_404_NOT_FOUND)

        # Get updated values
        name = request.data.get("name", admin.name)
        email = request.data.get("email", admin.email)
        mobile = request.data.get("mobile", admin.mobile)
        role = request.data.get("role", admin.role)
        password = request.data.get("password")

        # Check duplicate email
        if email != admin.email:

            if Admin.objects.filter(email=email).exclude(
                id=admin.id
            ).exists():

                return Response({
                    "status": "failed",
                    "code": 400,
                    "message": "Admin with this email already exists"
                }, status=status.HTTP_400_BAD_REQUEST)

            if User.objects.filter(email=email).exclude(
                id=admin_user.id
            ).exists():

                return Response({
                    "status": "failed",
                    "code": 400,
                    "message": "User with this email already exists"
                }, status=status.HTTP_400_BAD_REQUEST)

        try:

            # -----------------------------
            # Update Admin table
            # -----------------------------

            admin.name = name
            admin.email = email
            admin.mobile = mobile
            admin.role = role

            if password:
                admin.password = password

            admin.save()

            # -----------------------------
            # Update Django User
            # -----------------------------

            admin_user.username = email
            admin_user.email = email

            if password:
                admin_user.set_password(password)

            admin_user.save()

            # -----------------------------
            # Update UserProfile
            # -----------------------------

            profile.mobile = mobile
            profile.role = role
            profile.save()

            return Response({
                "status": "success",
                "code": 200,
                "message": "Admin updated successfully",
                "data": {
                    "id": admin.id,
                    "name": admin.name,
                    "email": admin.email,
                    "mobile": admin.mobile,
                    "role": admin.role
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:

            return Response({
                "status": "failed",
                "code": 400,
                "message": "Admin update failed",
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


    @swagger_auto_schema(
        tags=['admins']
    )
    def delete(self, request, id):

        admin = get_object_or_404(Admin, id=id)

        # Find corresponding Django User
        try:
            admin_user = User.objects.get(email=admin.email)
        except User.DoesNotExist:
            admin_user = None

        # Delete Admin
        admin.delete()

        # Delete corresponding Django User
        if admin_user:
            admin_user.delete()

        return Response({
            "status": "success",
            "code": 200,
            "message": "Admin deleted successfully"
        }, status=status.HTTP_200_OK)



from rest_framework.views import APIView

class UserView(APIView):
    permission_classes = [AllowAny]
    
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
    tags=['Users']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):

    serializer = UserSerializer(data=request.data)

    if serializer.is_valid():

        try:

            user = serializer.save()

            return Response({
                "status": "success",
                "message": "User registered successfully",

                "data": {
                    "id": user.id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email
                }

            }, status=status.HTTP_201_CREATED)

        except Exception as e:

            return Response({
                "status": "failed",
                "message": "Failed to create account",
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    return Response({

        "status": "failed",
        "message": "Registration failed",
        "errors": serializer.errors

    }, status=status.HTTP_400_BAD_REQUEST)


from .serializers import ProfileUpdateSerializer

@swagger_auto_schema(
    method='put',
    request_body=ProfileUpdateSerializer,
    tags=['users']
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user(request, id):

    # Get user
    user = get_object_or_404(User, id=id)

    # User can update only their own profile
    if request.user.id != user.id:
        return Response(
            {
                "status": "failed",
                "code": 403,
                "message": "You can update only your own profile"
            },
            status=status.HTTP_403_FORBIDDEN
        )

    # Profile Update Serializer
    serializer = ProfileUpdateSerializer(
        instance=user,
        data=request.data,
        partial=True
    )

    # Validate
    if not serializer.is_valid():
        return Response(
            {
                "status": "failed",
                "code": 400,
                "message": "Profile update failed",
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Save
    serializer.save()

    # Success Response
    return Response(
        {
            "status": "success",
            "code": 200,
            "message": "User profile updated successfully",
            "data": serializer.data
        },
        status=status.HTTP_200_OK
    )


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
            'email': openapi.Schema(
                type=openapi.TYPE_STRING
            ),
            'password': openapi.Schema(
                type=openapi.TYPE_STRING
            ),
        },
    ),
    tags=['Login']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):

    email = request.data.get("email")
    password = request.data.get("password")

    # -----------------------------------
    # VALIDATE INPUT
    # -----------------------------------

    if not email or not password:

        return Response(
            {
                "status": "failed",
                "message": "Email and password are required"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # -----------------------------------
    # ADMIN LOGIN
    # -----------------------------------

    try:

        admin = Admin.objects.get(
            email=email,
            password=password
        )

        # Find corresponding Django User
        try:

            admin_user = User.objects.get(
                email=email
            )

        except User.DoesNotExist:

            return Response(
                {
                    "status": "failed",
                    "message": "Admin account is not linked with a Django User account"
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Create JWT tokens
        refresh = RefreshToken.for_user(admin_user)

        return Response(
            {
                "status": "success",
                "message": "Admin Login Successful",

                "data": {
                    "id": admin.id,
                    "name": admin.name,
                    "email": admin.email,
                    "mobile": admin.mobile,
                    "role": "Admin"
                },

                "access": str(refresh.access_token),
                "refresh": str(refresh)
            },
            status=status.HTTP_200_OK
        )

    except Admin.DoesNotExist:
        pass

    # -----------------------------------
    # CUSTOMER / USER LOGIN
    # -----------------------------------

    try:

        user = User.objects.get(
            email=email
        )

    except User.DoesNotExist:

        return Response(
            {
                "status": "failed",
                "message": "Invalid Email or Password"
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

    # -----------------------------------
    # CHECK PASSWORD
    # -----------------------------------

    authenticated_user = authenticate(
        username=user.username,
        password=password
    )

    if authenticated_user is None:

        return Response(
            {
                "status": "failed",
                "message": "Invalid Email or Password"
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Use authenticated user
    user = authenticated_user

    # -----------------------------------
    # GET OR CREATE USER PROFILE
    # -----------------------------------

    profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            "mobile": "",
            "role": "Customer"
        }
    )

    # -----------------------------------
    # CREATE JWT TOKENS
    # -----------------------------------

    refresh = RefreshToken.for_user(user)

    # -----------------------------------
    # SUCCESS RESPONSE
    # -----------------------------------

    return Response(
        {
            "status": "success",
            "message": "User Login Successful",

            "data": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "mobile": profile.mobile,
                "role": profile.role
            },

            "access": str(refresh.access_token),
            "refresh": str(refresh)
        },
        status=status.HTTP_200_OK
    )

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User

from .models import Cart, CartItem, Plant

def get_product(product_type, product_id):

    if product_type == 'plant':
        try:
            return Plant.objects.get(id=product_id)
        except Plant.DoesNotExist:
            return None

    elif product_type == 'pot':
        try:
            return Pot.objects.get(id=product_id)
        except Pot.DoesNotExist:
            return None

    elif product_type == 'fertilizer':
        try:
            return Fertilizer.objects.get(id=product_id)
        except Fertilizer.DoesNotExist:
            return None

    return None


@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['user_id', 'product_type', 'product_id'],
        properties={
            'user_id': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description='User ID'
            ),
            'product_type': openapi.Schema(
                type=openapi.TYPE_STRING,
                enum=['plant', 'pot', 'fertilizer'],
                description='Product type'
            ),
            'product_id': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description='Product ID'
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
    product_type = request.data.get('product_type')
    product_id = request.data.get('product_id')
    quantity = request.data.get('quantity', 1)

    if not user_id:
        return Response({
            "status": "failed",
            "message": "user_id is required"
        }, status=status.HTTP_400_BAD_REQUEST)

    if not product_type:
        return Response({
            "status": "failed",
            "message": "product_type is required"
        }, status=status.HTTP_400_BAD_REQUEST)

    if not product_id:
        return Response({
            "status": "failed",
            "message": "product_id is required"
        }, status=status.HTTP_400_BAD_REQUEST)

    if product_type not in ['plant', 'pot', 'fertilizer']:
        return Response({
            "status": "failed",
            "message": "Invalid product_type. Use plant, pot or fertilizer"
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

    product = get_product(product_type, product_id)

    if not product:
        return Response({
            "status": "failed",
            "message": f"{product_type.capitalize()} not found"
        }, status=status.HTTP_404_NOT_FOUND)

    cart, created = Cart.objects.get_or_create(user=user)

    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart,
        product_type=product_type,
        product_id=product_id,
        defaults={
            "quantity": quantity
        }
    )

    if not item_created:
        cart_item.quantity += quantity
        cart_item.save()

    return Response({
        "status": "success",
        "message": f"{product_type.capitalize()} added to cart successfully",
        "cart_id": cart.id,
        "product_type": product_type,
        "product_id": product.id,
        "product_name": product.name,
        "quantity": cart_item.quantity,
        "price": product.price
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

        product = get_product(
            item.product_type,
            item.product_id
        )

        if not product:
            continue

        item_total = product.price * item.quantity
        total_amount += item_total

        items.append({
            "product_type": item.product_type,
            "product_id": product.id,
            "product_name": product.name,
            "price": product.price,
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
            'product_type',
            openapi.IN_QUERY,
            description='Product type',
            type=openapi.TYPE_STRING,
            required=True
        ),
        openapi.Parameter(
            'product_id',
            openapi.IN_QUERY,
            description='Product ID',
            type=openapi.TYPE_INTEGER,
            required=True
        ),
    ],
    tags=['cart']
)
@api_view(['DELETE'])
def remove_from_cart(request):

    user_id = request.GET.get('user_id')
    product_type = request.GET.get('product_type')
    product_id = request.GET.get('product_id')

    if not user_id:
        return Response({
            "status": "failed",
            "message": "user_id is required"
        }, status=status.HTTP_400_BAD_REQUEST)

    if not product_type:
        return Response({
            "status": "failed",
            "message": "product_type is required"
        }, status=status.HTTP_400_BAD_REQUEST)

    if not product_id:
        return Response({
            "status": "failed",
            "message": "product_id is required"
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        cart = Cart.objects.get(user_id=user_id)
    except Cart.DoesNotExist:
        return Response({
            "status": "failed",
            "message": "Cart not found"
        }, status=status.HTTP_404_NOT_FOUND)

    try:
        cart_item = CartItem.objects.get(
            cart=cart,
            product_type=product_type,
            product_id=product_id
        )
    except CartItem.DoesNotExist:
        return Response({
            "status": "failed",
            "message": "Product not found in cart"
        }, status=status.HTTP_404_NOT_FOUND)

    cart_item.delete()

    return Response({
        "status": "success",
        "message": "Product removed from cart successfully"
    }, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='put',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=[
            'user_id',
            'product_type',
            'product_id',
            'quantity'
        ],
        properties={
            'user_id': openapi.Schema(
                type=openapi.TYPE_INTEGER
            ),
            'product_type': openapi.Schema(
                type=openapi.TYPE_STRING,
                enum=['plant', 'pot', 'fertilizer']
            ),
            'product_id': openapi.Schema(
                type=openapi.TYPE_INTEGER
            ),
            'quantity': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                minimum=1
            ),
        },
    ),
    tags=['cart']
)
@api_view(['PUT'])
def update_cart_quantity(request):

    user_id = request.data.get('user_id')
    product_type = request.data.get('product_type')
    product_id = request.data.get('product_id')
    quantity = request.data.get('quantity')

    if not user_id:
        return Response({
            "status": "failed",
            "message": "user_id is required"
        }, status=status.HTTP_400_BAD_REQUEST)

    if not product_type:
        return Response({
            "status": "failed",
            "message": "product_type is required"
        }, status=status.HTTP_400_BAD_REQUEST)

    if not product_id:
        return Response({
            "status": "failed",
            "message": "product_id is required"
        }, status=status.HTTP_400_BAD_REQUEST)

    if quantity is None:
        return Response({
            "status": "failed",
            "message": "quantity is required"
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
        cart = Cart.objects.get(user_id=user_id)
    except Cart.DoesNotExist:
        return Response({
            "status": "failed",
            "message": "Cart not found"
        }, status=status.HTTP_404_NOT_FOUND)

    try:
        cart_item = CartItem.objects.get(
            cart=cart,
            product_type=product_type,
            product_id=product_id
        )
    except CartItem.DoesNotExist:
        return Response({
            "status": "failed",
            "message": "Product not found in cart"
        }, status=status.HTTP_404_NOT_FOUND)

    product = get_product(product_type, product_id)

    if not product:
        return Response({
            "status": "failed",
            "message": "Product not found"
        }, status=status.HTTP_404_NOT_FOUND)

    cart_item.quantity = quantity
    cart_item.save()

    item_total = product.price * cart_item.quantity

    return Response({
        "status": "success",
        "message": "Cart quantity updated successfully",
        "cart_id": cart.id,
        "product_type": product_type,
        "product_id": product.id,
        "product_name": product.name,
        "quantity": cart_item.quantity,
        "price": product.price,
        "item_total": item_total
    }, status=status.HTTP_200_OK)

from .models import Wishlist, WishlistItem

@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['user_id', 'product_type', 'product_id'],
        properties={
            'user_id': openapi.Schema(
                type=openapi.TYPE_INTEGER
            ),
            'product_type': openapi.Schema(
                type=openapi.TYPE_STRING,
                enum=['plant', 'pot', 'fertilizer']
            ),
            'product_id': openapi.Schema(
                type=openapi.TYPE_INTEGER
            ),
        },
    ),
    tags=['wishlist']
)
@api_view(['POST'])
def add_to_wishlist(request):

    user_id = request.data.get('user_id')
    product_type = request.data.get('product_type')
    product_id = request.data.get('product_id')

    if not user_id:
        return Response({
            "status": "failed",
            "message": "user_id is required"
        }, status=status.HTTP_400_BAD_REQUEST)

    if not product_type:
        return Response({
            "status": "failed",
            "message": "product_type is required"
        }, status=status.HTTP_400_BAD_REQUEST)

    if not product_id:
        return Response({
            "status": "failed",
            "message": "product_id is required"
        }, status=status.HTTP_400_BAD_REQUEST)

    if product_type not in ['plant', 'pot', 'fertilizer']:
        return Response({
            "status": "failed",
            "message": "Invalid product_type. Use plant, pot or fertilizer"
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({
            "status": "failed",
            "message": "User not found"
        }, status=status.HTTP_404_NOT_FOUND)

    product = get_product(product_type, product_id)

    if not product:
        return Response({
            "status": "failed",
            "message": f"{product_type.capitalize()} not found"
        }, status=status.HTTP_404_NOT_FOUND)

    wishlist, created = Wishlist.objects.get_or_create(user=user)

    wishlist_item, item_created = WishlistItem.objects.get_or_create(
        wishlist=wishlist,
        product_type=product_type,
        product_id=product_id
    )

    if not item_created:
        return Response({
            "status": "failed",
            "message": "Product already exists in wishlist"
        }, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        "status": "success",
        "message": f"{product_type.capitalize()} added to wishlist successfully",
        "wishlist_id": wishlist.id,
        "product_type": product_type,
        "product_id": product.id,
        "product_name": product.name,
        "price": product.price
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
    tags=['wishlist']
)
@api_view(['GET'])
def view_wishlist(request):

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

    wishlist, created = Wishlist.objects.get_or_create(user=user)

    items = []

    for item in wishlist.items.all():

        product = get_product(
            item.product_type,
            item.product_id
        )

        if not product:
            continue

        items.append({
            "product_type": item.product_type,
            "product_id": product.id,
            "product_name": product.name,
            "price": product.price,
            "created_at": item.created_at
        })

    return Response({
        "status": "success",
        "wishlist_id": wishlist.id,
        "user_id": user.id,
        "items": items
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
            'product_type',
            openapi.IN_QUERY,
            description='Product type',
            type=openapi.TYPE_STRING,
            required=True
        ),
        openapi.Parameter(
            'product_id',
            openapi.IN_QUERY,
            description='Product ID',
            type=openapi.TYPE_INTEGER,
            required=True
        ),
    ],
    tags=['wishlist']
)
@api_view(['DELETE'])
def remove_from_wishlist(request):

    user_id = request.GET.get('user_id')
    product_type = request.GET.get('product_type')
    product_id = request.GET.get('product_id')

    if not user_id:
        return Response({
            "status": "failed",
            "message": "user_id is required"
        }, status=status.HTTP_400_BAD_REQUEST)

    if not product_type:
        return Response({
            "status": "failed",
            "message": "product_type is required"
        }, status=status.HTTP_400_BAD_REQUEST)

    if not product_id:
        return Response({
            "status": "failed",
            "message": "product_id is required"
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        wishlist = Wishlist.objects.get(user_id=user_id)
    except Wishlist.DoesNotExist:
        return Response({
            "status": "failed",
            "message": "Wishlist not found"
        }, status=status.HTTP_404_NOT_FOUND)

    try:
        wishlist_item = WishlistItem.objects.get(
            wishlist=wishlist,
            product_type=product_type,
            product_id=product_id
        )
    except WishlistItem.DoesNotExist:
        return Response({
            "status": "failed",
            "message": "Product not found in wishlist"
        }, status=status.HTTP_404_NOT_FOUND)

    wishlist_item.delete()

    return Response({
        "status": "success",
        "message": "Product removed from wishlist successfully"
    }, status=status.HTTP_200_OK)

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

class ReportsView(APIView):
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        tags=['reports']
    )
    def get(self, request):

        total_plants = Plant.objects.count()

        total_customers = Customer.objects.count()

        total_orders = Order.objects.count()

        total_revenue = Order.objects.aggregate(
            total=Sum('total_amount')
        )['total'] or 0

        pending_orders = Order.objects.filter(
            status='ORDER_PLACED'
        ).count()

        delivered_orders = Order.objects.filter(
            status='DELIVERED'
        ).count()

        cancelled_orders = Order.objects.filter(
            status='CANCELLED'
        ).count()

        total_items_sold = OrderItem.objects.aggregate(
            total=Sum('quantity')
        )['total'] or 0

        total_ratings = OrderRating.objects.count()

        average_rating = OrderRating.objects.aggregate(
            average=Avg('rating')
        )['average'] or 0

        data = {
            "total_plants": total_plants,
            "total_customers": total_customers,
            "total_orders": total_orders,
            "total_revenue": float(total_revenue),
            "pending_orders": pending_orders,
            "delivered_orders": delivered_orders,
            "cancelled_orders": cancelled_orders,
            "total_items_sold": total_items_sold,
            "total_ratings": total_ratings,
            "average_rating": round(float(average_rating), 2)
        }

        serializer = ReportSerializer(data=data)

        serializer.is_valid(raise_exception=True)

        return Response({
            "status": "success",
            "code": 200,
            "message": "Reports fetched successfully",
            "data": serializer.data
        })

class SettingsView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        tags=['settings']
    )
    def get(self, request):

        settings = Settings.objects.first()

        if not settings:
            settings = Settings.objects.create()

        serializer = SettingsSerializer(
            settings,
            context={'request': request}
        )

        return Response({
            "status": "success",
            "code": 200,
            "message": "Settings fetched successfully",
            "data": serializer.data
        })

    @swagger_auto_schema(
        request_body=SettingsSerializer,
        consumes=['multipart/form-data'],
        tags=['settings']
    )
    def put(self, request):

        settings = Settings.objects.first()

        if not settings:
            settings = Settings.objects.create()

        serializer = SettingsSerializer(
            settings,
            data=request.data,
            partial=True,
            context={'request': request}
        )

        if serializer.is_valid():

            serializer.save()

            return Response({
                "status": "success",
                "code": 200,
                "message": "Settings updated successfully",
                "data": serializer.data
            })

        return Response({
            "status": "failed",
            "code": 400,
            "message": "Settings update failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

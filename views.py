from django.shortcuts import render, redirect, get_object_or_404
from .models import Plant
from .forms import PlantForm
from django.http import HttpResponse

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import PlantSerializer

from rest_framework import status
from django.contrib.auth.models import User

from .models import Cart, CartItem, Plant
from .serializers import CartSerializer

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

@api_view(['POST'])
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

@api_view(['DELETE'])
def delete_plant_api(request, id):

    plant = Plant.objects.get(id=id)

    plant.delete()

    return Response({
    "status": "success",
    "code": 200,
    "message": "Plant deleted successfully"
})

# @api_view(['DELETE'])
# def delete_plant_api(request, id):

#     plant = Plant.objects.get(id=id)

#     plant.delete()

#     return Response({
#         "status": "success",
#         "code": 200,
#         "message": "Plant deleted successfully"
#     })

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

    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        return Response({
            "status": "failed",
            "message": "Quantity must be a number"
        }, status=status.HTTP_400_BAD_REQUEST)

    if quantity <= 0:
        return Response({
            "status": "failed",
            "message": "Quantity must be greater than 0"
        }, status=status.HTTP_400_BAD_REQUEST)

    if quantity > plant.quantity:
        return Response({
            "status": "failed",
            "message": "Requested quantity is not available"
        }, status=status.HTTP_400_BAD_REQUEST)

    cart, created = Cart.objects.get_or_create(user=user)

    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart,
        plant=plant,
        defaults={'quantity': quantity}
    )

    if not item_created:
        new_quantity = cart_item.quantity + quantity

        if new_quantity > plant.quantity:
            return Response({
                "status": "failed",
                "message": "Requested quantity is not available"
            }, status=status.HTTP_400_BAD_REQUEST)

        cart_item.quantity = new_quantity
        cart_item.save()

    return Response({
        "status": "success",
        "message": "Plant added to cart successfully",
        "data": CartSerializer(cart).data
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
def view_cart(request):

    user_id = request.query_params.get('user_id')

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

    return Response({
        "status": "success",
        "message": "Cart fetched successfully",
        "data": CartSerializer(cart).data
    }, status=status.HTTP_200_OK)
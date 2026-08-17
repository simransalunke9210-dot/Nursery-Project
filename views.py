from django.shortcuts import render, redirect, get_object_or_404
from .models import Plant, Pot, Fertilizer, Cart, CartItem
from .forms import PlantForm
from django.http import HttpResponse

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import PlantSerializer

from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from .serializers import CartSerializer
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




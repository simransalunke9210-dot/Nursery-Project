from django import forms
from .models import Plant, Pot

class PlantForm(forms.ModelForm):
    class Meta:
        model = Plant
        fields = ['name', 'category', 'price', 'quantity', 'image']


class PotForm(forms.ModelForm):
    class Meta:
        model = Pot
        fields = ['name', 'category', 'price', 'stock', 'description', 'image']
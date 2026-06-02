from django import forms
from .models import LeafImage


class LeafImageForm(forms.ModelForm):
    class Meta:
        model = LeafImage
        fields = ['image', 'temperature', 'humidity', 'moisture_content', 'notes']
        widgets = {
            'image': forms.ClearableFileInput(attrs={
                'accept': 'image/*',
                'class': 'form-control'
            }),
            'temperature': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 25',
                'step': '0.1'
            }),
            'humidity': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 60',
                'step': '0.1',
                'min': '0',
                'max': '100'
            }),
            'moisture_content': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 45',
                'step': '0.1',
                'min': '0',
                'max': '100'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional observations about the leaf...'
            }),
        }
        labels = {
            'temperature': 'Temperature (°C)',
            'humidity': 'Humidity (%)',
            'moisture_content': 'Soil Moisture Content (%)',
        }

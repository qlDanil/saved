from django import forms
from django.forms import Textarea
from django.forms.widgets import Input

from .models import Photo


class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['title', 'description', 'image', ]
        labels = {'title': 'Название', 'description': 'Описание', 'image': 'Картинка', }
        widgets = {
            'title': Input(
                attrs={'class': 'form-control', 'placeholder': 'Название'}),
            'description': Textarea(
                attrs={'class': 'form-control', 'placeholder': 'Описание картинки'})
        }

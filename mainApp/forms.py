from django import forms
from .models import Photo


class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['title', 'description', 'image',]
        labels = {'title': 'Название', 'description': 'Описание', 'image': 'Картинка', }
        widgets = {
            'title': forms.widgets.Input(
                attrs={'class': 'form-control', 'placeholder': 'Название'}),
            'description': forms.Textarea(
                attrs={'class': 'form-control', 'placeholder': 'Описание картинки'}),
            'image': forms.widgets.FileInput(
                attrs={'class': 'form-image'}
            )
        }

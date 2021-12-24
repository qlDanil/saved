from django import forms
from .models import Photo


class PhotoForm(forms.ModelForm):
    """Класс формы для добавления фотографии"""
    class Meta:
        model = Photo
        fields = ['title', 'description', 'image', ]
        labels = {'title': 'Title', 'description': 'Description', 'image': 'Image', }
        widgets = {
            'title': forms.widgets.Input(
                attrs={'class': 'form-control', 'placeholder': 'image name'}),
            'description': forms.Textarea(
                attrs={'class': 'form-control', 'placeholder': 'info about image'}),
            'image': forms.widgets.FileInput(
                attrs={'class': 'form-image', 'accept': 'image/*'}
            )
        }

    def __init__(self, *args, **kwargs):
        super(PhotoForm, self).__init__(*args, **kwargs)
        self.fields['image'].required = False

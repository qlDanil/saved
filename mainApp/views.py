from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Photo
from .forms import PhotoForm


@login_required
def main_window(request):
    photos = Photo.objects.filter(owner=request.user)
    count = Photo.objects.filter(owner=request.user).count()
    return render(request, 'mainApp/main.html', context={'photos': photos, 'count': count})


@login_required
def add_photo(request):
    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            title = form.cleaned_data['title']
            image = form.cleaned_data['image']
            owner = request.user
            new_photo = Photo.objects.create(title=title, image=image, owner=owner)
            new_photo.save()
            return HttpResponseRedirect(reverse('main_window'))
    else:
        form = PhotoForm()
    return render(request, 'mainApp/add_photo.html', {'form': form})

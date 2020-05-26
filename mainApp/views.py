import requests
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from .forms import PhotoForm
from .models import Photo, Hashtag
from social_django.models import UserSocialAuth
from django.db.models import Q
from .tasks import upload


@login_required
def main_window(request):
    """Отображение главной страницы с фотографиями и хештегами"""
    hashtags = request.GET.get('hashtag', 'all')
    search = request.GET.get('search', 'all')
    photos = Photo.objects.filter(owner=request.user)
    if not search == 'all':
        photos = photos.filter(Q(hashtags__tag__icontains=search) | Q(description__icontains=search))
    if not hashtags == 'all':
        hashtags = set(hashtags.split(' '))
        for hashtag in hashtags:
            photos = photos.filter(hashtags__tag=hashtag)
    count = photos.count()
    hashtag_count = Hashtag.objects.count()
    random_hashtags = []
    if hashtag_count > 0:
        counter = 0
        if not hashtags == 'all':
            for hashtag in hashtags:
                if Hashtag.objects.filter(tag=hashtag).exists():
                    random_hashtags.append(Hashtag.objects.get(tag=hashtag))
                    counter += 1
        while counter < min(hashtag_count, 10):
            random = Hashtag.objects.random()
            if random not in random_hashtags:
                random_hashtags.append(random)
                counter += 1
    if not hashtags == 'all':
        hashtags = ' '.join(hashtags) + ' '
    else:
        hashtags = ''
    print(hashtags)
    return render(request, 'mainApp/main.html',
                  context={'photos': photos.order_by('-date_time'), 'count': count,
                           'hashtags': sorted(random_hashtags, key=lambda hashtag: hashtag.tag),
                           'current_hashtags': hashtags})


@login_required
def detail_photo(request, pk):
    """Отображение страницы с детельной информацией об одной фотографии"""
    try:
        photo = Photo.objects.filter(owner=request.user).get(pk=pk)
    except Photo.DoesNotExist:
        raise Http404("Photo does not exist")

    return render(request, 'mainApp/photo_detail.html', context={'photo': photo})


@login_required
def add_photo(request):
    """Отображение страницы с формой для добавления новой фотографии"""
    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            image = form.cleaned_data['image']
            owner = request.user
            new_photo = Photo.objects.create(title=title, description=description, image=image, owner=owner)
            new_photo.save()
            hashtags = request.POST.getlist('hashtags[]')
            for hashtag in hashtags:
                if not Hashtag.objects.filter(tag=hashtag).exists():
                    new_hashtag = Hashtag.objects.create(tag=hashtag)
                    new_hashtag.save()
                hashtag_object = Hashtag.objects.get(tag=hashtag)
                new_photo.hashtags.add(hashtag_object)
            new_photo.save()
            return HttpResponseRedirect(reverse('main_window'))
    else:
        form = PhotoForm()
    return render(request, 'mainApp/add_photo.html', {'form': form})


@login_required
def edit_photo(request, pk):
    """Отображение страницы с формой для редактирования определенной фотографии"""
    try:
        photo = Photo.objects.filter(owner=request.user).get(pk=pk)
    except Photo.DoesNotExist:
        raise Http404("Photo does not exist")

    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo.title = form.cleaned_data['title']
            photo.description = form.cleaned_data['description']
            photo.hashtags.clear()
            hashtags = request.POST.getlist('hashtags[]')
            for hashtag in hashtags:
                if not Hashtag.objects.filter(tag=hashtag).exists():
                    new_hashtag = Hashtag.objects.create(tag=hashtag)
                    new_hashtag.save()
                hashtag_object = Hashtag.objects.get(tag=hashtag)
                photo.hashtags.add(hashtag_object)
            photo.save()
            return HttpResponseRedirect(reverse('detail_photo', kwargs={'pk': photo.id}))
    else:
        form = PhotoForm(instance=photo)

    return render(request, 'mainApp/edit_photo.html', {'form': form, 'photo': photo})


@login_required
def profile(request):
    """Отображение страницы с настройками пользователя"""
    return render(request, 'mainApp/profile.html')


def about(request):
    """Отображение страницы "О нас" """
    return render(request, 'mainApp/about.html')


def contact(request):
    """Отображение страницы "Контакты" """
    return render(request, 'mainApp/contact.html')


@login_required
def photo_import(request):
    """Отображение страницы в момент импорта фотографий из Вконтакте"""
    vk_user = None
    if 'state' not in request.GET:
        if len(UserSocialAuth.objects.filter(user=request.user, provider='vk-oauth2')) <= 0:
            return HttpResponseRedirect(
                'https://oauth.vk.com/authorize?client_id=7346377&display=page&redirect_uri=http://saved-production'
                '.herokuapp.com/photo_import&scope=photos&response_type=code&v=5.103&state=1')
        vk_user = UserSocialAuth.objects.get(user=request.user, provider='vk-oauth2')
    elif request.GET['state'] == '1':
        response = requests.get(
            'https://oauth.vk.com/access_token?client_id=7346377&client_secret=LNLjEgOrBOeIu6cJQVYb&redirect_uri=http'
            '://saved-production.herokuapp.com/photo_import&code=' + request.GET['code'] + '&state=2')
        UserSocialAuth.create_social_auth(user=request.user, uid=response.json()['user_id'], provider='vk-oauth2')
        vk_user = UserSocialAuth.objects.get(user=request.user, provider='vk-oauth2')
        vk_user.set_extra_data({'access_token': response.json()['access_token']})
    imports = upload.delay(vk_user.access_token, vk_user.uid, request.user.id)
    return render(request, 'mainApp/photo_import.html', context={'task_id': imports.task_id})


@login_required
def photo_delete(request, pk):
    """Удаление конкретной фотографии"""
    try:
        photo = Photo.objects.filter(owner=request.user).get(pk=pk)
        photo.delete()
    except Photo.DoesNotExist:
        raise Http404("Photo does not exist")
    return HttpResponseRedirect(reverse('main_window'))

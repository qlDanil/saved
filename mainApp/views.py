import math
import time
import vk
import requests
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from .forms import PhotoForm
from .models import Photo, Hashtag
from social_django.models import UserSocialAuth


@login_required
def main_window(request):
    hashtags = request.GET.get('hashtag', 'all')
    photos = Photo.objects.filter(owner=request.user)
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
    try:
        photo = Photo.objects.filter(owner=request.user).get(pk=pk)
    except Photo.DoesNotExist:
        raise Http404("Photo does not exist")

    return render(request, 'mainApp/photo_detail.html', context={'photo': photo})


@login_required
def add_photo(request):
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
    try:
        photo = Photo.objects.filter(owner=request.user).get(pk=pk)
    except Photo.DoesNotExist:
        raise Http404("Photo does not exist")

    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES)
        print(form)
        if form.is_valid():
            photo.title = form.cleaned_data['title']
            photo.description = form.cleaned_data['description']
            photo.image = form.cleaned_data['image']
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
        print(form['image'].value())

    return render(request, 'mainApp/add_photo.html', {'form': form})


@login_required
def profile(request):
    return render(request, 'mainApp/profile.html')


def about(request):
    return render(request, 'mainApp/about.html')


def contact(request):
    return render(request, 'mainApp/contact.html')


@login_required
def photo_import(request):
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
    vk_token = vk_user.access_token
    session = vk.Session(access_token=vk_token)
    vk_api = vk.API(session)
    album_id = -15
    owner_id = vk_user.uid
    photos_count = vk_api.photos.getAlbums(owner_id=owner_id, album_ids=album_id, v='5.30')['items'][0]['size']
    counter = 0
    progress = 0
    failed = 0
    cached = 0
    time_now = time.time()

    for j in range(math.ceil(photos_count / 1000)):
        photos = vk_api.photos.get(owner_id=owner_id, album_id=album_id, count=1000, offset=j * 1000, v='5.30')['items']
        for photo in photos:
            counter += 1
            if {'vk_id': photo['id']} in Photo.objects.filter(owner=request.user).values('vk_id'):
                cached += 1
                continue
            if 'photo_2560' in photo:
                url = photo['photo_2560']
            elif 'photo_2560' in photo:
                url = photo['photo_1280']
            elif 'photo_807' in photo:
                url = photo['photo_807']
            elif 'photo_604' in photo:
                url = photo['photo_604']
            elif 'photo_130' in photo:
                url = photo['photo_130']
            elif 'photo_75' in photo:
                url = photo['photo_75']
            else:
                url = None
            print('Загружаю фото № {} из {}. Прогресс: {} %'.format(counter, photos_count, progress))
            progress = round(100 / photos_count * counter, 2)
            try:
                new_photo = Photo.objects.create(title='Фото_' + str(photo['id']), description=photo['text'],
                                                 vk_id=photo['id'], owner=request.user)
                new_photo.save_photo_from_url(url)
            except Exception:
                print('Произошла ошибка, файл пропущен.')
                failed += 1
                continue
    time_for_dw = time.time() - time_now
    print(
        "\nВ очереди было {} файлов. Из них удачно загружено {} файлов, {} не удалось загрузить. {} Были загружены "
        "ранее. Затрачено времени: {} сек.".format(photos_count, photos_count - failed, failed, cached,
                                                   round(time_for_dw, 1)))
    return render(request, 'mainApp/profile.html')

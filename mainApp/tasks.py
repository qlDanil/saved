import time
import vk
import math
from celery import shared_task
from django.contrib.auth.models import User
from .models import Photo, Hashtag
from celery_progress.backend import ProgressRecorder
import os
from .ocr import get_text
import requests
from urllib.request import urlopen, urlretrieve

rest_api_address = os.environ.get('REST_API_ADDRESS')
DEBUG = bool(os.environ.get('DJANGO_DEBUG', True))


def is_rest_api_work():
    try:
        urlopen(rest_api_address, timeout=0.5)
        return True
    except:
        return False


@shared_task(bind=True)
def upload(self, vk_token, owner_id, user_id):
    """Процесс импорта фотографий из Вконтакте для ассинхронного выполнения"""
    if not Hashtag.objects.filter(tag='VK').exists():
        new_hashtag = Hashtag.objects.create(tag='VK')
        new_hashtag.save()
    hashtag_vk = Hashtag.objects.get(tag='VK')
    progress_recorder = ProgressRecorder(self)
    try:
        vk_api = vk.API(vk.Session(access_token=vk_token))
    except Exception as e:
        print(e.msg)
    album_id = -15
    try:
        photos_count = vk_api.photos.getAlbums(owner_id=owner_id, album_ids=album_id, v='5.81')['items'][0]['size']
    except Exception as e:
        print(e.msg)
    counter = 0
    progress = 0
    failed = 0
    cached = 0
    time_now = time.time()

    for j in range(math.ceil(photos_count / 1000)):
        photos = vk_api.photos.get(owner_id=owner_id, album_id=album_id, count=1000, offset=j * 1000, v='5.81')['items']
        for photo in photos:
            counter += 1
            if {'vk_id': photo['id']} in Photo.objects.filter(owner=User.objects.get(id=user_id)).values('vk_id'):
                cached += 1
                continue
            url = photo['sizes'][-1]['url']
            print('Загружаю фото № {} из {}. Прогресс: {} %'.format(counter, photos_count, progress))
            progress_recorder.set_progress(counter, photos_count)
            progress = round(100 / photos_count * counter, 2)
            new_photo = None
            try:
                new_photo = Photo.objects.create(title='Photo_' + str(photo['id']), description=photo['text'],
                                                 vk_id=photo['id'], owner=User.objects.get(id=user_id))
                new_photo.hashtags.add(hashtag_vk)
                new_photo.save_photo_from_url(url)
            except Exception as e:
                new_photo.delete()
                print('Произошла ошибка, файл пропущен.\n' + str(e))
                failed += 1
                continue
            new_photo.description = new_photo.description + " || Optical character recognition: " + get_text(
                new_photo.image.url)
            new_photo.save()

            if is_rest_api_work():
                if DEBUG:
                    url = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + new_photo.image.url
                    files = {'file': open(url, 'rb')}
                else:
                    url = new_photo.image.url
                    filename = './' + url.split("/")[-1]
                    urlretrieve(url, filename)
                    files = {'file': open(filename, 'rb')}
                response_1 = requests.post(rest_api_address + '/1', files=files)
                hashtags = response_1.text.replace('\"', '').split(' ')
                response_2 = requests.post(rest_api_address + '/2', files=files)
                new_photo.description = new_photo.description + " || Image captioning: " + " ".join(
                    str(response_2.text))

                for hashtag in hashtags:
                    if not Hashtag.objects.filter(tag=hashtag).exists():
                        new_hashtag = Hashtag.objects.create(tag=hashtag)
                        new_hashtag.save()
                    hashtag_object = Hashtag.objects.get(tag=hashtag)
                    new_photo.hashtags.add(hashtag_object)
            new_photo.available = True
            new_photo.save()

    time_for_dw = time.time() - time_now
    print(
        "\nВ очереди было {} файлов. Из них удачно загружено {} файлов, {} не удалось загрузить. {} Были загружены "
        "ранее. Затрачено времени: {} сек.".format(photos_count, photos_count - failed, failed, cached,
                                                   round(time_for_dw, 1)))
    return True


@shared_task(bind=True)
def save_photo(self, hashtags, photo_id):
    progress_recorder = ProgressRecorder(self)
    new_photo = Photo.objects.get(id=photo_id)
    new_photo.description = new_photo.description + " || Optical character recognition: " + get_text(
        new_photo.image.url)
    new_photo.save()
    progress_recorder.set_progress(25, 100)

    if is_rest_api_work():
        if DEBUG:
            url = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + new_photo.image.url
            files = {'file': open(url, 'rb')}
        else:
            url = new_photo.image.url
            filename = './' + url.split("/")[-1]
            urlretrieve(url, filename)
            files = {'file': open(filename, 'rb')}
        response_1 = requests.post(rest_api_address + '/1', files=files)
        hashtags = response_1.text.replace('\"', '').split(' ')
        response_2 = requests.post(rest_api_address + '/2', files=files)
        new_photo.description = new_photo.description + " || Image captioning: " + " ".join(str(response_2.text))

        progress_recorder.set_progress(75, 100)
        for hashtag in hashtags:
            if not Hashtag.objects.filter(tag=hashtag).exists():
                new_hashtag = Hashtag.objects.create(tag=hashtag)
                new_hashtag.save()
            hashtag_object = Hashtag.objects.get(tag=hashtag)
            new_photo.hashtags.add(hashtag_object)
    new_photo.available = True
    new_photo.save()
    progress_recorder.set_progress(100, 100)
    return True

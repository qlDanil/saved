import time
import vk
import math
from celery import shared_task
from django.contrib.auth.models import User
from .models import Photo, Hashtag
from celery_progress.backend import ProgressRecorder


@shared_task(bind=True)
def upload(self, vk_token, owner_id, user_id):
    """Процесс импорта фотографий из Вконтакте для ассинхронного выполнения"""
    if not Hashtag.objects.filter(tag='ВК').exists():
        new_hashtag = Hashtag.objects.create(tag='ВК')
        new_hashtag.save()
    hashtag_vk = Hashtag.objects.get(tag='ВК')
    progress_recorder = ProgressRecorder(self)
    vk_api = vk.API(vk.Session(access_token=vk_token))
    album_id = -15
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
            if {'vk_id': photo['id']} in Photo.objects.filter(owner=User.objects.get(id=user_id)).values('vk_id'):
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
            progress_recorder.set_progress(counter, photos_count)
            progress = round(100 / photos_count * counter, 2)
            try:
                new_photo = Photo.objects.create(title='Фото_' + str(photo['id']), description=photo['text'],
                                                 vk_id=photo['id'], owner=User.objects.get(id=user_id))
                new_photo.hashtags.add(hashtag_vk)
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
    return True

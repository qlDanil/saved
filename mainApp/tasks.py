import time
import vk
import math
from celery import shared_task
from django.contrib.auth.models import User
from .models import Photo, Hashtag
from celery_progress.backend import ProgressRecorder
import os
import cv2
from .ocr import get_text
from .caption import evaluate

DEBUG = bool(os.environ.get('DJANGO_DEBUG', True))

if DEBUG:
    from yolov4.tflite import YOLOv4


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
            new_photo = None
            try:
                new_photo = Photo.objects.create(title='Фото_' + str(photo['id']), description=photo['text'],
                                                 vk_id=photo['id'], owner=User.objects.get(id=user_id))
                new_photo.hashtags.add(hashtag_vk)
                new_photo.save_photo_from_url(url)
            except Exception as e:
                new_photo.delete()
                print('Произошла ошибка, файл пропущен.\n' + str(e))
                failed += 1
                continue
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
    new_photo.description = new_photo.description + " || Оптическое распознавание символов: " + get_text(
        new_photo.image.url)
    if DEBUG:
        url = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + new_photo.image.url
        new_photo.description = new_photo.description + " || Генерация подписи: " + " ".join(evaluate(url)[:-1])
        yolo = YOLOv4()
        yolo.config.parse_names("mainApp/yolov4Data/coco.names")
        yolo.config.parse_cfg("mainApp/yolov4Data/yolov4-tiny.cfg")
        yolo.load_tflite("mainApp/yolov4Data/yolov4-tiny-float16.tflite")

        frame = cv2.imread(url)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        progress_recorder.set_progress(50, 100)
        bboxes = yolo.predict(frame_rgb, prob_thresh=0.25)
        items = set()
        for box in bboxes:
            items.add(yolo.config.names[box[4]])
        hashtags.extend(items)
    progress_recorder.set_progress(50, 100)
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

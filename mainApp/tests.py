from django.test import TestCase
from .models import Photo, Hashtag
from django.db.models import Q


class PhotoModelTest(TestCase):
    """Класс тестирования функционала веб-сервиса"""

    @classmethod
    def setUpTestData(cls):
        new_hashtag = Hashtag.objects.create(tag='cat')
        new_hashtag.save()
        new_photo = Photo.objects.create(title='Photo with cat', description='Beautiful photo with white cat')
        new_photo.save()
        new_photo.hashtags.add(new_hashtag)
        new_photo.save()
        new_photo_2 = Photo.objects.create(title='Photo', description='Beautiful photo')
        new_photo_2.save()

    def test_title_label(self):
        photo = Photo.objects.get(id=1)
        field_label = photo._meta.get_field('title').verbose_name
        self.assertEquals(field_label, 'title')

    def test_description_label(self):
        photo = Photo.objects.get(id=1)
        field_label = photo._meta.get_field('description').verbose_name
        self.assertEquals(field_label, 'description')

    def test_title_max_length(self):
        photo = Photo.objects.get(id=1)
        max_length = photo._meta.get_field('title').max_length
        self.assertEquals(max_length, 30)

    def test_object_name_is_title(self):
        photo = Photo.objects.get(id=1)
        expected_object_name = photo.title
        self.assertEquals(expected_object_name, str(photo))

    def test_get_absolute_url(self):
        photo = Photo.objects.get(id=1)
        self.assertEquals(photo.get_absolute_url(), '/photo_1/')

    def test_get_photo_by_tag(self):
        photos = Photo.objects.all()
        photo = photos.get(hashtags__tag='cat')
        self.assertEquals(photo.title, 'Photo with cat')

    def test_get_photo_by_search(self):
        search = 'cat'
        photos = Photo.objects.all()
        photo = photos.get(Q(hashtags__tag__icontains=search) | Q(description__icontains=search))
        self.assertEquals(photo.title, 'Photo with cat')

    def test_get_photo_by_search_2(self):
        search = 'Beautiful'
        photos = Photo.objects.all()
        photos = photos.filter((Q(hashtags__tag__icontains=search) | Q(description__icontains=search)))
        self.assertEquals(photos.count(), 2)

from django.test import TestCase
from .models import Photo


class PhotoModelTest(TestCase):
    """Класс тестирования функционала веб-сервиса"""
    @classmethod
    def setUpTestData(cls):
        Photo.objects.create(title='Big', description='Bob')

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

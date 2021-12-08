import os
from urllib.request import urlretrieve
from django.contrib.auth.models import User
from django.core.files.images import ImageFile
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.db.models.aggregates import Count
from random import randint
from django.dispatch import receiver


class HashtagsManager(models.Manager):
    """Класс-менеджер для выбора случайного хештега"""

    def random(self):
        count = self.aggregate(count=Count('id'))['count']
        random_index = randint(0, count - 1)
        return self.all()[random_index]


class Hashtag(models.Model):
    """Класс-модель хештег"""
    objects = HashtagsManager()
    tag = models.CharField(max_length=30)

    class Meta:
        ordering = ["tag"]

    def __str__(self):
        return self.tag


def get_upload_path(instance, filename):
    """Вычисление пути сохранения фотографий пользователя"""
    return os.path.join(
        "saved_photos", "user_%d(%s)" % (instance.owner.id, instance.owner.username),
        instance.date_time.strftime("%Y-%m-%d"), filename)


class Photo(models.Model):
    """Класс-модель фотография"""
    title = models.CharField(max_length=30)
    description = models.CharField(max_length=1000)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to=get_upload_path, max_length=500)
    vk_id = models.IntegerField(null=True, blank=True)
    hashtags = models.ManyToManyField(Hashtag)
    date_time = models.DateTimeField(default=timezone.now)
    available = models.BooleanField(default=False)

    class Meta:
        ordering = ["-date_time"]

    def get_absolute_url(self):
        return reverse('detail_photo', args=[str(self.id)])

    def __str__(self):
        return self.title

    def save_photo_from_url(self, url):
        """Сохранение фотографии по url"""
        result = urlretrieve(url)
        self.image.save(
            os.path.basename(url),
            ImageFile(file=open(result[0], 'rb'))
        )
        self.save()


@receiver(models.signals.post_delete, sender=Photo)
def remove_file_from_s3(sender, instance, using, **kwargs):
    """Сигнал для удаления файла из aws3 при удалении из базы данных"""
    instance.image.delete(save=False)

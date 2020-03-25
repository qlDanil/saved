import os
from datetime import datetime
from urllib.request import urlretrieve
from django.contrib.auth.models import User
from django.core.files import File
from django.db import models
from django.urls import reverse


class Photo(models.Model):
    title = models.CharField(max_length=30)
    description = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to='photos')
    vk_id = models.IntegerField(null=True, blank=True)
    date_time = models.DateTimeField(default=datetime.now())

    class Meta:
        ordering = ["title"]

    def get_absolute_url(self):
        return reverse('model-detail-view', args=[str(self.id)])

    def __str__(self):
        return self.title

    def save_photo_from_url(self, url):
        result = urlretrieve(url)
        self.image.save(
            os.path.basename(url),
            File(open(result[0], 'rb'))
        )
        self.save()

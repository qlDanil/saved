from django.db import models


# Create your models here.
class Picture(models.Model):
    title = models.CharField(max_length=500)
    URL_way = models.CharField(max_length=200)



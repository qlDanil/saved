# Generated by Django 3.1.7 on 2021-03-26 06:52

from django.db import migrations, models
import mainApp.models


class Migration(migrations.Migration):

    dependencies = [
        ('mainApp', '0009_auto_20201121_2031'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='image',
            field=models.ImageField(max_length=500, upload_to=mainApp.models.get_upload_path),
        ),
    ]
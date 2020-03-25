from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_window, name='main_window'),
    path('add_photo/', views.add_photo, name='add_photo'),
    path('profile/', views.profile, name='profile'),
    path('photo_import/', views.photo_import, name='photo_import'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_window, name='main_window'),
    path('add_photo/', views.add_photo, name='add_photo'),
    path('edit_photo/photo_<int:pk>', views.edit_photo, name='edit_photo'),
    path('profile/', views.profile, name='profile'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('photo_import/', views.photo_import, name='photo_import'),
    path('photo_<int:pk>/', views.detail_photo, name='detail_photo'),
    path('photo_delete_<int:pk>/', views.photo_delete, name='photo_delete'),
]

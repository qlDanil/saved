from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_window, name='main_window'),
]

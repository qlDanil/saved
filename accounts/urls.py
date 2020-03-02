from django.urls import path
from accounts import views

urlpatterns = [
    path('', views.signup, name="signup"),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
]

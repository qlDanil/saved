from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^celery-progress/', include('celery_progress.urls')),
    path('', include('social_django.urls')),
    path('', include('mainApp.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('signup/', include('accounts.urls')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

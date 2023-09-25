from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

#URL Config
urlpatterns = [
    path("", views.home, name= "homepage"),
    path("", views.upload_file, name= 'upload_file'),
]

if settings.DEBUG:
    urlpatterns +=static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)

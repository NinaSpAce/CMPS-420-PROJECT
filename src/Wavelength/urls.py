from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

#URL Config
urlpatterns = [
    path("", views.home, name= "homepage"),
    path("presentation", views.presentation, name= "presentation"),
    path("settings/graphs", views.settings1, name= "settings-graphs"),
    path("settings/electrode-topography", views.settings2, name="settings-electrode-topography"),
    path("settings/image-map", views.settings3, name="settings-image-map")
]

if settings.DEBUG:
    urlpatterns +=static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)

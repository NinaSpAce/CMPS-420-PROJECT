from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

#URL Config
urlpatterns = [
    path("home", views.home, name= "homepage"),
    path("presentation", views.presentation, name= "presentation"),
    path("settings/graphs", views.settings1, name= "settings-graphs"),
    path("settings/graphs/regression", views.regression_handling, name="regression"),
    path("settings/graphs/filtering", views.filter_handling, name="filtering"),
    path("settings/graphs/ica", views.ica_handling, name="ica"),
    path("settings/graphs/channels", views.channel_graph, name="channels"),
    path("settings/graphs/epochs", views.epoch_handler, name="epochs"),
]

if settings.DEBUG:
    urlpatterns +=static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)

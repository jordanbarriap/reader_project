from django.conf.urls import include, url

from api import views

urlpatterns = [
    url(r"^$", views.root, name="root"),
    url(r"^annotator/annotations/?$", views.index_create, name="index_create"),
    url(r"^annotator/annotations/(?P<pk>.+)/?$", views.read_update_delete, name="read_update_delete"),
    url(r"^annotator/search/?$", views.search, name="search"),
    url(r"^reader/?$", views.reading_log, name="reading_log")
]
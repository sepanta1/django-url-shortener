from django.urls import path

from .views import shorten_form_view
from .views import user_shorten_links

app_name = "shortener"

urlpatterns = [
    path("", shorten_form_view, name="home"),
    path("mylinks/", user_shorten_links, name="mylinks"),
]

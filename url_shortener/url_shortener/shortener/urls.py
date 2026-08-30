from django.urls import path

from .views import shorten_form_view

# app_name = "shortener"

urlpatterns = [
    path("", shorten_form_view, name="home"),
]

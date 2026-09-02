from django.urls import path

from . import views

app_name = "redirector"

urlpatterns = [
    path("<str:short_code>/", views.redirect_view, name="redirect"),
]

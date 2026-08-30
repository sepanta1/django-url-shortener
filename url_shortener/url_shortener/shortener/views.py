from django.shortcuts import render

from url_shortener.links.models import ShortenedURL

from .forms import ShortenURLForm
from .services import create_short_url


def shorten_form_view(request):
    short_url = None

    if request.method == "POST":
        form = ShortenURLForm(request.POST)
        if form.is_valid():
            long_url = form.cleaned_data["long_url"]
            code = create_short_url(long_url, ShortenedURL, user=request.user)
            short_url = request.build_absolute_uri(f"/{code}")
    else:
        form = ShortenURLForm()

    return render(
        request,
        "shortener/home.html",
        {"form": form, "short_url": short_url},
    )

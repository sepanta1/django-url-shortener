from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django_ratelimit.decorators import ratelimit

from url_shortener.links.models import ShortenedURL

from .forms import ShortenURLForm
from .services import create_short_url


def _shorten_rate(group, request):
    """Effectively unlimited for logged-in users, 10/hour for anonymous visitors."""
    if request.user.is_authenticated:
        return "500/h"
    return "10/h"


@ratelimit(key="ip", rate=_shorten_rate, method="POST", block=True)
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


@login_required
def user_shorten_links(request):
    links = ShortenedURL.objects.filter(created_by=request.user)
    return render(
        request,
        "shortener/user_links.html",
        {
            "links": links,
        },
    )

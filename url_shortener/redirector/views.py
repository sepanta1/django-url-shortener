from django.shortcuts import redirect, render

from url_shortener.redirector.services import resolve_short_code

# Create your views here.
def redirect_view(request,short_code):
    long_url = resolve_short_code(short_code)
    return redirect(long_url)
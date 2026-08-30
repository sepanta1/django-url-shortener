from django.contrib import admin

from .models import ShortenedURL


@admin.register(ShortenedURL)
class ShortenedURLAdmin(admin.ModelAdmin):
    list_display = ["short_code", "long_url", "created_by", "click_count", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["short_code", "long_url", "created_by__username"]
    readonly_fields = ["created_at", "click_count", "last_clicked_at"]

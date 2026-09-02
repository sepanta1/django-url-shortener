from django.conf import settings
from django.db import models


class ShortenedURL(models.Model):
    short_code= models.CharField(max_length=10,primary_key=True)
    long_url = models.URLField(max_length=2050)
    created_at= models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="shortened_urls",
    )
    click_count = models.PositiveIntegerField(default=0)
    last_clicked_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        verbose_name = "Shortened URL"
        verbose_name_plural = "Shortened URLs"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.short_code} → {self.long_url[:50]}"

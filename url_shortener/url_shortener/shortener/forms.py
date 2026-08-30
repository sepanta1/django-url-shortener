from django import forms


class ShortenURLForm(forms.Form):
    long_url = forms.URLField(
        label="URL to shorten:",
        max_length=2050,
        widget=forms.URLInput(
            attrs={"placeholder": "https://example.com/your-long-url"}
        ),
    )

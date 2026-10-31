from django.conf import settings
from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt


def home(request):
    return render(request, "learning/index.html")


# The hosted development preview embeds the app in a frame.
if settings.DEBUG:
    home = xframe_options_exempt(home)

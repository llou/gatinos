from datetime import date
from django.conf import settings


def title(request):
    return {"app_title": settings.APPLICATION_TITLE}


def version(request):
    return {"app_version": settings.VERSION}


def year(request):
    return {"current_year": date.today().year}

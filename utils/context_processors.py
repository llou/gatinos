from django.conf import settings


def title(request):
    return {"title": settings.APPLICATION_TITLE}


def version(request):
    return {"version": settings.VERSION}

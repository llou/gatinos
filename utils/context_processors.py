from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo
from django.conf import settings
from gatinos import __version__
from gatos.models import Anuncio


def metadata(request):
    return {"app_title": settings.APPLICATION_TITLE,
            "app_version": __version__,
            "current_year": date.today().year}


def check_intervalo(t, h_i=None, h_f=None):
    if h_i is None and h_f is None:
        return True
    elif h_i is None and h_f is not None and t < h_f:
        return True
    elif h_i is not None and h_f is None and t > h_i:
        return True
    elif h_i is not None and h_f is not None and h_i < t < h_f:
        return True
    else:
        return False


def anuncios(request):
    now = datetime.now(ZoneInfo("Europe/Madrid"))
    anuncios = []
    for anuncio in Anuncio.objects.all():
        if check_intervalo(now, anuncio.hora_inicio, anuncio.hora_fin):
            anuncios.append(anuncio)
    return {"anuncios": anuncios}

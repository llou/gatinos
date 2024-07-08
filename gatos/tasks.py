from datetime import date
from django.conf import settings
from celery import shared_task
from .models import Foto, Colonia, Gato
from .flows import GatoFlow


@shared_task()
def process_image(foto_id):
    foto_instancia = Foto.objects.get(id=foto_id)
    foto_pil = foto_instancia.get_pil_image()
    foto_instancia.update_miniatura(pil=foto_pil)
    foto_instancia.update_exif(pil=foto_pil)
    foto_instancia.save()


@shared_task()
def update_miniaturas(colonia_slug):
    colonia = Colonia.objects.get(slug=colonia_slug)
    for foto in colonia.fotos.all():
        if not foto.miniatura:
            foto.update_miniatura()


@shared_task()
def update_exif(colonia_slug):
    colonia = Colonia.objects.get(slug=colonia_slug)
    for foto in colonia.fotos.all():
        if not foto.exif:
            foto.update_exif()


def get_ultima_fecha(gato):
    fechas = gato.get_actividad()
    if not fechas:
        return
    fechas.sort()
    return fechas[-1]


def update_estado_gato(gato):
    tdelta = date.today() - get_ultima_fecha(gato)
    flow = GatoFlow(gato)
    if gato.estado == 'LIBRE' and tdelta > settings.PERIODO_DESAPARECIDO:
        flow.desaparecer()
    if gato.estado == 'DESAPARECIDO' and tdelta > settings.PERIODO_OLVIDADO:
        flow.olvidar()


def check_gatos_estado():
    gatos = Gato.objects.filter(estado__in=["LIBRE",
                                            "OLVIDADO",
                                            "DESAPARECIDO"])
    for gato in gatos:
        update_estado_gato(gato)

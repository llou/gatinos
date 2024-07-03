from django.conf import settings
from celery import shared_task
from .models import Foto, Colonia


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

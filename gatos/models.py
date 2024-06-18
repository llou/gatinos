import uuid
from io import BytesIO
from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS
from django.core.files import File
from django.conf import settings
from django.urls import reverse
from django.db import models
from django.utils.text import slugify
from .utils import pil_to_django_file

SEXOS = [
          ("M", "Macho"),
          ("H", "Hembra")
]


class Gato(models.Model):
    slug = models.SlugField(max_length=200, unique=True, default="")
    nombre = models.CharField(max_length=200, unique=True)
    color = models.CharField(max_length=50)
    descripcion = models.TextField()
    colonia = models.ForeignKey("gatos.Colonia", on_delete=models.CASCADE,
                                related_name="gatos")
    retrato = models.ForeignKey("gatos.Foto", on_delete=models.SET_NULL,
                                null=True)
    sexo = models.CharField(max_length=10, choices=SEXOS)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("gato", kwargs={"colonia": self.colonia.slug,
                                       "gato": self.slug})

    @property
    def foto(self):
        if self.retrato:
            return self.retrato.foto.url
        else:
            return settings.RELLENO_FOTO_URL

    def __str__(self):
        return self.nombre

    def __repr__(self):
        return f"<{self.__class__.__name__} nombre='{self.nombre}'>"


class Colonia(models.Model):
    slug = models.SlugField(max_length=200, unique=True, default="")
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("colonia", kwargs={"colonia": self.slug})

    def __str__(self):
        return self.nombre

    def __repr__(self):
        return f"<{self.__class__.__name__} nombre='{self.nombre}'>"


class Foto(models.Model):
    MINIATURA_SIZE = (170, 120)

    colonia = models.ForeignKey("gatos.Colonia", on_delete=models.CASCADE,
                                related_name="fotos")
    foto = models.ImageField(upload_to="fotos/%Y/%m/%d")
    miniatura = models.ImageField(upload_to="miniaturas/%Y/%m/%d", default="")
    exif = models.JSONField(default=dict)
    descripcion = models.TextField(blank=True)
    gatos = models.ManyToManyField("gatos.Gato", related_name="fotos",
                                   blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    @property
    def foto_name(self):
        return Path(self.foto.name).name

    def get_pil_image(self):
        return Image.open(self.foto.path)

    def update_miniatura(self, pil=None):
        if pil is None:
            pil = self.get_pil_image()
        pil.thumbnail(self.MINIATURA_SIZE)
        django_file = pil_to_django_file(pil)
        self.miniatura.save(self.foto_name, django_file)
        self.save()

    def update_exif(self, pil=None):
        if pil is None:
            pil = self.get_pil_image()
        exif = pil._getexif()
        if exif is not None:
            self.exif = {TAGS.get(tag, tag): value for tag, value in exif.items()}
        self.save()

    def get_absolute_url(self):
        return reverse("foto", kwargs={"colonia": self.colonia.slug,
                                       "foto": self.uuid})

    def __str__(self):
        return str(self.uuid)

    def __repr__(self):
        return f"<{self.__class__.__name__} id={self.id}>"


EVENTOS_GATO = (
        ('PESADA', 'PESADA'),
        ('NACIMIENTO', 'Nacimiento'),
        ('CAPTURA', 'Captura'),
        ('DEVOLUCION', 'Devolución'),
        ('DIAGNOSTICO', 'Diagnóstico'),
        ('MUERTE', 'Muerte'),
        ('APARICION', 'Aparición'),
        ('DESAPARICION', 'Desaparición'),
        ('REAPARICION', 'Reaparición'),
        ('VACUNACION', 'Vacunación'),
        ('ENFERMEDAD', 'Enfermedad'),
        ('CURACION', 'Curación'),
        ('ESTERILIZACION', 'Esterilización'),
        )


class GatoEvent(models.Model):
    gato = models.ForeignKey("gatos.Gato", related_name="eventos",
                             on_delete=models.CASCADE)
    tipo = models.CharField(max_length=50, choices=EVENTOS_GATO)
    momento = models.DateTimeField(auto_now=True)
    valor = models.DecimalField(max_digits=6, decimal_places=2)
    observaciones = models.TextField(blank=True)


EVENTOS_COLONIA = (
        ('FUNDACION', 'Fundación'),
        ('CLAUSURA', 'Clausura'),
        ('ABANDONO', 'Abandono'),
        )


class ColoniaEvent(models.Model):
    colonia = models.ForeignKey("gatos.Colonia", related_name="eventos",
                                on_delete=models.CASCADE)
    tipo = models.CharField(max_length=50, choices=EVENTOS_COLONIA)
    momento = models.DateTimeField(auto_now=True)
    valor = models.DecimalField(max_digits=6, decimal_places=2)
    observaciones = models.TextField(blank=True)

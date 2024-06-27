import uuid
from functools import reduce
from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS
from django.conf import settings
from django.urls import reverse
from django.db import models
from django.utils.text import slugify
from .data import vacunas
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
    esterilizacion = models.DateField(null=True)
    feo = models.BooleanField(default=False)

    @property
    def peso(self):
        return self.get_ultima_captura().peso

    @property
    def capturado(self):
        return self.get_ultima_captura() is not None

    @property
    def estado(self):
        return "Vivito"

    def get_vacunas(self):
        return Vacunacion.objects.filter(captura__gato=self)

    def get_ultima_captura(self):
        capturas = self.capturas.filter(fecha_liberacion=None).order_by("-fecha_captura")
        if capturas:
            return capturas[0]
        return None

    def get_peso(self):
        capturas = self.capturas.exclude(peso=None).order_by("-fecha_captura")
        if capturas:
            return capturas[0].peso
        return None

    def devolucion(self):
        pass

    def sexuacion(self, sexo):
        self.sexo = sexo
        self.save()

    def pesada(self, peso):
        pass

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
        clase = self.__class__.__name__
        nombre = self.nombre
        colonia = self.colonia.nombre
        return f"<{clase} nombre='{nombre}' colonia='{colonia}'>"


class Colonia(models.Model):
    slug = models.SlugField(max_length=200, unique=True, default="")
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, default="")

    @property
    def gatos_activos(self):
        return 0

    def get_actividad(self, min_fecha=None, max_fecha=None):
        result = []
        informes = self.informes
        fotos = self.fotos
        if min_fecha is not None:
            informes = informes.filter(fecha__gte=min_fecha)
            fotos = fotos.filter(fecha__gte=min_fecha)
        if max_fecha is not None:
            informes = informes.filter(fecha__lte=max_fecha)
            fotos = fotos.filter(fecha__lte=max_fecha)
        result.extend([x.fecha for x in informes.all()])
        result.extend([x.fecha for x in fotos.all()])
        return result

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("colonia", kwargs={"colonia": self.slug})

    def __str__(self):
        return self.nombre

    def __repr__(self):
        return f"<{self.__class__.__name__} nombre='{self.nombre}'>"


class UserBound(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL,
                                on_delete=models.SET_NULL,
                                blank=True,
                                null=True)
    nombre_usuario = models.CharField(max_length=200, blank=True, default="")

    def save(self, *args, **kwargs):
        if self.usuario is not None and self.nombre_usuario != "":
            self.nombre_usuario = " ".join((self.usuario.first_name,
                                            self.usuario.last_name))
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class Foto(UserBound):
    MINIATURA_SIZE = (170, 120)

    colonia = models.ForeignKey("gatos.Colonia", on_delete=models.CASCADE,
                                related_name="fotos")
    foto = models.ImageField(upload_to="fotos/%Y/%m/%d")
    miniatura = models.ImageField(upload_to="miniaturas/%Y/%m/%d", default="")
    exif = models.JSONField(default=dict)
    descripcion = models.TextField(blank=True)
    gatos = models.ManyToManyField("gatos.Gato", related_name="fotos",
                                   blank=True)
    fecha = models.DateField(auto_now_add=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    fea = models.BooleanField(default=False)

    @property
    def foto_name(self):
        return Path(self.foto.name).name

    def es_fea(self):
        gatos = [z.feo for z in self.gatos.all()]
        gatos = reduce(lambda x, y: x or y.feo, gatos)
        return self.fea or gatos

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


class Informe(UserBound):
    colonia = models.ForeignKey("gatos.Colonia", on_delete=models.CASCADE,
                                related_name="informes")
    fecha = models.DateField(auto_now=True)
    titulo = models.CharField(max_length=250)
    texto = models.TextField(blank=True, default="")
    gatos = models.ManyToManyField("gatos.Gato", related_name="informes")

    def __repr__(self):
        class_name = self.__class__.__name__
        name = self.gato.name
        tipo = self.tipo
        return f"<{class_name} gato={name} tipo={tipo}>"

    def __str__(self):
        return f"{self.titulo}"


class Captura(UserBound):
    gato = models.ForeignKey("gatos.Gato", related_name="capturas",
                             on_delete=models.CASCADE)
    fecha_captura = models.DateField(auto_now=True)
    fecha_liberacion = models.DateField(null=True, default=None)
    peso = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    esterilizacion = models.BooleanField(default=False)
    sacrificio = models.BooleanField(default=False)
    observaciones = models.TextField(blank=True, default="")

    class Meta:
        permissions = [
                ("capturar_gato", ""),
                ("liberar_gato", ""),
                ]

    @property
    def capturado(self):
        return self.fecha_liberacion is None

    def get_absolute_url(self):
        view = "captura-update" if self.capturado else "captura"
        return reverse(view, kwargs={"colonia": self.gato.colonia.slug,
                                     "gato": self.gato.slug,
                                     "pk": self.id})

    def __repr__(self):
        class_name = self.__class__.__name__
        name = self.gato.name
        fecha = self.gato.fecha_captura
        return f"<{class_name} gato={name} fecha={fecha}>"

    def __str__(self):
        return "Capturado" if self.capturado else f"{self.fecha_captura}"


class Vacunacion(UserBound):
    captura = models.ForeignKey("gatos.Captura", related_name="vacunas",
                                on_delete=models.CASCADE)
    tipo = models.CharField(max_length=100,
                            choices=vacunas.get_choices())
    efecto = models.DurationField()

    class Meta:
        permissions = [
                ("vacunar_gato", ""),
                ]

    @property
    def duracion(self):
        return vacunas[self.tipo]["duracion"]

    @property
    def fecha(self):
        return self.captura.fecha_captura

    @property
    def gato(self):
        return self.captura.gato

    def __repr__(self):
        cls = self.__class__.__name__
        vcn = self.get_tipo_display()
        fecha = self.captura.fecha_captura
        gato = self.gato.nombre
        return f"<{cls} nombre={vcn} gato={gato} fecha={fecha}>"

    def __str__(self):
        return self.get_tipo_display()


class Enfermedad(UserBound):
    gato = models.ForeignKey("gatos.Gato", related_name="enfermedades",
                             on_delete=models.CASCADE)
    diagnostico = models.CharField(max_length=200)
    fecha_diagnostico = models.DateField(auto_now=True)
    fecha_curacion = models.DateField(blank=True, null=True)
    observaciones = models.TextField(blank=True, default="")

    class Meta:
        verbose_name_plural = "enfermedades"

    def __repr__(self):
        class_name = self.__class__.__name__
        name = self.gato.name
        nombre = self.nombre
        fecha = self.fecha_diagnostico
        return f"<{class_name} gato={name} nombre={nombre} fecha={fecha}>"

    def __str__(self):
        return f"{self.diagnostico} ({self.fecha_diagnostico})"

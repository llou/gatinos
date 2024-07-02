import uuid
from datetime import date, timedelta
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


class Alta:
    def __init__(self, gato):
        self.gato = gato

    @property
    def fecha(self):
        return self.gato.fecha_alta

    def get_absolute_url(self):
        return self.gato.get_absolute_url()

    def __str__(self):
        return f"Alta {self.gato.nombre}"

    def __repr__(self):
        return f"<{self.__class__.__name__} gato={self.gato.nombre}>"


class GatosColoniaManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(vecino=False)


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
    esterilizacion = models.DateField(null=True, blank=True)
    feo = models.BooleanField(default=False)
    vecino = models.BooleanField(default=False)
    nombre_vecino = models.CharField(max_length=200, blank=True)
    fecha_alta = models.DateField(auto_now=True)
    muerto = models.BooleanField(default=False)
    muerto_fecha = models.DateField(null=True, blank=True)

    objects = models.Manager()
    gatos_colonia = GatosColoniaManager()

    @property
    def peso(self):
        return self.get_ultima_captura().peso

    def get_estado(self):
        if self.muerto:
            return "Muerto"
        if self.get_capturado():
            return "Capturado"
        if self not in self.colonia.get_gatos_activos():
            return "Desaparecido"
        else:
            return "Activo"

    def get_vacunas(self):
        return Vacunacion.objects.filter(captura__gato=self)

    def get_ultima_captura(self):
        capturas = self.capturas.filter(fecha_liberacion=None)
        capturas = capturas.order_by("-fecha_captura")
        if capturas:
            return capturas[0]
        return None

    def get_capturado(self):
        captura = self.get_ultima_captura()
        if captura is None:
            return False
        else:
            return captura.fecha_liberacion is None

    def get_peso(self):
        capturas = self.capturas.exclude(peso=None).order_by("-fecha_captura")
        if capturas:
            return capturas[0].peso
        return None

    def get_eventos(self, min_fecha=None, max_fecha=None):
        informes = self.informes
        fotos = self.fotos
        if min_fecha is not None:
            informes = informes.filter(fecha__gte=min_fecha)
            fotos = fotos.filter(fecha__gte=min_fecha)
        if max_fecha is not None:
            informes = informes.filter(fecha__lte=max_fecha)
            fotos = fotos.filter(fecha__lte=max_fecha)
        informes = list(informes.all())
        fotos = list(fotos.all())
        return informes + fotos + [Alta(self)]

    def get_actividad(self, min_fecha=None, max_fecha=None):
        eventos = self.get_eventos(min_fecha=min_fecha, max_fecha=max_fecha)
        return [x.fecha for x in eventos]

    def toggle_avistamiento(self, fecha, user):
        avistamientos = self.avistamientos.filter(fecha=fecha)
        if avistamientos:
            avistamientos.delete()
        else:
            av = Avistamiento(colonia=self.colonia, gato=self,
                              usuario=user, fecha=date.today())
            av.save()

    def devolucion(self):
        pass

    def sexuacion(self, sexo):
        self.sexo = sexo
        self.save()

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
    periodo_activo = models.DurationField(default=timedelta(120, 0, 0))
    descripcion = models.TextField(blank=True, default="")

    def get_eventos(self, min_fecha=None, max_fecha=None):
        informes = self.informes
        fotos = self.fotos
        avtos = self.gatos
        if min_fecha is not None:
            informes = informes.filter(fecha__gte=min_fecha)
            fotos = fotos.filter(fecha__gte=min_fecha)
            avtos = avtos.filter(fecha_alta__gte=min_fecha)
        if max_fecha is not None:
            informes = informes.filter(fecha__lte=max_fecha)
            fotos = fotos.filter(fecha__lte=max_fecha)
            avtos = avtos.filter(fecha_alta__lte=max_fecha)
        informes = list(informes.all())
        fotos = list(fotos.all())
        avtos = [Alta(x) for x in avtos.all()]
        return informes + fotos + avtos

    def get_actividad(self, min_fecha=None, max_fecha=None):
        eventos = self.get_eventos(min_fecha=min_fecha, max_fecha=max_fecha)
        return [x.fecha for x in eventos]

    def get_gatos_activos(self, min_fecha=None, max_fecha=None):
        if min_fecha is None:
            min_fecha = date.today() - self.periodo_activo
        result = set()
        eventos = self.get_eventos(min_fecha=min_fecha, max_fecha=max_fecha)
        for evento in eventos:
            if hasattr(evento, "gatos"):
                for gato in evento.gatos.filter(muerto=False):
                    result.add(gato)
            if hasattr(evento, "gato"):
                result.add(evento.gato)
        return list(result)

    def get_gatos_desaparecidos(self):
        result = []
        activos = self.get_gatos_activos()
        for gato in self.gatos.filter(muerto=False):
            if gato not in activos:
                result.append(gato)
        return result

    def get_avistamientos(self, date):
        vistos_set = {av.gato for av in self.avistamientos.filter(fecha=date)}
        gatos = self.get_gatos_activos()
        vistos = [x for x in gatos if x in vistos_set]
        no_vistos = [x for x in gatos if x not in vistos_set]
        return vistos, no_vistos

    def get_gatos_muertos(self):
        return self.gatos.filter(muerto=True)

    def get_calendarios(self):
        return ""

    def toggle_comida(self, fecha, user):
        comidas = self.comidas.filter(fecha=fecha).order_by('id')
        if not comidas:
            comida = AsignacionComida(fecha=fecha, usuario=user, colonia=self)
            comida.save()
        else:
            if comidas[0].usuario == user:
                comidas.delete()
            else:
                comidas[0].usuario = user
                comidas[0].save()

    def save(self, *args, **kwargs):
        if not self.slug:
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
        gatos = reduce(lambda x, y: x or y, gatos, False)
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
            self.exif = {TAGS.get(t, t): v for t, v in exif.items()}
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
    texto = models.TextField(blank=True, null=True)
    gatos = models.ManyToManyField("gatos.Gato", related_name="informes")

    def get_absolute_url(self):
        return reverse('informe', kwargs={"colonia": self.colonia.slug,
                                          "pk": self.id})

    def __repr__(self):
        c = self.__class__.__name__
        t = self.titulo
        f = self.fecha
        n = self.nombre_usuario
        return f"<{c} titulo='{t}' fecha={f} autor='{n}'>"

    def __str__(self):
        return f"{self.titulo}"


class Captura(UserBound):
    gato = models.ForeignKey("gatos.Gato", related_name="capturas",
                             on_delete=models.CASCADE)
    fecha_captura = models.DateField(auto_now=True)
    fecha_liberacion = models.DateField(null=True, default=None)
    peso = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    esterilizacion = models.BooleanField(default=False)
    observaciones = models.TextField(blank=True, default="")

    class Meta:
        permissions = [
                ("capturar_gato", ""),
                ("liberar_gato", ""),
                ]

    @property
    def capturado(self):
        return self.fecha_liberacion is None

    @property
    def liberado(self):
        return self.fecha_liberacion is not None

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
        return f"captura del gato {self.gato.nombre} el {self.fecha_captura}"


class Vacunacion(UserBound):
    captura = models.ForeignKey("gatos.Captura", related_name="vacunas",
                                on_delete=models.CASCADE)
    tipo = models.CharField(max_length=100,
                            choices=vacunas.get_choices())
    efecto = models.DurationField()

    class Meta:
        verbose_name_plural = "vacunaciones"
        permissions = [
                ("vacunar_gato", ""),
                ]

    @property
    def vacuna(self):
        return vacunas[self.tipo]

    @property
    def nombre(self):
        return self.vacuna.nombre

    @property
    def duracion(self):
        return self.vacuna.efecto

    @property
    def vacunacion(self):
        return self.fecha + self.duracion

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

    @property
    def curado(self):
        return self.fecha_curacion is None

    def __repr__(self):
        class_name = self.__class__.__name__
        name = self.gato.name
        nombre = self.nombre
        fecha = self.fecha_diagnostico
        return f"<{class_name} gato={name} nombre={nombre} fecha={fecha}>"

    def __str__(self):
        d = self.diagnostico
        g = self.gato.nombre
        f = self.fecha_diagnostico
        return f"enfermedad {d} del gato {g} el {f}"


class Avistamiento(UserBound):
    fecha = models.DateField(auto_now=True)
    gato = models.ForeignKey("gatos.Gato", on_delete=models.CASCADE,
                             related_name="avistamientos")
    colonia = models.ForeignKey("gatos.Colonia", on_delete=models.CASCADE,
                                related_name="avistamientos")

    class Meta:
        permissions = [
                ("avistar_gato", ""),
                ]

    def str(self):
        g = self.gato.nombre
        f = self.fecha.date
        u = self.usuario
        return f"Avistamiento de {g} el {f} por {u}."

    def __repr__(self):
        cls = self.__class__.__name__
        u = self.usuario.username
        g = self.gato.nombre
        f = self.fecha
        return f"<{cls} gato={g} usuario={u} fecha={f}>"


class AsignacionComida(models.Model):
    fecha = models.DateField()
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)
    colonia = models.ForeignKey("gatos.Colonia", on_delete=models.CASCADE,
                                related_name="comidas")

    def str(self):
        f = self.fecha
        u = self.usuario.username
        return f"Asignacion de dar comida el {f} a {u}"

    def __repr__(self):
        cls = self.__class__.__name__
        u = self.usuario.username
        f = self.fecha
        c = self.colonia.nombre
        return f"<{cls} usuario={u} fecha={f} colonia={c}>"

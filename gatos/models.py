import uuid
from django.urls import reverse
from django.db import models
from django.utils.text import slugify


class Gato(models.Model):
    slug = models.SlugField(max_length=200, unique=True, default="")
    nombre = models.CharField(max_length=200, unique=True)
    color = models.CharField(max_length=50)
    descripcion = models.TextField()
    colonia = models.ForeignKey("gatos.Colonia", on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("gato", kwargs={"colonia": self.colonia.slug,
                                       "gato": self.slug})

    def __unicode__(self):
        return self.nombre

    def __repr__(self):
        return f"<{self.__class__.__name__} nombre='{self.nombre}'>"


class Colonia(models.Model):
    slug = models.SlugField(max_length=200, default="")
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("colonia", kwargs={"colonia": self.slug})

    def __unicode__(self):
        return self.nombre

    def __repr__(self):
        return f"<{self.__class__.__name__} nombre='{self.nombre}'>"

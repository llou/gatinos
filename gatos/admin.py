from django.contrib import admin
from gatinos.admin import admin_site
from .models import (Gato, Colonia, Foto, Informe, Enfermedad, Vacunacion,
                     Captura)


class GatoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "colonia", "estado")

    def estado(self, obj):
        return obj.get_estado()


class ColoniaAdmin(admin.ModelAdmin):
    pass


class FotoAdmin(admin.ModelAdmin):
    list_display = ("fecha", "usuario", "colonia", "lista_de_gatos")

    def lista_de_gatos(self, obj):
        return ",".join([x.nombre for x in obj.gatos.all()])


class InformeAdmin(admin.ModelAdmin):
    list_display = ("titulo", "fecha_", "usuario", "colonia", "lista_de_gatos")

    def lista_de_gatos(self, obj):
        return ",".join([x.nombre for x in obj.gatos.all()])

    def fecha_(self, obj):
        return obj.fecha


class EnfermedadAdmin(admin.ModelAdmin):
    list_display = ("diagnostico", "fecha", "gato", "colonia")

    def colonia(self, obj):
        return obj.gato.colonia

    def fecha(self, obj):
        return obj.fecha_diagnostico


class VacunacionAdmin(admin.ModelAdmin):
    list_display = ("gato", "vacuna", "fecha", "colonia")

    def vacuna(self, obj):
        return obj.get_tipo_display()

    def fecha(self, obj):
        return obj.captura.fecha_captura

    def gato(self, obj):
        return obj.captura.gato

    def colonia(self, obj):
        return obj.captura.gato.colonia


class CapturaAdmin(admin.ModelAdmin):
    list_display = ("fecha", "gato", "activa", "colonia")

    def activa(self, obj):
        return obj.capturado

    def fecha(self, obj):
        return obj.fecha_captura

    def colonia(self, obj):
        return obj.gato.colonia


admin_site.register(Gato, GatoAdmin)
admin_site.register(Colonia, ColoniaAdmin)
admin_site.register(Foto, FotoAdmin)
admin_site.register(Informe, InformeAdmin)
admin_site.register(Enfermedad, EnfermedadAdmin)
admin_site.register(Vacunacion, VacunacionAdmin)
admin_site.register(Captura, CapturaAdmin)

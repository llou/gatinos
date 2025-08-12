from django.contrib import admin
from viewflow import fsm
from gatinos.admin import admin_site
from .models import (
        Gato,
        Colonia,
        Foto, Informe,
        Enfermedad,
        Vacunacion,
        Captura,
        Anuncio
        )
from .flows import GatoFlow


class GatoAdmin(fsm.FlowAdminMixin, admin.ModelAdmin):
    list_display = ("nombre", "colonia", "estado")
    readonly_fields = ('estado', )
    flow_state = GatoFlow.estado

    def get_object_flow(self, request, obj):
        return GatoFlow(obj)


class ColoniaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug', 'get_usuarios_count')
    filter_horizontal = ('usuarios_autorizados',)
    search_fields = ('nombre', 'descripcion')
    
    def get_usuarios_count(self, obj):
        return obj.usuarios_autorizados.count()
    get_usuarios_count.short_description = 'Usuarios autorizados'


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


class AnuncioAdmin(admin.ModelAdmin):
    list_display = ("mensaje", "hora_inicio", "hora_fin", "urgencia")

    def mensaje(self, obj):
        return obj.mensaje[:50]


admin_site.register(Gato, GatoAdmin)
admin_site.register(Colonia, ColoniaAdmin)
admin_site.register(Foto, FotoAdmin)
admin_site.register(Informe, InformeAdmin)
admin_site.register(Enfermedad, EnfermedadAdmin)
admin_site.register(Vacunacion, VacunacionAdmin)
admin_site.register(Captura, CapturaAdmin)
admin_site.register(Anuncio, AnuncioAdmin)

from django.contrib import admin
from gatinos.admin import admin_site
from .models import Gato, Colonia, Foto


class GatoAdmin(admin.ModelAdmin):
    pass


class ColoniaAdmin(admin.ModelAdmin):
    pass


class FotoAdmin(admin.ModelAdmin):
    pass


admin_site.register(Gato, GatoAdmin)
admin_site.register(Colonia, ColoniaAdmin)
admin_site.register(Foto, FotoAdmin)

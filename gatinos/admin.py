from django.contrib import admin
from django.contrib.auth.models import User, Group


class GatinosAdminSite(admin.AdminSite):
    site_title = ("Gatinos")
    site_header = ("Gatinos")
    index_header = ("Gatinos")


admin_site = GatinosAdminSite(name="gatinos_admin")


class UserAdmin(admin.ModelAdmin):
    pass


class GroupAdmin(admin.ModelAdmin):
    pass


admin_site.register(User, UserAdmin)
admin_site.register(Group, GroupAdmin)

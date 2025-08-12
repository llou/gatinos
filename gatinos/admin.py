from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django import forms
from django.core.exceptions import ValidationError
from gatos.models import Colonia


class GatinosAdminSite(admin.AdminSite):
    site_title = ("Gatinos")
    site_header = ("Gatinos")
    index_header = ("Gatinos")


admin_site = GatinosAdminSite(name="gatinos_admin")


class UserChangeForm(forms.ModelForm):
    """Custom form for User update with password change field"""
    password = ReadOnlyPasswordHashField(
        label="Contraseña",
        help_text="Las contraseñas no se almacenan en texto plano, por lo que no hay forma de ver "
                  "la contraseña de este usuario, pero puede cambiarla usando "
                  '<a href="../password/">este formulario</a>.'
    )
    
    colonias_autorizadas = forms.ModelMultipleChoiceField(
        queryset=Colonia.objects.all(),
        required=False,
        widget=admin.widgets.FilteredSelectMultiple(
            verbose_name='Colonias',
            is_stacked=False
        ),
        label="Colonias autorizadas",
        help_text="Seleccione las colonias a las que este usuario tendrá acceso"
    )
    
    class Meta:
        model = User
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['colonias_autorizadas'].initial = self.instance.colonias_autorizadas.all()
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        if user.pk:
            user.colonias_autorizadas.set(self.cleaned_data['colonias_autorizadas'])
        return user


class UserAdmin(BaseUserAdmin):
    """Custom User admin that removes last_login and adds password change"""
    form = UserChangeForm
    
    # Customize list display to remove last_login
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'get_colonias_count', 'date_joined')
    
    def get_colonias_count(self, obj):
        """Show count of authorized colonies"""
        return obj.colonias_autorizadas.count()
    get_colonias_count.short_description = 'Colonias'
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    
    # Customize fieldsets to remove last_login and organize better
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información personal', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Colonias', {'fields': ('colonias_autorizadas',)}),
        ('Fechas importantes', {'fields': ('date_joined',)}),
    )
    
    # For adding new users
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )
    
    # Make date_joined read-only
    readonly_fields = ('date_joined',)
    
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions',)


class GroupAdmin(admin.ModelAdmin):
    pass


admin_site.register(User, UserAdmin)
admin_site.register(Group, GroupAdmin)

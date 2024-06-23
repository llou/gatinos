from django.shortcuts import get_object_or_404
from django import forms
from .models import Foto, Gato, Colonia, Captura, Enfermedad, Informe


class ColoniaFotoForm(forms.ModelForm):
    class Meta:
        model = Foto
        fields = ["foto", "gatos", "colonia"]
        slug_field = "colonia"
        widgets = {
                'colonia': forms.HiddenInput()
                }

    gatos = forms.ModelMultipleChoiceField(
                widget=forms.CheckboxSelectMultiple,
                queryset=None,
                required=False
                )

    def __init__(self, *args, **kwargs):
        colonia = kwargs.pop("colonia")
        super().__init__(*args, **kwargs)
        self.fields["colonia"].initial = colonia
        self.fields["colonia"].widget.attrs['readonly'] = True
        self.fields["gatos"].queryset = colonia.gatos.all()


class GatoForm(forms.ModelForm):
    class Meta:
        model = Gato
        fields = ["nombre", "sexo", "descripcion", "color", "retrato"]

    retrato = forms.ModelChoiceField(required=False, queryset=None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["retrato"].queryset = self.instance.fotos.all()


class InformeForm(forms.ModelForm):
    class Meta:
        model = Informe
        fields = ["titulo", "texto", "gatos", "colonia"]
        slug_field = "colonia"
        widgets = {
                'colonia': forms.HiddenInput()
                }

    gatos = forms.ModelMultipleChoiceField(
                widget=forms.CheckboxSelectMultiple,
                queryset=None,
                required=False
                )

    def __init__(self, *args, **kwargs):
        colonia = kwargs.pop("colonia")
        super().__init__(*args, **kwargs)
        self.fields["colonia"].initial = colonia
        self.fields["colonia"].widget.attrs['readonly'] = True
        self.fields["gatos"].queryset = colonia.gatos.all()


class CapturaForm(forms.ModelForm):
    class Meta:
        model = Captura
        fields = ["observaciones", "peso"]


class EnfermedadForm(forms.ModelForm):
    class Meta:
        model = Enfermedad
        fields = ["observaciones"]

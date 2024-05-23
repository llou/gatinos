from django.shortcuts import get_object_or_404
from django import forms
from .models import Foto, Gato, Colonia


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
                queryset=Foto.objects.all(),
                required=False
                )

    def __init__(self, *args, **kwargs):
        slug = kwargs.pop("slug")
        super().__init__(*args, **kwargs)
        colonia = get_object_or_404(Colonia, slug=slug)
        self.fields["colonia"].initial = colonia
        self.fields["colonia"].widget.attrs['readonly'] = True
        self.fields["gatos"].queryset = Gato.objects.filter(colonia__slug=slug)

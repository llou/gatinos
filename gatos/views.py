from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import (DetailView, ListView, CreateView,
                                  DeleteView, UpdateView)
from .models import Gato, Colonia


class GatosView(ListView):
    template_name = "gatos/gatos.html"
    queryset = Gato.objects.all()
    context_object_name = "gatos"


class GatoView(DetailView):
    template_name = "gatos/gato.html"
    queryset = Gato.objects.all()
    fields = ["nombre", "color", "descripcion"]
    context_object_name = "gato"

    def get_context_data(self, *args, **kwargs):
        data = super().get_context_data(*args, **kwargs)
        colonia = get_object_or_404(Colonia, slug=self.kwargs["colonia"])
        data['colonia'] = colonia
        data['nuevo'] = False
        return data

    def get_object(self):
        colonia = get_object_or_404(Colonia,
                                    slug=self.kwargs['colonia'])
        gatos = Gato.objects.filter(colonia=colonia,
                                    slug=self.kwargs['gato'])
        return gatos[0] if gatos else None


class GatoCreateView(CreateView):
    template_name = "gatos/gato_form.html"
    model = Gato
    context_object_name = "gato"

    def get_context_data(self, *args, **kwargs):
        data = super().get_context_data(*args, **kwargs)
        colonia = get_object_or_404(Colonia, slug=self.kwargs["colonia"])
        data['colonia'] = colonia
        data['nuevo'] = True
        return data

    def form_valid(self, form):
        colonia = get_object_or_404(Colonia, slug=self.kwargs['colonia'])
        form.instance.colonia_id = colonia.id
        return super().form_valid(form)

    fields = ["nombre", "color", "descripcion"]


class GatoDeleteView(DeleteView):
    model = Gato
    context_object_name = "gato"

    def get_context_data(self, *args, **kwargs):
        data = super().get_context_data(*args, **kwargs)
        colonia = get_object_or_404(Colonia, slug=self.kwargs["colonia"])
        data['colonia'] = colonia
        return data

    def get_success_url(self):
        colonia = get_object_or_404(Colonia, slug=self.kwargs["colonia"])
        return reverse("colonia", kwargs={"colonia": colonia.slug})


class GatoUpdateView(UpdateView):
    model = Gato
    context_object_name = "gato"
    template_name = "gatos/gato_form.html"
    fields = "nombre", "descripcion", "color"

    def get_context_data(self, *args, **kwargs):
        data = super().get_context_data(*args, **kwargs)
        colonia = get_object_or_404(Colonia, slug=self.kwargs["colonia"])
        data['colonia'] = colonia
        data['nuevo'] = False
        return data


class ColoniasList(ListView):
    template_name = "gatos/colonias.html"
    queryset = Colonia.objects.all()
    context_object_name = "colonias"


class ColoniaView(DetailView):
    template_name = "gatos/colonia.html"
    queryset = Colonia.objects.all()
    context_object_name = "colonia"

    def get_context_data(self, *args, **kwargs):
        data = super().get_context_data(*args, **kwargs)
        data['gatos'] = Gato.objects.filter(colonia__slug=self.kwargs['colonia'])
        return data

    def get_object(self):
        return get_object_or_404(Colonia, slug=self.kwargs['colonia'])


class ColoniaCreateView(CreateView):
    model = Colonia
    fields = ["nombre", "descripcion"]
    success_url = reverse_lazy("colonias")
    context_object_name = "colonia"

    def get_context_data(self, *args, **kwargs):
        data = super().get_context_data(*args, **kwargs)
        data['nueva'] = True
        return data


class ColoniaDeleteView(DeleteView):
    model = Colonia
    context_object_name = "colonia"
    success_url = reverse_lazy("colonias")


class ColoniaUpdateView(UpdateView):
    model = Colonia
    fields = ["nombre", "descripcion"]
    context_object_name = "colonia"
    success_url = reverse_lazy("colonias")

    def get_context_data(self, *args, **kwargs):
        data = super().get_context_data(*args, **kwargs)
        data['nueva'] = True
        return data

from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (DetailView, ListView, CreateView,
                                  DeleteView, UpdateView)
from .models import Gato, Colonia, Foto
from .forms import ColoniaFotoForm


class BaseColoniaMixin:
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.colonia = get_object_or_404(Colonia, slug=self.kwargs['colonia'])


class SubColoniaMixin(BaseColoniaMixin):
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['colonia'] = self.colonia
        return data

    def get_success_url(self):
        return self.colonia.get_absolute_url()


class ColoniaMixin(BaseColoniaMixin):
    def get_object(self):
        return self.colonia


class GatoMixin:
    gato_slug = "gato"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.gato = get_object_or_404(Gato, slug=self.kwargs[self.gato_slug])

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['gato'] = self.gato
        return data

    def get_object(self):
        return self.gato


class FotoMixin:
    foto_uuid = "foto"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.foto = get_object_or_404(Foto, uuid=self.kwargs[self.foto_uuid])

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['foto'] = self.foto
        return data

    def get_object(self):
        return self.foto


class ColoniasList(ListView):
    template_name = "gatos/colonias.html"
    queryset = Colonia.objects.all()
    context_object_name = "colonias"


class ColoniaView(ColoniaMixin, DetailView):
    template_name = "gatos/colonia.html"
    queryset = Colonia.objects.all()

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        colonia = self.get_object()
        data['gatos'] = colonia.gatos.all()
        data['fotos'] = colonia.fotos.all()
        return data


class ColoniaCreateView(CreateView):
    template_name = "gatos/colonia_new.html"
    model = Colonia
    fields = ["nombre", "descripcion"]


class ColoniaDeleteView(ColoniaMixin, DeleteView):
    model = Colonia
    success_url = reverse_lazy("colonias")


class ColoniaUpdateView(ColoniaMixin, UpdateView):
    template_name = "gatos/colonia_update.html"
    model = Colonia
    fields = ["nombre", "descripcion"]


class GatosView(SubColoniaMixin, ListView):
    template_name = "gatos/gatos.html"
    queryset = Gato.objects.all()


class GatoView(SubColoniaMixin, GatoMixin, DetailView):
    template_name = "gatos/gato.html"
    queryset = Gato.objects.all()
    fields = ["nombre", "color", "descripcion"]


class GatoCreateView(SubColoniaMixin, CreateView):
    template_name = "gatos/gato_new.html"
    model = Gato
    fields = ["nombre", "sexo", "color", "descripcion"]

    def form_valid(self, form):
        form.instance.colonia_id = self.colonia.id
        return super().form_valid(form)


class GatoDeleteView(GatoMixin, SubColoniaMixin, DeleteView):
    model = Gato


class GatoUpdateView(GatoMixin, SubColoniaMixin, UpdateView):
    model = Gato
    context_object_name = "gato"
    template_name = "gatos/gato_update.html"
    fields = "nombre", "descripcion", "sexo", "color", "retrato"


class FotoCreateView(SubColoniaMixin, CreateView):
    template_name = "gatos/foto_create.html"
    model = Foto
    form_class = ColoniaFotoForm

    # Relleno previo de los datos del formulario para no tener que rellenar
    # el campo colonia ya que este aparece.
    def get_initial(self):
        initial = super().get_initial()
        initial['colonia'] = self.colonia
        return initial

    # Pasa el objeto colonia para poder acceder a los datos de la colonia
    # cuando se genere el queryset de los gatos que aparecen en la foto.
    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs["colonia"] = self.colonia
        return form_kwargs


class FotoView(SubColoniaMixin, FotoMixin, DetailView):
    template_name = "gatos/foto.html"
    queryset = Foto.objects.select_related("colonia").all()
    context_name = "foto"


class FotosView(SubColoniaMixin, ListView):
    template_name = "gatos/fotos.html"
    queryset = Foto.objects.all()
    context_name = "fotos"


class FotoUpdateView(SubColoniaMixin, FotoMixin, UpdateView):
    model = Foto
    template_name = "gatos/foto_update.html"
    context_name = "foto"
    form_class = ColoniaFotoForm

    # Pasa el objeto colonia para poder acceder a los datos de la colonia
    # cuando se genere el queryset de los gatos que aparecen en la foto.
    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs["colonia"] = self.colonia
        return form_kwargs


class FotoDeleteView(SubColoniaMixin, FotoMixin, DeleteView):
    model = Foto
    context_object_name = "foto"

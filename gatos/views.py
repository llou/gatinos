from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import (DetailView, ListView, CreateView,
                                  DeleteView, UpdateView)
from .models import Gato, Colonia, Foto
from .forms import ColoniaFotoForm


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
        data['gatos'] = self.object.gatos.all()
        data['fotos'] = self.object.fotos.all()
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


class ColoniaUpdateView(UpdateView):
    model = Colonia
    fields = ["nombre", "descripcion"]
    context_object_name = "colonia"
    success_url = reverse_lazy("colonias")

    def get_context_data(self, *args, **kwargs):
        data = super().get_context_data(*args, **kwargs)
        data['nueva'] = True
        return data


class FotoCreateView(CreateView):
    model = Foto
    form_class = ColoniaFotoForm

    # Relleno previo de los datos del formulario para no tener que rellenar
    # el campo colonia ya que este aparece.
    def get_initial(self):
        initial = super().get_initial()
        slug = self.kwargs['colonia']
        colonia = get_object_or_404(Colonia, slug=slug)
        initial['colonia'] = colonia
        return initial

    # Pasa el objeto colonia para poder acceder a los datos de la colonia
    # cuando se genere el queryset de los gatos que aparecen en la foto.
    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs["slug"] = self.kwargs['colonia']
        return form_kwargs

    # Pasar el objeto colonia a la plantilla para poder acceder al reverse
    # al enviar el formulario.
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        colonia = get_object_or_404(Colonia, slug=self.kwargs['colonia'])
        data['colonia'] = colonia
        return data

    def get_success_url(self):
        return reverse("colonia", kwargs={"colonia": self.kwargs["colonia"]})


class FotoView(DetailView):
    template_name = "gatos/foto.html"
    queryset = Foto.objects.select_related("colonia").all()
    context_name = "foto"

    def get_object(self):
        fotos = Foto.objects.filter(colonia__slug=self.kwargs['colonia'],
                                    uuid=self.kwargs['foto'])
        return fotos[0] if fotos else None

    def get_context_data(self, *args, **kwargs):
        data = super().get_context_data()
        foto = kwargs['object']
        data['gatos'] = foto.gatos.all()
        return data


class FotosView(ListView):
    template_name = "gatos/fotos.html"
    queryset = Foto.objects.all()
    context_name = "fotos"


class FotoUpdateView(UpdateView):
    model = Foto
    template_name = "gatos/foto_update.html"
    context_name = "foto"
    fields = ['descripcion', 'gatos']

    def get_object(self):
        fotos = Foto.objects.filter(colonia__slug=self.kwargs['colonia'],
                                    uuid=self.kwargs['foto'])
        return fotos[0] if fotos else None


class FotoDeleteView(DeleteView):
    model = Foto
    context_object_name = "foto"

    def get_success_url(self):
        return reverse("colonia", kwargs={"colonia": self.kwargs["colonia"]})

    def get_object(self):
        fotos = Foto.objects.filter(colonia__slug=self.kwargs['colonia'],
                                    uuid=self.kwargs['foto'])
        return fotos[0] if fotos else None



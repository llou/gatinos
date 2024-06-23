from datetime import date
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin as PRMixin
from django.views.generic import (DetailView, ListView, CreateView,
                                  DeleteView, UpdateView)
from .models import Gato, Colonia, Foto, Enfermedad, Captura, Informe
from .forms import (ColoniaFotoForm, GatoForm, CapturaForm, EnfermedadForm,
                    InformeForm)
from . import tasks


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
        data['gatos'] = self.foto.gatos.all()
        return data

    def get_object(self):
        return self.foto


class InformeMixin:
    informe_pk = "pk"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.informe = get_object_or_404(Informe, pk=self.kwargs[self.informe_pk])

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['informe'] = self.informe
        data['gatos'] = self.informe.gatos.all()
        return data

    def get_object(self):
        return self.informe


class ColoniasList(PRMixin, ListView):
    template_name = "gatos/colonias.html"
    queryset = Colonia.objects.all()
    context_object_name = "colonias"
    permission_required = "gatos.view_colonia"


class ColoniaView(PRMixin, ColoniaMixin, DetailView):
    template_name = "gatos/colonia.html"
    queryset = Colonia.objects.all()
    permission_required = "gatos.view_colonia"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        colonia = self.get_object()
        data['gatos'] = colonia.gatos.order_by("nombre").all().select_related("retrato")
        data['fotos'] = colonia.fotos.order_by("fecha").all()[:20]
        data['informes'] = colonia.informes.order_by("fecha").all()[:20]
        return data


class ColoniaCreateView(PRMixin, CreateView):
    template_name = "gatos/colonia_new.html"
    model = Colonia
    fields = ["nombre", "descripcion"]
    permission_required = "gatos.create_colonia"


class ColoniaDeleteView(PRMixin, ColoniaMixin, DeleteView):
    model = Colonia
    success_url = reverse_lazy("colonias")
    permission_required = "gatos.delete_colonia"


class ColoniaUpdateView(PRMixin, ColoniaMixin, UpdateView):
    template_name = "gatos/colonia_update.html"
    model = Colonia
    fields = ["nombre", "descripcion"]
    permission_required = "gatos.update_colonia"


class GatosView(PRMixin, SubColoniaMixin, ListView):
    template_name = "gatos/gatos.html"
    queryset = Gato.objects.all()
    permission_required = "gatos.view_gato"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['eventos'] = [x[0].lower() for x in models.EVENTOS_GATO]
        return data


class GatoView(PRMixin, SubColoniaMixin, GatoMixin, DetailView):
    template_name = "gatos/gato.html"
    queryset = Gato.objects.all()
    fields = ["nombre", "color", "descripcion"]
    permission_required = "gatos.view_gato"


class GatoCreateView(PRMixin, SubColoniaMixin, CreateView):
    template_name = "gatos/gato_new.html"
    model = Gato
    fields = ["nombre", "sexo", "color", "descripcion"]
    permission_required = "gatos.create_gato"

    def form_valid(self, form):
        form.instance.colonia_id = self.colonia.id
        return super().form_valid(form)


class GatoDeleteView(PRMixin, GatoMixin, SubColoniaMixin, DeleteView):
    model = Gato
    permission_required = "gatos.delete_gato"


class GatoUpdateView(PRMixin, GatoMixin, SubColoniaMixin, UpdateView):
    model = Gato
    context_object_name = "gato"
    template_name = "gatos/gato_update.html"
    form_class = GatoForm
    permission_required = "gatos.update_gato"


class FotoCreateView(PRMixin, SubColoniaMixin, CreateView):
    template_name = "gatos/foto_create.html"
    model = Foto
    form_class = ColoniaFotoForm
    permission_required = "gatos.create_foto"

    # Relleno previo de los datos del formulario para no tener que rellenar
    # el campo colonia ya que este aparece.
    # XXX Borrar esto porque ya esta en SubColoniaMixin
    def get_initial(self):
        initial = super().get_initial()
        initial['colonia'] = self.colonia
        return initial

    # Pasa el objeto colonia para poder acceder a los datos de la colonia
    # cuando se genere el queryset de los gatos que aparecen en la foto.
    # XXX Borrar esto porque ya esta en SubColoniaMixin
    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs["colonia"] = self.colonia
        return form_kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        tasks.process_image.delay(form.instance.uuid)
        return response


class FotoView(PRMixin, SubColoniaMixin, FotoMixin, DetailView):
    template_name = "gatos/foto.html"
    queryset = Foto.objects.select_related("colonia").all()
    context_name = "foto"
    permission_required = "gatos.view_foto"


class FotosView(PRMixin, SubColoniaMixin, ListView):
    template_name = "gatos/fotos.html"
    context_name = "fotos"
    permission_required = "gatos.view_foto"

    def get_queryset(self):
        return self.colonia.fotos.all()


class FotoUpdateView(PRMixin, SubColoniaMixin, FotoMixin, UpdateView):
    model = Foto
    template_name = "gatos/foto_update.html"
    context_name = "foto"
    form_class = ColoniaFotoForm
    permission_required = "gatos.update_foto"

    # Pasa el objeto colonia para poder acceder a los datos de la colonia
    # cuando se genere el queryset de los gatos que aparecen en la foto.
    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs["colonia"] = self.colonia
        return form_kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        tasks.process_image.delay(form.instance.uuid)
        return response


class FotoDeleteView(PRMixin, SubColoniaMixin, FotoMixin, DeleteView):
    model = Foto
    context_object_name = "foto"
    permission_required = "gatos.delete_foto"

# TODO Gato y Colonia Events


class BaseInformeView(SubColoniaMixin):
    model = Informe
    context_name = "informe"


class InformeView(BaseInformeView, DetailView):
    template_name = "gatos/informe.html"


class InformeCreateView(PRMixin, SubColoniaMixin, CreateView):
    template_name = "gatos/informe_create.html"
    model = Informe
    form_class = InformeForm
    permission_required = "gatos.create_informe"

    # Relleno previo de los datos del formulario para no tener que rellenar
    # el campo colonia ya que este aparece.
    # XXX Borrar esto porque ya esta en SubColoniaMixin
    def get_initial(self):
        initial = super().get_initial()
        initial['colonia'] = self.colonia
        return initial

    # Pasa el objeto colonia para poder acceder a los datos de la colonia
    # cuando se genere el queryset de los gatos que aparecen en la foto.
    # XXX Borrar esto porque ya esta en SubColoniaMixin
    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs["colonia"] = self.colonia
        return form_kwargs


class InformeUpdateView(PRMixin, SubColoniaMixin, InformeMixin, UpdateView):
    model = Informe
    template_name = "gatos/informe_update.html"
    context_name = "informe"
    form_class = InformeForm
    permission_required = "gatos.update_informe"

    # Pasa el objeto colonia para poder acceder a los datos de la colonia
    # cuando se genere el queryset de los gatos que aparecen en la foto.
    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs["colonia"] = self.colonia
        return form_kwargs


class InformeDeleteView(BaseInformeView, DeleteView):
    pass


class CapturaBaseView(GatoMixin, SubColoniaMixin):
    model = Captura


def capturar_gato(request, colonia_slug, gato_slug):
    colonia = get_object_or_404(Colonia, slug=colonia_slug)
    gato = get_object_or_404(Gato, colonia=colonia, slug=gato_slug)
    if gato.capturado:
        return render(request, "gatos/mensaje.html", {
                          "colonia": colonia,
                          "gato": gato,
                          "mensaje": "Gato ya capturado."})
    if bool(request['GET'].get("confirmado", False)):
        captura = Captura(gato=gato, fecha_captura=date.today(), peso=None)
        captura.save()
        return HttpResponseRedirect(gato.get_absolute_url())
    mensaje = f"¿Seguro que ha capturado al gato {gato.nombre}?"
    url = reverse("capturar", gato=gato.slug, colonia=colonia.slug)
    url += "?confirmado=True"
    return render(request, "gatos/confirmacion.html", {"colonia": colonia,
                  "gato": gato, "mensaje": mensaje, "url": url})


def liberar_gato(request, colonia_slug, gato_slug):
    colonia = get_object_or_404(Colonia, slug=colonia_slug)
    gato = get_object_or_404(Gato, colonia=colonia, slug=gato_slug)
    if not gato.capturado:
        return render(request, "gatos/mensaje.html", {
                          "colonia": colonia,
                          "gato": gato,
                          "mensaje": "Gato no capturado"})

    if bool(request['GET'].get("confirmado", False)):
        captura = Captura(gato=gato, fecha_captura=date.today(), peso=None)
        captura.save()
        return HttpResponseRedirect(gato.get_absolute_url())
    mensaje = f"¿Seguro que ha capturado al gato {gato.nombre}?"
    url = reverse("capturar", gato=gato.slug, colonia=colonia.slug)
    url += "?confirmado=True"
    return render(request, "gatos/confirmacion.html", {"gato": gato,
                  "colonia": colonia, "mensaje": mensaje, "url": url})


class CapturaView(CapturaBaseView, DetailView):
    template_name = "gatos/captura_view.html"
    context_name = "captura"


class CapturaCreateView(CapturaBaseView, CreateView):
    template_name = "gatos/captura_create_view.html"
    form_class = CapturaForm
    context_name = "captura"


class CapturaUpdateView(CapturaBaseView, UpdateView):
    template_name = "gatos/captura_update_view.html"
    form_class = CapturaForm
    context_name = "captura"


class CapturaDeleteView(CapturaBaseView, DeleteView):
    context_object_name = "captura"


class EnfermedadBaseView(GatoMixin, SubColoniaMixin):
    model = Enfermedad


class EnfermedadView(EnfermedadBaseView, DetailView):
    template_name = "gatos/enfermedad_view.html"
    context_name = "enfermedad"


class EnfermedadCreateView(EnfermedadBaseView, CreateView):
    template_name = "gatos/enfermedad_create_view.html"
    form_class = EnfermedadForm
    context_name = "enfermedad"


class EnfermedadUpdateView(EnfermedadBaseView, UpdateView):
    template_name = "gatos/enfermedad_update_view.html"
    form_class = EnfermedadForm
    context_name = "enfermedad"


class EnfermedadDeleteView(EnfermedadBaseView, DeleteView):
    context_object_name = "enfermedad"


class ColoniaBaseEventView(SubColoniaMixin, ColoniaMixin, CreateView):

    def get_success_url(self):
        return self.colonia.get_absolute_url()

# Acciones Provisionales


def update_miniaturas(request, colonia="ponte"):
    tasks.update_miniaturas.delay(colonia)
    return HttpResponse("Ok, Updating Miniaturas")


def update_exifs(request, colonia="ponte"):
    c = get_object_or_404(Colonia, slug=colonia)
    tasks.update_exifs.delay(c.slug)
    return HttpResponse("Ok, Updating Exifs")

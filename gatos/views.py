from datetime import date
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin as PRMixin
from django.views import View
from django.views.generic import (DetailView, ListView, CreateView,
                                  DeleteView, UpdateView)
from .models import Gato, Colonia, Foto, Enfermedad, Captura, Informe
from .forms import (ColoniaFotoForm, GatoForm, CapturaForm, InformeForm,
                    EnfermedadCreateForm, EnfermedadUpdateForm,
                    VacunarGatoForm)
from . import tasks


class ConfirmationView(View):
    confirmation_key = "confirmation"
    cancel_key = "cancel"
    question = "Are you sure?"
    template = "confirmation.html"

    def confirm(self):
        return HttpResponse("confirmed")

    def cancel(self):
        return HttpResponse("canceled")

    def get_question(self):
        return self.question

    def get_path(self):
        return self.request.path_info

    def get_confirmation_uri(self):
        return self.get_path() + "?" + self.confirmation_key

    def get_cancel_uri(self):
        return self.get_path() + "?" + self.cancel_key

    def get_context(self):
        return {
            "question": self.get_question(),
            "confirmation_uri": self.get_confirmation_uri(),
            "cancel_uri": self.get_cancel_uri()
            }

    def get(self, request, *args, **kwargs):
        if self.confirmation_key in request.GET:
            return self.confirm()
        elif self.cancel_key in request.GET:
            return self.cancel()
        else:
            return render(request, self.template, self.get_context())


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


class BaseGatoMixin:
    gato_slug = "gato"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.gato = get_object_or_404(Gato, slug=self.kwargs[self.gato_slug])
        self.ultima_captura = self.gato.get_ultima_captura()
        self.peso = self.gato.get_peso()
        self.enfermedades = self.gato.enfermedades.all()
        self.capturas = self.gato.capturas.order_by("-fecha_captura").select_related("gato__colonia").all()[:5]
        self.vacunas = self.gato.get_vacunas()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ultima_captura'] = self.ultima_captura
        context['enfermedades'] = self.enfermedades
        context['peso'] = self.peso
        context['capturas'] = self.capturas
        context['vacunas'] = self.vacunas
        return context


class SubGatoMixin(BaseGatoMixin):
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['gato'] = self.gato
        return data

    def get_success_url(self):
        return self.gato.get_absolute_url()


class GatoMixin(BaseGatoMixin):
    def get_object(self):
        return self.gato


class BaseCapturaMixin:
    captura_pk = "pk"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.captura = get_object_or_404(Captura, id=kwargs[self.captura_pk])


class SubCapturaMixin(BaseCapturaMixin):
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        print(data)
        data['captura'] = self.captura
        return data

    def get_success_url(self):
        return self.captura.gato.get_absolute_url()


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
        self.informe = get_object_or_404(Informe,
                                         pk=self.kwargs[self.informe_pk])

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['informe'] = self.informe
        data['gatos'] = self.informe.gatos.all()
        return data

    def get_object(self):
        return self.informe

# ------------------------------------------------------------------------

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


class ColoniaUpdateView(PRMixin, ColoniaMixin, UpdateView):
    template_name = "gatos/colonia_update.html"
    model = Colonia
    fields = ["nombre", "descripcion"]
    permission_required = "gatos.update_colonia"


class ColoniaDeleteView(PRMixin, ColoniaMixin, DeleteView):
    model = Colonia
    success_url = reverse_lazy("colonias")
    permission_required = "gatos.delete_colonia"


# ------------------------------------------------------------------------


class GatosView(PRMixin, SubColoniaMixin, ListView):
    template_name = "gatos/gatos.html"
    queryset = Gato.objects.all()
    permission_required = "gatos.view_gato"


class GatoView(PRMixin, SubColoniaMixin, GatoMixin, DetailView):
    template_name = "gatos/gato.html"
    queryset = Gato.objects.all()
    permission_required = "gatos.view_gato"


class GatoCreateView(PRMixin, SubColoniaMixin, CreateView):
    template_name = "gatos/gato_new.html"
    model = Gato
    fields = ["nombre", "sexo", "color", "descripcion"]
    permission_required = "gatos.create_gato"

    def form_valid(self, form):
        form.instance.colonia_id = self.colonia.id
        return super().form_valid(form)


class GatoUpdateView(PRMixin, GatoMixin, SubColoniaMixin, UpdateView):
    model = Gato
    context_object_name = "gato"
    template_name = "gatos/gato_update.html"
    form_class = GatoForm
    permission_required = "gatos.update_gato"


class GatoDeleteView(PRMixin, GatoMixin, SubColoniaMixin, DeleteView):
    model = Gato
    permission_required = "gatos.delete_gato"


# ------------------------------------------------------------------------


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


# ------------------------------------------------------------------------


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


# ------------------------------------------------------------------------


class CapturaBaseMixin(SubGatoMixin, SubColoniaMixin):
    model = Captura

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.captura = get_object_or_404(Captura, id=kwargs['pk'])

    def get_object(self):
        return self.captura

    def get_success_url(self):
        return self.gato.get_absolute_url()


class GatoConfirmationView(ConfirmationView):
    template = "gatos/gato_confirmacion.html"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.colonia = get_object_or_404(Colonia, slug=self.kwargs['colonia'])
        self.gato = get_object_or_404(Gato, colonia=self.colonia,
                                      slug=self.kwargs['gato'])
        self.ultima_captura = self.gato.get_ultima_captura()

    def get_context(self):
        context = super().get_context()
        context['colonia'] = self.colonia
        context['gato'] = self.gato
        context['captura'] = self.ultima_captura
        return context

# TODO Aqui hay un problema con la ultima captura


class CapturarGato(GatoConfirmationView):
    def get_question(self):
        return f"¿Seguro que ha capturado al gato '{self.gato}'?"

    def confirm(self):
        if self.ultima_captura is None:
            captura = Captura(gato=self.gato, fecha_captura=date.today())
            captura.save()
        else:
            raise RuntimeError("No puede ser esto")
        return HttpResponseRedirect(self.gato.get_absolute_url())

    def cancel(self):
        return HttpResponseRedirect(self.gato.get_absolute_url())


class LiberarGato(GatoConfirmationView):
    def get_question(self):
        return f"¿Seguro que ha liberado al gato '{self.gato}'?"

    def confirm(self):
        if self.gato.capturado:
            captura = self.gato.get_ultima_captura()
            captura.fecha_liberacion = date.today()
            captura.save()
        return HttpResponseRedirect(self.gato.get_absolute_url())

    def cancel(self):
        return HttpResponseRedirect(self.gato.get_absolute_url())


class CapturaView(CapturaBaseMixin, DetailView):
    template_name = "gatos/captura_view.html"
    context_name = "captura"


class CapturaUpdateView(CapturaBaseMixin, UpdateView):
    template_name = "gatos/captura_update_view.html"
    form_class = CapturaForm


class CapturaDeleteView(CapturaBaseMixin, DeleteView):
    context_object_name = "captura"


# ------------------------------------------------------------------------


class EnfermedadBaseView(SubGatoMixin, SubColoniaMixin):
    model = Enfermedad
    context_name = "enfermedad"


class EnfermedadView(EnfermedadBaseView, DetailView):
    template_name = "gatos/enfermedad.html"


class EnfermedadCreateView(EnfermedadBaseView, CreateView):
    template_name = "gatos/enfermedad_create_view.html"
    form_class = EnfermedadCreateForm

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs["gato"] = self.gato
        return form_kwargs

    def get_success_url(self):
        return self.gato.get_absolute_url()


class EnfermedadUpdateView(EnfermedadBaseView, UpdateView):
    template_name = "gatos/enfermedad_update_view.html"
    form_class = EnfermedadUpdateForm


class EnfermedadDeleteView(EnfermedadBaseView, DeleteView):
    template = "gatos/enfermedad_confirm_delete.html"


# ------------------------------------------------------------------------


class VacunarGato(SubColoniaMixin, SubGatoMixin, SubCapturaMixin, CreateView):
    template_name = "gatos/vacunar_gato.html"
    form_class = VacunarGatoForm

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs["captura"] = self.captura
        return form_kwargs

    def get_success_url(self):
        return self.captura.gato.get_absolute_url()



# ------------------------------------------------------------------------
#                Acciones Provisionales
# ------------------------------------------------------------------------


def update_miniaturas(request, colonia="ponte"):
    tasks.update_miniaturas.delay(colonia)
    return HttpResponse("Ok, Updating Miniaturas")


def update_exifs(request, colonia="ponte"):
    c = get_object_or_404(Colonia, slug=colonia)
    tasks.update_exifs.delay(c.slug)
    return HttpResponse("Ok, Updating Exifs")

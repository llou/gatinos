from datetime import date, datetime
from htmlcalendar import htmlcalendar
from icalendar import Calendar, Event as IcalEvent
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.contrib.auth.mixins import PermissionRequiredMixin as PRMixin
from django.views import View
from django.views.generic import (DetailView,
                                  ListView,
                                  CreateView,
                                  DeleteView,
                                  UpdateView,
                                  TemplateView,
                                  )
from plottings import PNGPlotView
from .models import (Gato,
                     Colonia,
                     Foto,
                     Enfermedad,
                     Captura,
                     Informe,
                     Vacunacion,
                     Avistamiento,
                     CodigoCalendarioComidas,
                     )
from .forms import (FotoCreateForm,
                    FotoEditForm,
                    GatoForm,
                    CapturaForm,
                    InformeForm,
                    EnfermedadCreateForm,
                    EnfermedadUpdateForm,
                    VacunarGatoForm
                    )
from .plots import activity_plot, SpanishActivityMap, get_svg_qrcode
from .utils import Agrupador
from .flows import GatoFlow
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


class CommandView(TemplateView):
    def run_command(self, request, *args, **kwargs):
        pass

    def get(self, request, *args, **kwargs):
        self.run_command(request, *args, **kwargs)
        return super().get(request, *args, **kwargs)


class GatoConfirmationView(ConfirmationView):
    template = "gatos/gato_confirmacion.html"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.colonia = get_object_or_404(Colonia, slug=self.kwargs['colonia'])
        self.gato = get_object_or_404(Gato, colonia=self.colonia,
                                      slug=self.kwargs['gato'])

    def get_context(self):
        context = super().get_context()
        context['colonia'] = self.colonia
        context['gato'] = self.gato
        capturas = self.gato.capturas.order_by("-fecha_captura")
        context['captura'] = capturas[0] if capturas else None
        return context

# TODO Aqui hay un problema con la ultima captura


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
        self.capturas = self.gato.capturas.order_by('fecha_captura')
        self.ultima_captura = self.capturas[0] if self.capturas else None
        self.peso = self.gato.get_peso()
        self.enfermedades = self.gato.enfermedades.all()
        capturas = self.gato.capturas.order_by("-fecha_captura")
        self.capturas = capturas.select_related("gato__colonia").all()[:5]
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
        data['captura'] = self.captura
        return data

    def get_success_url(self):
        return self.captura.gato.get_absolute_url()


class FotoMixin:
    foto_id = "foto"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.foto = get_object_or_404(Foto, id=self.kwargs[self.foto_id])

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


class UserBoundMixin:
    usuario_field = "usuario"

    def form_valid(self, form):
        result = super().form_valid(form)
        self.object.usuario = self.request.user
        self.object.save()
        return result

# ------------------------------------------------------------------------


class ColoniasList(PRMixin, ListView):
    permission_required = "gatos.view_colonia"
    template_name = "gatos/colonias.html"
    queryset = Colonia.objects.all()
    context_object_name = "colonias"


class ColoniaView(PRMixin, ColoniaMixin, DetailView):
    permission_required = "gatos.view_colonia"
    template_name = "gatos/colonia.html"
    queryset = Colonia.objects.all()
    class_otro = "comidas-otro"
    class_usuario = "comidas-usuario"
    class_none = "comidas-none"

    def get_calendars(self):
        comidas = {c.fecha: c for c in self.colonia.comidas.all()}

        def classes(f):
            if f not in comidas:
                return ["comidas-none"]
            elif comidas[f].usuario == self.request.user:
                return ["comidas-usuario"]
            else:
                return ["comidas-otro"]

        return htmlcalendar(date.today(), months=2, backwards=False,
                            classes=classes, header="h2", th_classes=[])

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['gatos'] = self.colonia.get_gatos_activos()
        data['fotos'] = self.colonia.fotos.order_by("fecha").all()[:20]
        data['informes'] = self.colonia.informes.order_by("fecha").all()[:20]
        data['calendarios'] = self.get_calendars()
        return data


class ColoniaCreateView(PRMixin, CreateView):
    permission_required = "gatos.add_colonia"
    template_name = "gatos/colonia_new.html"
    model = Colonia
    fields = ["nombre", "descripcion"]


class ColoniaUpdateView(PRMixin, ColoniaMixin, UpdateView):
    permission_required = "gatos.change_colonia"
    template_name = "gatos/colonia_update.html"
    model = Colonia
    fields = ["nombre", "periodo_activo", "descripcion"]


# ------------------------------------------------------------------------


class GatosView(PRMixin, SubColoniaMixin, ListView):
    permission_required = "gatos.view_gato"
    template_name = "gatos/gatos.html"
    context_object_name = "gatos"
    valid_estados = ["activos", "desaparecidos", "muertos"]

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.estado = self.request.GET.get("estado", "activos")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['estado'] = self.estado
        return context

    def get_queryset(self):
        if self.estado == "activos":
            return self.colonia.get_gatos_activos()
        elif self.estado == "desaparecidos":
            return self.colonia.get_gatos_desaparecidos()
        elif self.estado == "muertos":
            return self.colonia.gatos.filter(muerto=True)
        else:
            return self.colonia.get_gatos_activos()


class GatoView(PRMixin, SubColoniaMixin, GatoMixin, DetailView):
    permission_required = "gatos.view_gato"
    template_name = "gatos/gato.html"
    queryset = Gato.gatos_colonia

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['estado'] = self.gato.estado
        context['informes'] = self.gato.informes.all()
        return context


class GatoCreateView(PRMixin, SubColoniaMixin, CreateView):
    permission_required = "gatos.add_gato"
    template_name = "gatos/gato_new.html"
    model = Gato
    fields = ["nombre", "sexo", "color", "descripcion", "feo", "vecino",
              "nombre_vecino"]

    def form_valid(self, form):
        form.instance.colonia_id = self.colonia.id
        return super().form_valid(form)


class GatoUpdateView(PRMixin, GatoMixin, SubColoniaMixin, UpdateView):
    permission_required = "gatos.change_gato"
    model = Gato
    context_object_name = "gato"
    template_name = "gatos/gato_update.html"
    form_class = GatoForm


# ------------------------------------------------------------------------


class FotoCreateView(PRMixin, UserBoundMixin, SubColoniaMixin, CreateView):
    permission_required = "gatos.add_foto"
    template_name = "gatos/foto_create.html"
    model = Foto
    form_class = FotoCreateForm

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
        tasks.process_image.delay(form.instance.id)
        return response


class FotoView(PRMixin, SubColoniaMixin, FotoMixin, DetailView):
    permission_required = "gatos.view_foto"
    template_name = "gatos/foto.html"
    queryset = Foto.objects.select_related("colonia").all()
    context_name = "foto"


class FotosView(PRMixin, SubColoniaMixin, ListView):
    permission_required = "gatos.view_foto"
    template_name = "gatos/fotos.html"
    context_object_name = "fotos"

    def get_queryset(self):
        return self.colonia.fotos.all()


class FotoUpdateView(PRMixin, UserBoundMixin, SubColoniaMixin, FotoMixin,
                     UpdateView):
    permission_required = "gatos.change_foto"
    model = Foto
    template_name = "gatos/foto_update.html"
    context_name = "foto"
    form_class = FotoEditForm

    # Pasa el objeto colonia para poder acceder a los datos de la colonia
    # cuando se genere el queryset de los gatos que aparecen en la foto.
    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs["colonia"] = self.colonia
        return form_kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        tasks.process_image.delay(form.instance.id)
        return response


class FotoDeleteView(PRMixin, SubColoniaMixin, FotoMixin, DeleteView):
    permission_required = "gatos.delete_foto"
    model = Foto
    context_object_name = "foto"

# TODO Gato y Colonia Events


# ------------------------------------------------------------------------


class BaseInformeView(SubColoniaMixin):
    model = Informe
    context_name = "informe"


class AgrupadorDeInformes(Agrupador):

    @staticmethod
    def get_value(item):
        return date(item.fecha.year, item.fecha.month, 1)


class InformesView(PRMixin, SubColoniaMixin, TemplateView):
    permission_required = "gatos.view_informe"
    template_name = "gatos/informes.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        informes = self.colonia.informes.all().order_by("-fecha")
        context['agrupador'] = AgrupadorDeInformes(informes)
        return context


class InformeView(PRMixin, BaseInformeView, InformeMixin, DetailView):
    permission_required = "gatos.view_informe"
    template_name = "gatos/informe.html"


class InformeCreateView(PRMixin, UserBoundMixin, SubColoniaMixin, CreateView):
    permission_required = "gatos.add_informe"
    template_name = "gatos/informe_create.html"
    model = Informe
    form_class = InformeForm

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

    def get_success_url(self):
        return reverse("informe", kwargs={"colonia": self.colonia.slug,
                                          "pk": self.object.id})


class InformeUpdateView(PRMixin, UserBoundMixin, SubColoniaMixin,
                        InformeMixin, UpdateView):
    permission_required = "gatos.change_informe"
    model = Informe
    template_name = "gatos/informe_update.html"
    context_name = "informe"
    form_class = InformeForm

    # Pasa el objeto colonia para poder acceder a los datos de la colonia
    # cuando se genere el queryset de los gatos que aparecen en la foto.
    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs["colonia"] = self.colonia
        return form_kwargs

    def get_success_url(self):
        return reverse("informe", kwargs={"colonia": self.colonia.slug,
                                          "pk": self.object.id})


class InformeDeleteView(PRMixin, BaseInformeView, DeleteView):
    permission_required = "gatos.delete_informe"


# ------------------------------------------------------------------------


class CapturaBaseMixin(SubGatoMixin, SubColoniaMixin):
    model = Captura

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.captura = get_object_or_404(Captura, id=kwargs['pk'])

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['captura'] = self.captura
        return context

    def get_success_url(self):
        return self.gato.get_absolute_url()


class CapturarGato(PRMixin, GatoConfirmationView):
    permission_required = "gatos.capturar_gato"

    def get_question(self):
        return f"¿Seguro que ha capturado al gato '{self.gato}'?"

    def confirm(self):
        flow = GatoFlow(self.gato)
        flow.capturar()
        return HttpResponseRedirect(self.gato.get_absolute_url())

    def cancel(self):
        return HttpResponseRedirect(self.gato.get_absolute_url())


class LiberarGato(PRMixin, GatoConfirmationView):
    permission_required = "gatos.liberar_gato"

    def get_question(self):
        return f"¿Seguro que ha liberado al gato '{self.gato}'?"

    def confirm(self):
        flow = GatoFlow(self.gato)
        flow.liberar()
        return HttpResponseRedirect(self.gato.get_absolute_url())

    def cancel(self):
        return HttpResponseRedirect(self.gato.get_absolute_url())


class MorirGato(PRMixin, GatoConfirmationView):
    permission_required = "gatos.liberar_gato"

    def get_question(self):
        return f"¿Seguro que quiere declarar muerto a '{self.gato}'?"

    def confirm(self):
        flow = GatoFlow(self.gato)
        flow.morir()
        return HttpResponseRedirect(self.gato.get_absolute_url())

    def cancel(self):
        return HttpResponseRedirect(self.gato.get_absolute_url())


class CapturaView(PRMixin, SubColoniaMixin, SubGatoMixin, DetailView):
    model = Captura
    permission_required = "gatos.view_captura"
    template_name = "gatos/captura_view.html"
    context_object_name = "captura"


class CapturaUpdateView(PRMixin, CapturaBaseMixin, UpdateView):
    permission_required = "gatos.change_captura"
    template_name = "gatos/captura_update_view.html"
    form_class = CapturaForm


class CapturaDeleteView(PRMixin, CapturaBaseMixin, DeleteView):
    permission_required = "gatos.delete_captura"
    context_object_name = "captura"


# ------------------------------------------------------------------------


class EnfermedadBaseView(SubGatoMixin, SubColoniaMixin):
    model = Enfermedad
    context_name = "enfermedad"


class EnfermedadView(PRMixin, EnfermedadBaseView, DetailView):
    permission_required = "gatos.view_enfermedad"
    template_name = "gatos/enfermedad.html"


class EnfermedadCreateView(PRMixin, EnfermedadBaseView, CreateView):
    permission_required = "gatos.add_enfermedad"
    template_name = "gatos/enfermedad_create_view.html"
    form_class = EnfermedadCreateForm

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs["gato"] = self.gato
        return form_kwargs

    def get_success_url(self):
        return self.gato.get_absolute_url()


class EnfermedadUpdateView(PRMixin, EnfermedadBaseView, UpdateView):
    permission_required = "gatos.change_enfermedad"
    template_name = "gatos/enfermedad_update_view.html"
    form_class = EnfermedadUpdateForm


class EnfermedadDeleteView(PRMixin, EnfermedadBaseView, DeleteView):
    permission_required = "gatos.delete_enfermedad"
    template = "gatos/enfermedad_confirm_delete.html"


# ------------------------------------------------------------------------


class VacunarGato(PRMixin, SubColoniaMixin, SubGatoMixin, SubCapturaMixin,
                  CreateView):
    permission_required = "gatos.vacunar"
    template_name = "gatos/vacunar_gato.html"
    form_class = VacunarGatoForm

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs["gato"] = self.gato
        form_kwargs["captura"] = self.captura
        return form_kwargs

    def get_success_url(self):
        return self.captura.gato.get_absolute_url()


class ColoniaActivityPlotView(SubColoniaMixin, PNGPlotView):
    plotter_function = staticmethod(activity_plot)
    activity_class = SpanishActivityMap
    filename = "activity.png"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.map = self.activity_class(date.today())
        self.map.load_activity(self.colonia.get_actividad())

    def get_plot_kwargs(self):
        return {"xticks": self.map.get_x_ticks(),
                "yticks": self.map.get_y_ticks(),
                }

    def get_kwargs(self):
        return {"colonia": self.colonia}

    def get_data(self):
        return self.map.get_data()


class GatoActivityPlotView(SubGatoMixin, PNGPlotView):
    plotter_function = staticmethod(activity_plot)
    activity_class = SpanishActivityMap
    filename = "activity.png"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.map = self.activity_class(date.today())
        self.map.load_activity(self.gato.get_actividad())

    def get_plot_kwargs(self):
        return {"xticks": self.map.get_x_ticks(),
                "yticks": self.map.get_y_ticks(),
                }

    def get_kwargs(self):
        return {"colonia": self.colonia}

    def get_data(self):
        return self.map.get_data()


class UserMixin:
    def __setup__(self, request, *args, **kwargs):
        super().__setup__(request, *args, **kwargs)
        self.user = get_object_or_404(settings.AUTH_USER_MODEL,
                                      username=kwargs['username'])


class UserActivityPlotView(UserMixin, PNGPlotView):
    plotter_function = staticmethod(activity_plot)
    activity_class = SpanishActivityMap
    filename = "activity.png"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.map = self.activity_class(date.today())
        self.map.load_activity(get_actividad_usuario(self.user))

    def get_plot_kwargs(self):
        return {"xticks": self.map.get_x_ticks(),
                "yticks": self.map.get_y_ticks(),
                }

    def get_kwargs(self):
        return {"colonia": self.colonia}

    def get_data(self):
        return self.map.get_data()


# ------------------------------------------------------------------------


class Avistamientos(SubColoniaMixin, CommandView):
    template_name = "gatos/avistamientos.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vistos, no_vistos = self.colonia.get_avistamientos(date.today())
        context['vistos'] = vistos
        context['no_vistos'] = no_vistos
        return context

    def run_command(self, request, *args, **kwargs):
        if 'gato' in request.GET:
            colonia = get_object_or_404(Colonia, slug=kwargs['colonia'])
            gato = colonia.gatos.get(slug=request.GET["gato"])
            gato.toggle_avistamiento(date.today(), request.user)


class CalendarioComidas(SubColoniaMixin, CommandView):
    template_name = "gatos/comidas.html"
    class_otro = "comidas-otro"
    class_usuario = "comidas-usuario"
    class_none = "comidas-none"
    metodo = "alternar_comida_usuario"

    def get_calendars(self):
        today = date.today()
        comidas = {c.fecha: c for c in self.colonia.comidas.all()}

        def classes(f):
            if f > today:
                if f not in comidas:
                    return ["comidas-calendario", "comidas-none"]
                elif comidas[f].usuario == self.request.user:
                    return ["comidas-calendario", "comidas-usuario"]
                else:
                    return ["comidas-calendario", "comidas-otro"]
            else:
                return []

        def attrs(f):
            if f > today:
                date = f"{f.year}, {f.month}, {f.day}"
                colonia = self.colonia.slug
                return {"onclick": f"{self.metodo}('{colonia}', {date})"}
            else:
                return {}

        return htmlcalendar(date.today(), months=2, backwards=False,
                            classes=classes, header="h2", attrs=attrs,
                            th_classes=[], safe=True, locale="es_ES.UTF-8")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['calendars'] = self.get_calendars()
        return context

    def run_command(self, request, *args, **kwargs):
        colonia = get_object_or_404(Colonia, slug=kwargs['colonia'])
        qs = request.GET
        if "day" in qs and "month" in qs and "year" in qs:
            dia = int(qs["day"])
            mes = int(qs["month"])
            ano = int(qs["year"])
            fecha = date(ano, mes, dia)
            colonia.toggle_comida(fecha, request.user)

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


def get_actividad_usuario(usuario, min_fecha=None, max_fecha=None):
    fotos = Foto.objects.filter(usuario=usuario)
    informes = Informe.objects.filter(usuario=usuario)
    capturas = Captura.objects.filter(usuario=usuario)
    vacunas = Vacunacion.objects.filter(usuario=usuario)
    diag = Enfermedad.objects.filter(usuario=usuario)
    avist = Avistamiento.objects.filter(usuario=usuario)
    if min_fecha is not None:
        fotos = fotos.filter(fecha__gte=min_fecha)
        informes = informes.filter(fecha__gte=min_fecha)
        capturas = capturas.filter(fecha_captura__gte=min_fecha)
        vacunas = vacunas.filter(captura__fecha_captura__gte=min_fecha)
        diag = diag.filter(fecha_diagnostico__gte=min_fecha)
        avist = avist.filter(fecha__gte=min_fecha)
    if max_fecha is not None:
        fotos = fotos.filter(fecha__lte=max_fecha)
        informes = informes.filter(fecha__lte=max_fecha)
        capturas = capturas.filter(fecha_captura__lte=max_fecha)
        vacunas = vacunas.filter(captura__fecha_captura__lte=max_fecha)
        diag = diag.filter(fecha_diagnostico__lte=max_fecha)
        avist = avist.filter(fecha__lte=max_fecha)
    fotos = list(fotos.all())
    informes = list(informes.all())
    capturas = list(capturas.all())
    vacunas = list(vacunas.all())
    diag = list(diag.all())
    avist = list(avist.all())
    activs = fotos + informes + capturas + vacunas + diag + avist
    return activs


class AgrupadorDeActividades(Agrupador):
    @classmethod
    def build_from_user(cls, usuario, min_fecha=None, max_fecha=None):
        activs = get_actividad_usuario(usuario, min_fecha=min_fecha,
                                       max_fecha=max_fecha)
        return cls(activs)

    @classmethod
    def build_from_colonia(cls, colonia, min_fecha=None, max_fecha=None):
        activs = colonia.get_eventos(min_fecha=min_fecha,
                                     max_fecha=max_fecha)
        return cls(activs)

    @classmethod
    def build_from_gato(cls, gato, min_fecha=None, max_fecha=None):
        activs = gato.get_eventos(min_fecha=min_fecha, max_fecha=max_fecha)
        return cls(activs)

    @staticmethod
    def get_value(x):
        return x.fecha

    @property
    def lista_de_actividades(self):
        return [x.fecha for x in self.items]


class ActividadesColonia(SubColoniaMixin, TemplateView):
    template_name = "gatos/actividad_colonia.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        agrupador = AgrupadorDeActividades.build_from_colonia(self.colonia)
        context['agrupador'] = agrupador
        return context


class ActividadesGato(SubColoniaMixin, SubGatoMixin, TemplateView):
    template_name = "gatos/actividad_gato.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        agrupador = AgrupadorDeActividades.build_from_gato(self.gato)
        context['agrupador'] = agrupador
        return context


class UserProfile(TemplateView):
    template_name = "gatos/user_profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            user = self.request.user
            codigo = CodigoCalendarioComidas.objects.get(user=user)
            url_codigo = reverse("calendario-comidas",
                                 kwargs=dict(codigo=codigo.codigo))
            context["codigo"] = get_svg_qrcode(url_codigo)
        except ObjectDoesNotExist:
            context["codigo"] = None
        context["user"] = self.request.user
        agrupador = AgrupadorDeActividades.build_from_user(self.request.user)
        context["agrupador"] = agrupador
        return context


def calendario_comidas(request, codigo):
    calendario = get_object_or_404(CalendarioComidas, codig=codigo)
    colonia = calendario.colonia
    cal = Calendar()
    cal.add('prodid', f'-//Comidas {codigo}//mxm.dk//')
    cal.add('version', '2.0')

    comidas = colonia.comidas.filter(usuario=request.user)

    for comida in comidas:
        ical_event = IcalEvent()
        ical_event.add('summary', f"Dar de comer a {colonia.nombre}")
        ical_event.add('description', "")
        ical_event.add('dtstart', comida.fecha)
        ical_event.add('dtend', comida.fecha)
        ical_event.add('dtstamp', datetime.now())
        cal.add_component(ical_event)

    response = HttpResponse(cal.to_ical(), content_type='text/calendar')
    response['Content-Disposition'] = 'attachment; filename="comidas.ics"'
    return response

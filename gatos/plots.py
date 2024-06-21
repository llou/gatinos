from io import BytesIO
from datetime import date, timedelta
import matplotlib.pyplot as plt
import pandas as pd
from calmap import yearplot
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import classonlymethod
from .models import Colonia

# --- Under Construction ---


class Plotter:
    http_method_names = [
            "get",
            "head",
            "options",
            "trace",
    ]

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def get_data(self):
        return []

    def transform_data(self):
        _input = self.get_input()
        return _input

    def get_axes(self):
        data = self.transform_data()
        return (data, data)

    def get_figure(self):
        axes = self.get_axes()
        return axes

    def get_png(self):
        return b""

    def get_svg(self):
        return ""

    def get_base64(self):
        return ""

    def get_png_file(self):
        return None

    def get_svg_file(self):
        return None

    @classonlymethod
    def as_view(cls, format="png", **initkwargs):
        for key in initkwargs:
            if key in cls.http_method_names:
                raise TypeError("Conflictin with method name")

        def view(request, **kwargs):
            return HttpResponse

        return view

    def save(self, storage):
        pass


# --- Working Code ---


def colonia_activity_plot(request, colonia=None):
    colonia = get_object_or_404(Colonia, slug=colonia)
    fig = draw_colonia_activity_map(colonia).figure
    return response_matplotlib_plot(fig, "activity.png")


def draw_colonia_activity_map(colonia, days=365):
    today = date.today()
    period_start = today - timedelta(days=days)
    rango_fechas = pd.date_range(period_start, date.today(), freq="D")
    fechas = colonia.fotos.filter(fecha__gte=period_start).values("fecha")
    fechas = pd.Series(1, index=[x['fecha'].date() for x in fechas])
    fechas = fechas.groupby(fechas.index).count()
    fechas = fechas.reindex(rango_fechas, fill_value=0)
    fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(8, 1.5))
    yearplot(fechas, year=today.year, vmin=0.0, vmax=5.0)
    return fig


def response_matplotlib_plot(fig, name="plot"):
    buf = BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)

    response = HttpResponse(buf, content_type='image/png')
    response['Content-Disposition'] = 'inline; filename="%s.png"' % name
    return response

from io import BytesIO
from base64 import b64encode
from datetime import date, timedelta
import matplotlib.pyplot as plt
import pandas as pd
from calmap import yearplot
import numpy as np
from django.core.files.storage import storages
from django.http import HttpResponse
from django.views import View
from django.shortcuts import get_object_or_404
from .models import Colonia

# --- Under Construction ---


class BaseFileView(View):
    buffer_class = BytesIO
    file_format = ""
    disposition = ""  # values: inline, attachment
    mimetype = ""
    http_method_names = [
            "get",
            "options",
    ]

    def get_disposition(self):
        return self.disposition

    def get_filename(self):
        return self.filename

    def get_extension(self):
        return self.file_format

    def get_filetype(self):
        return self.file_format

    def get_mimetype(self):
        return self.mimetype

    def get_headers(self):
        name = self.get_filename()
        disposition = self.get_disposition()
        return {"Content-Disposition": f'{disposition}; filename="{name}"'}

    def get_buffer(self):
        return self.buffer_class()

    def get(self, request, *args, **kwargs):
        buffer = self.get_buffer()
        response = HttpResponse(buffer, content_type=self.get_mimetype())
        response.update(self.get_headers)
        return response


def plotter_function(data, **kwargs):
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3, 4], [1, 4, 2, 3])
    return fig


class BasePlotMixin:
    plotter_function = plotter_function
    buffer_class = BytesIO

    def get_filetype(self):
        return self.filetype

    def get_data(self):
        return {}

    def get_plot_kwargs(self):
        return {}

    def get_buffer(self):
        buffer = super().get_buffer()
        data = self.get_data()
        plot_kwargs = self.get_plot_kwargs()
        figure = self.plotter_function(data, **plot_kwargs)
        figure.savefig(buffer, format=self.get_filetype())
        buffer.seek(0)
        return buffer

    def get_content(self):
        buffer = self.get_buffer()
        return buffer.getvalue()


class SVGPlotMixin(BasePlotMixin):
    filetype = "svg"


class PNGPlotMixin(BasePlotMixin):
    filetype = "png"


class Base64PlotMixin:
    def get_content(self):
        content = super().get_content()
        return b64encode(content)


class StorageMixin:
    storage_name = "default"

    def select_storage(self):
        return storages[self.storage_name]

    def save(self):
        storage = self.select_storage()
        buffer = self.get_buffer()
        name = self.get_filename()
        storage.save(name, buffer)


class ActivityMap:
    num_days = 365
    weekdays = ["mon", "", "wed", "", "fri", "", "sun"]
    months = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep",
              "oct", "nov", "dec"]

    def __init__(self, today):
        self.today = today
        self.num_days = self.get_num_days(today)
        self.base = self.get_base(today, self.num_days)
        self.extra_week = self.get_extra_week(self.today, self.base)
        self.weeks = self.get_weeks(self.num_days, self.extra_week)
        self.ticks = self.get_ticks()
        self.reset()

    def reset(self):
        self.data = np.zeros((7, self.weeks), dtype=int)

    def get_num_days(self, day):
        return self.num_days

    def get_base(self, today, num_days):
        year_ago = today - timedelta(num_days)
        return year_ago - timedelta(year_ago.weekday())

    def get_extra_week(self, today, base):
        return 2 if today.weekday() + base.weekday() > 6 else 1

    def get_weeks(self, num_days, extra_week):
        return num_days // 7 + extra_week

    def get_month(self, month):
        return self.months[month - 1]

    def inc_date(self, date):
        week = (date - self.base).days // 7
        week_day = date.weekday()
        self.data[week_day, week] = self.data[week_day, week] + 1

    def get_ticks(self):
        result = [""] * self.weeks
        for week in range(self.weeks):
            for weekday in range(7):
                d = self.base + timedelta(week * 7 + weekday)
                if d.day == 1:
                    result[week] = self.get_month(d.month)
        return result

    def load_activity(self, activity):
        for d in activity:
            self.inc_date(d)

    def get_data(self):
        return self.data


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
    fechas = pd.Series(1, index=[x['fecha'] for x in fechas])
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

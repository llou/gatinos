from io import BytesIO
from django.views import View
from django.http import HttpResponse
from ..base import BasePlotMixin, SVGPlotMixin, PNGPlotMixin


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
        response.update(self.get_headers())
        return response


class PNGPlotView(PNGPlotMixin, BasePlotMixin, BaseFileView):
    pass


class SVGPlotView(SVGPlotMixin, BasePlotMixin, BaseFileView):
    pass

from io import BytesIO
from mimetypes import MimeTypes
from django.core.files import File
from django.http import HttpResponse

mime = MimeTypes()


def pil_to_django_file(pil_image, format="JPEG"):
    img_arr = BytesIO()
    pil_image.save(img_arr, format=format)
    return File(img_arr)


def response_matplotlib_plot(fig, name="plot"):
    buf = BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)

    response = HttpResponse(buf, content_type='image/png')
    response['Content-Disposition'] = 'inline; filename="%s.png"' % name
    return response

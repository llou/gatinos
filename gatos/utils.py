from io import BytesIO
from mimetypes import MimeTypes
from django.core.files import File

mime = MimeTypes()


def pil_to_django_file(pil_image, format="JPEG"):
    img_arr = BytesIO()
    pil_image.save(img_arr, format=format)
    return File(img_arr)

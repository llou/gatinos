from io import BytesIO
import string
from mimetypes import MimeTypes
import secrets
from django.core.files import File

alphabet = string.ascii_lowercase + string.digits

mime = MimeTypes()


def pil_to_django_file(pil_image, format="JPEG"):
    img_arr = BytesIO()
    pil_image.save(img_arr, format=format)
    return File(img_arr)


def random_choice():
    return ''.join(secrets.choice(alphabet) for _ in range(8))

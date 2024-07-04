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
    return ''.join(secrets.choice(alphabet) for _ in range(16))


class Agrupador:
    @staticmethod
    def get_value(item):
        raise NotImplementedError()

    @classmethod
    def agrupador(cls, actividades):
        result = {}
        for item in actividades:
            fecha = cls.get_value(item)
            if fecha in result:
                result[fecha].append(item)
            else:
                result[fecha] = [item]
        return result

    def __init__(self, items):
        self.items = items
        self.grupos = self.agrupador(items)

    def __iter__(self):
        fechas = sorted(self.grupos.keys(), reverse=True)
        for f in fechas:
            yield f, self.grupos[f]

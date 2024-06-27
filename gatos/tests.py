from pathlib import Path
from PIL import Image
from django.test import TestCase
from .models import Foto, Colonia
from .utils import pil_to_django_file

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


class FotoTest(TestCase):
    GATO_NAME = "pelirrojo.jpg"
    GATO_PATH = FIXTURES_DIR / GATO_NAME

    def setUp(self):
        self.imagen = Image.open(self.GATO_PATH)
        self.imagen_file = pil_to_django_file(self.imagen)
        self.colonia = Colonia.objects.create(slug="mi-colonia",
                                              nombre="Mi Colonia")
        self.foto = Foto.objects.create(colonia=self.colonia)
        self.foto.foto.save(self.GATO_NAME, self.imagen_file)

    def test_setup(self):
        self.assertTrue(self.GATO_PATH.exists())
        image = Image.open(self.GATO_PATH)
        self.assertTrue(image)

    def test_miniatura(self):
        self.foto.update_miniatura()
        self.assertTrue(Path(self.foto.miniatura.path).exists)

    def test_exif(self):
        self.foto.update_exif()

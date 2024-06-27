import random
from datetime import date, timedelta
from pathlib import Path
from PIL import Image
from django.test import TestCase
from .models import Foto, Colonia
from .utils import pil_to_django_file
from .plots import ActivityMap

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


def random_activity(today, num_days=365, num_choices=200):
    result = []
    choices = range(num_choices)
    for i in choices:
        o = random.choice(choices)
        result.append(today - timedelta(o))
    return result


class ActivityMapTest(TestCase):
    today = date(2024, 6, 12)
    num_days = 365
    activity_class = ActivityMap

    def setUp(self):
        self.map = self.activity_class(self.today)

    def test_methods(self):
        self.assertEqual(self.map.get_num_days(self.today), self.num_days)
        base = self.map.get_base(self.today, self.num_days)
        self.assertEqual(self.map.get_extra_week(self.today, base), 1)
        self.assertEqual(base.weekday(), 0)
        dist = self.today - base
        self.assertGreater(dist.days, self.num_days)
        self.assertLess(dist.days, self.num_days + 7)
        self.assertEqual(self.map.get_month(8), "aug")
        extra_week = self.map.get_extra_week(self.today, base)
        weeks = self.map.get_weeks(self.num_days, extra_week)
        ticks = self.map.get_ticks()
        self.assertEqual(len(ticks), weeks)

    def test_extra_week(self):
        from_date = date(2024, 5, 26)
        to_date = date(2024, 6, 23)
        self.assertEqual(self.map.get_extra_week(to_date, from_date), 2)
        from_date = date(2024, 5, 27)
        to_date = date(2024, 6, 24)
        self.assertEqual(self.map.get_extra_week(to_date, from_date), 1)

    def test_blackbox(self):
        activity = random_activity(self.today)
        activity_map = self.activity_class(self.today)
        activity_map.load_activity(activity)


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

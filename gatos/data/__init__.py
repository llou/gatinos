from datetime import timedelta, date
from pathlib import Path
import yaml
import markdown
from django.conf import settings
from django.utils.safestring import mark_safe


DATA_PATH = Path(__file__).resolve().parent


md = markdown.Markdown(extensions=["fenced_code"])


class Vacuna:
    efecto_default = timedelta(0)

    @classmethod
    def build(cls, i, nombre, item):
        nombre = cls.parse_nombre(nombre)
        choice_name = cls.parse_choice_name(nombre)
        if "efecto" in item:
            efecto = cls.parse_efecto(item["efecto"])
        else:
            efecto = cls.efecto_default
        if "observaciones" in item:
            observaciones = cls.parse_observaciones(item['observaciones'])
        else:
            observaciones = ""
        return cls(i, nombre, choice_name, efecto, observaciones)

    @classmethod
    def parse_nombre(cls, nombre):
        return nombre

    @classmethod
    def parse_choice_name(cls, nombre):
        return nombre.upper()

    @classmethod
    def parse_efecto(cls, t):
        years, months, days = t
        return timedelta(years * 365 + months * 31 + days)

    @classmethod
    def parse_observaciones(cls, observaciones):
        return mark_safe(md.convert(observaciones))

    def __init__(self, id, nombre, choice_name, efecto, observaciones):
        self.id = id
        self.nombre = nombre
        self.choice_name = choice_name
        self.efecto = efecto
        self.observacionens = observaciones

    def hasta(self):
        return date.today() + self.efecto


class Vacunas:
    vacuna_class = Vacuna
    settings_path = "TIPOS_DE_VACUNAS_PATH"
    file_path = DATA_PATH / "vacunas.yml"

    @classmethod
    def get_vacuna(cls, i, name, item):
        return cls.vacuna_class.build(i, name, item)

    @classmethod
    def get_path(cls, file_path=None):
        if file_path is None:
            if cls.settings_path in dir(settings):
                return getattr(settings, cls.settings_path)
            else:
                return cls.file_path
        else:
            return file_path

    @classmethod
    def build(cls, file_path=None):
        result = {}
        with open(cls.get_path(file_path=file_path), "r") as f:
            raw_data = yaml.safe_load(f)
        for i, (name, values) in enumerate(raw_data.items()):
            vacuna = cls.get_vacuna(i, name, values)
            nombre_vacuna = vacuna.choice_name
            result[nombre_vacuna] = vacuna
        return cls(result)

    def __init__(self, data):
        self.data = data

    def get_choices(self):
        items = list(self.data.values())
        items.sort(key=lambda x: x.id)
        return [(x.choice_name, x.nombre) for x in items]

    def __getitem__(self, name):
        return self.data[name]


vacunas = Vacunas.build()

import yaml
from datetime import timedelta
from pathlib import Path
from django.conf import settings


DATA_PATH = Path(__file__).resolve().parent


class Vacunas:
    settings_path = "TIPOS_DE_VACUNAS_PATH"
    file_path = DATA_PATH / "vacunas.yml"

    def __init__(self, file_path=None):
        if file_path is None:
            if self.settings_path in dir(settings):
                self.path = getattr(settings, self.settings_path)
            else:
                self.path = self.file_path
        else:
            self.path = file_path

        with open(self.path, "r") as f:
            raw_data = yaml.safe_load(f)
        self.data = self.parse_file(raw_data)

    @classmethod
    def parse_file(cls, raw_data):
        result = {}
        for i, (name, values) in enumerate(raw_data.items()):
            choice_name = cls.get_choice_name(name)
            entry = {"order": i}
            result[choice_name] = entry
            entry["nombre"] = name
            if "efecto" in values:
                entry["efecto"] = cls.parse_time(values["efecto"])
            else:
                entry["efecto"] = 0
            if "observaciones" in values:
                obs = cls.get_observaciones(values["observaciones"])
                entry["observaciones"] = obs
            else:
                entry["observaciones"] = ""
        return result

    @classmethod
    def get_observaciones(cls, obs):
        return obs

    @classmethod
    def get_choice_name(cls, name):
        return name.upper()

    @classmethod
    def parse_time(cls, t):
        years, months, days = t
        return timedelta(years * 365 + months * 31 + days)

    def get_choices(self):
        result = []
        for name, vacuna in self.data.items():
            result.append((name, vacuna['nombre']))
        return result

    def __getitem__(self, name):
        return self.data[name]


vacunas = Vacunas()

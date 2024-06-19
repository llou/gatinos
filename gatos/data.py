from datetime import date, timedelta
import matplotlib.pyplot as plt
import pandas as pd
from calmap import yearplot


def draw_colonia_activity_map(colonia, days=365):
    today = date.today()
    period_start = today - timedelta(days=days)
    rango_fechas = pd.date_range(period_start, date.today(), freq="D")
    fechas = colonia.fotos.filter(fecha__gte=period_start).values("fecha")
    fechas = pd.Series(1, index=[x['fecha'].date() for x in fechas])
    fechas = fechas.groupby(fechas.index).count()
    fechas = fechas.reindex(rango_fechas, fill_value=0)
    fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(8, 1.5))
    yearplot(fechas, year=today.year, vmin=0.0, vmax=5.0)
    return fig

import io
import numpy as np
import matplotlib.pyplot as plt
import segno
from .activity import ActivityMap


class SpanishActivityMap(ActivityMap):
    weekdays = ["lun", "", "mie", "", "vie", "", "dom"]
    months = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep",
              "oct", "nov", "dic"]


def activity_plot(data, xticks=None, yticks=None, color="grey"):
    fig, ax = plt.subplots(figsize=(8, 1.5))
    ax.pcolormesh(data, vmin=0, vmax=5, cmap="Blues", edgecolors=color)
    ax.set_xticks(np.arange(len(xticks))*4.7, labels=xticks)
    ax.set_yticks(np.arange(len(yticks)), labels=yticks)
    ax.spines['bottom'].set_color(color)
    ax.spines['top'].set_color(color)
    ax.spines['right'].set_color(color)
    ax.spines['left'].set_color(color)
    ax.tick_params(axis="x", color="none")
    ax.tick_params(axis="y", color="none")
    ax.grid(color="none", linestyle="-", linewidth=1)
    ax.set_aspect("equal")
    ax.yaxis.set_ticks_position("right")
    fig.tight_layout()
    return fig


def get_svg_qrcode(content):
    qrcode = segno.make(content)
    out = io.BytesIO()
    qrcode.save(out, kind='svg',
                xmldecl=False,
                svgid="calendar-qr",
                omitsize=True)
    value = out.getvalue()
    return value.decode('utf-8')

import io
import numpy as np
import matplotlib.pyplot as plt
import segno
from .activity import ActivityMap


def get_svg_qrcode(content):
    qrcode = segno.make(content)
    out = io.BytesIO()
    qrcode.save(out, kind='svg',
                xmldecl=False,
                svgid="calendar-qr",
                omitsize=True)
    value = out.getvalue()
    return value.decode('utf-8')

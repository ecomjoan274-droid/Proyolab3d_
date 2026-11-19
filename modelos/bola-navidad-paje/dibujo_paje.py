"""Dibujo vectorial del paje para la bola de Navidad.

Cara redonda oscura, fez rojo con borla negra, ojos redondos blancos con la
pupila en el centro y una sonrisa roja con una raya negra. Las medidas van
directamente en mm, con el centro de la bola en (0, 0).

El resultado es un dict color -> geometría (shapely, en mm), con las zonas de
cada color sin solaparse. Lo que no tiene color se queda en el blanco de la base.
"""
import math
import os
import sys

import numpy as np
from shapely.geometry import LineString, Point, Polygon

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "bolas-navidad-personaje"))
from diseno import Lienzo, curva  # noqa: E402  (mismo lienzo que el Tirisiti)


class LienzoMM(Lienzo):
    """Lienzo del Tirisiti, pero con las coordenadas ya en mm."""

    def __init__(self, contorno):
        super().__init__(1.0, 0.0, contorno)

    def mm(self, pts):
        return [tuple(p[:2]) for p in pts]


def arco(cx, cy, r, a0, a1, n=48):
    """Puntos de un arco de circunferencia (ángulos en grados)."""
    return [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
            for a in np.linspace(a0, a1, n)]


# Medidas del personaje (mm)
CARA = (0.0, -7.0, 21.5)          # centro x, centro y, radio
OJOS = (8.2, -2.5, 5.0, 2.0)      # separación desde el centro, altura, radio, radio de la pupila
FEZ_ABAJO, FEZ_ARRIBA = 21.5, 17.5  # media anchura del fez abajo y arriba
FEZ_Y_LADO, FEZ_Y_CENTRO, FEZ_Y_TOPE = 8.0, 4.0, 25.0


def paje(contorno=0.7):
    L = LienzoMM(contorno)
    cx, cy, r = CARA

    # Cara
    L.pintar(Point(cx, cy).buffer(r, 128), "negro")

    # Fez: el borde de abajo se curva siguiendo la cabeza y la tapa es casi plana
    fez = [(-FEZ_ABAJO, FEZ_Y_LADO, "p"), (-FEZ_ARRIBA, FEZ_Y_TOPE - 1.2, "p"), (-9, FEZ_Y_TOPE - 0.3),
           (0, FEZ_Y_TOPE), (9, FEZ_Y_TOPE - 0.3), (FEZ_ARRIBA, FEZ_Y_TOPE - 1.2, "p"),
           (FEZ_ABAJO, FEZ_Y_LADO, "p"), (11, FEZ_Y_CENTRO + 1.2), (0, FEZ_Y_CENTRO),
           (-11, FEZ_Y_CENTRO + 1.2)]
    L.forma(fez, "rojo")

    # Borla: cordón desde el centro de la tapa, nudo y flecos abiertos en abanico
    L.trazo([(0, FEZ_Y_TOPE - 0.4), (0.5, 22.6), (1.4, 20.8)], 1.1)
    L.circulo(1.6, 20.0, 1.7, "negro")
    flecos = Polygon(curva([(0.3, 19.6, "p"), (3.1, 19.6, "p"), (6.4, 13.6), (7.6, 10.6, "p"),
                            (4.8, 10.0), (1.8, 10.0), (-1.6, 10.6, "p"), (-0.8, 13.8)]))
    L.pintar(flecos, "negro")
    L.trazo([(0.4, 18.6), (3.0, 18.6)], 0.6, "rojo", suave=False)  # anillo del nudo
    for x0, x1 in ((1.0, -0.4), (2.4, 5.4)):  # rayas finas para marcar los hilos
        L.trazo([(x0, 17.4), (x1, 11.6)], 0.5, "rojo", suave=False)

    # Ojos: aros blancos con la pupila redonda en el centro
    sep, y, ro, rp = OJOS
    for x in (-sep, sep):
        L.pintar(Point(x, y).buffer(ro, 64), "blanco")
        L.pintar(Point(x, y).buffer(rp, 48), "negro")

    # Sonrisa: media luna roja con las puntas redondas y una raya negra en medio
    centro_sonrisa, radio_sonrisa = (0.0, -5.0), 12.0
    linea = LineString(arco(*centro_sonrisa, radio_sonrisa, 205, 335))
    L.pintar(linea.buffer(2.1, cap_style=1), "rojo")
    L.pintar(LineString(arco(*centro_sonrisa, radio_sonrisa, 214, 326)).buffer(0.3, cap_style=1), "negro")
    return L.zonas

#!/usr/bin/env python3
"""Adorno de Navidad del paje, copiado de la foto `referencia.jpg`.

Uso: generar.py [carpeta_salida]

La pieza tiene la silueta del paje (fez y cara), sin disco ni marco, y un
agujero en lo alto del fez para pasar el cordón. Se construye por capas:

  0,0 a 1,6 mm  base   negro   toda la silueta (la cara es esta base)
  1,6 a 2,4 mm  piezas rojo    fez y sonrisa (la raya de la boca es un hueco)
                       blanco  ojos (el centro es un hueco: se ve la cara)
  2,4 a 3,0 mm  borla  negro   borla encima del fez

Las medidas se han tomado en píxeles sobre la foto (pieza de arriba) y se
pasan a mm con la altura total que se quiera (ALTO).
"""
import importlib.util
import math
import os
import sys

import numpy as np
import shapely
from PIL import Image, ImageDraw, ImageFilter
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

AQUI = os.path.dirname(os.path.abspath(__file__))
TIRISITI = os.path.join(AQUI, "..", "bolas-navidad-personaje")
sys.path.append(TIRISITI)
from diseno import curva  # noqa: E402
from proyecto_3mf import escribir_3mf  # noqa: E402

sys.path.append(os.path.join(AQUI, "..", "perfiles-anycubic"))
from kobra3v2 import ajustes_proyecto  # noqa: E402

# Utilidades de extrusión del generador del Tirisiti (se carga con otro nombre: este también se llama generar)
_spec = importlib.util.spec_from_file_location("generar_tirisiti", os.path.join(TIRISITI, "generar.py"))
_tirisiti = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_tirisiti)
extruir, limpiar, poligonos = _tirisiti.extruir, _tirisiti.limpiar, _tirisiti.poligonos

ALTO = 80.0          # mm, del borde de arriba del fez a la barbilla
AGUJERO = 4.0        # diámetro del agujero del cordón
BASE = 1.6           # grosor de la base negra
PIEZAS_ALTO = 0.8    # fez, sonrisa y ojos (4 capas de 0,2)
BORLA_ALTO = 0.6     # borla encima del fez (3 capas)

# Medidas tomadas en la foto (píxeles de referencia.jpg, pieza de arriba, y hacia abajo),
# como desplazamiento dx desde el eje de la cara. La foto está algo girada: se han
# promediado los dos lados para que salga simétrico.
PX_CENTRO = 466
PX_ARRIBA, PX_ABAJO = 289, 725         # tapa del fez y barbilla
S = ALTO / (PX_ABAJO - PX_ARRIBA)      # mm por píxel


def mm(pts):
    return [((dx * S, (PX_ARRIBA - y) * S) + tuple(p)) for dx, y, *p in pts]


def forma(pts, suave=True):
    pts = mm(pts)
    return Polygon(curva(pts) if suave else [p[:2] for p in pts]).buffer(0)


def simetrico(mitad):
    """Recorre la mitad derecha (dx >= 0) y la cierra con su espejo."""
    izq = [(-p[0],) + tuple(p[1:]) for p in reversed(mitad) if p[0] > 0]
    return list(mitad) + izq


# Sonrisa (píxeles de la foto)
BOCA_R, BOCA_Y = 146, 645.5      # radio del arco y punto más bajo del centro de la banda
BOCA_ARCO, BOCA_GROSOR = 38.5, 54  # medio ángulo de la banda (grados) y su grosor
RAYA_ARCO, RAYA_GROSOR = 35.5, 7.5  # medio ángulo y grosor de la raya hueca


def dibujo():
    # Cara: círculo
    (cx, cy), = mm([(0, 562)])
    cara = Point(cx, cy).buffer(163 * S, 256)

    # Fez: la tapa y el borde de abajo son arcos hacia arriba; los lados, rectos
    tapa = [(dx, 289 + 0.0018 * dx * dx) for dx in np.linspace(-106, 106, 41)]
    borde = [(dx, 452 + 0.0017 * dx * dx) for dx in np.linspace(151, -151, 61)]
    fez = forma(tapa + borde, suave=False)
    fez = fez.buffer(-0.5, join_style=1).buffer(0.5, join_style=1)  # esquinas apenas redondeadas

    # Agujero del cordón, en lo alto del fez, donde sale el cordón en la foto
    (hx, hy), = mm([(0, 311)])
    hueco = Point(hx, hy).buffer(AGUJERO / 2, 64)

    # Borla: cuello estrecho justo debajo del agujero y flecos abiertos en abanico
    borla = forma(simetrico([(0, 326), (5, 326, "p"), (6, 336), (12, 346), (22, 361), (35, 381),
                             (50, 400), (58, 411), (46, 419), (24, 422), (0, 423)]))

    # Ojos: aros con el centro hueco
    ojos = []
    for dx in (-63, 63):
        (ox, oy), = mm([(dx, 536)])
        ojos.append(Point(ox, oy).buffer(40 * S, 96).difference(Point(ox, oy).buffer(16.5 * S, 64)))
    ojos = unary_union(ojos)

    # Sonrisa: banda de grosor constante que sigue un arco, con las puntas redondas, y una raya
    # hueca por el centro del mismo arco. Medido en la foto: el centro de la banda cae en un
    # círculo de radio 138-150 px (la foto está algo girada) con el punto más bajo en y = 645,5; la banda mide 54 px de grueso.
    def arco_sonrisa(grados):
        return LineString(mm([(BOCA_R * math.sin(math.radians(a)), BOCA_Y - BOCA_R + BOCA_R * math.cos(math.radians(a)))
                              for a in np.linspace(-grados, grados, 121)]))
    boca = arco_sonrisa(BOCA_ARCO).buffer(BOCA_GROSOR / 2 * S, 64, cap_style=1)
    raya = arco_sonrisa(RAYA_ARCO).buffer(RAYA_GROSOR / 2 * S, 32, cap_style=1)
    boca = boca.difference(raya)

    silueta = unary_union([cara, fez]).difference(hueco)
    return dict(silueta=silueta, fez=fez.difference(hueco), boca=boca, ojos=ojos, borla=borla)


def construir():
    d = dibujo()
    base = d["silueta"]
    rojo = limpiar(unary_union([d["fez"], d["boca"]]).intersection(base))
    blanco = limpiar(d["ojos"].intersection(base).difference(rojo))
    borla = limpiar(d["borla"].intersection(rojo))
    return [shapely.set_precision(g.buffer(0), 0.002).buffer(0) for g in (base, rojo, blanco, borla)]


# nombre del archivo, nombre de la pieza, filamento, z de abajo, alto, color de la vista previa
CAPAS = [
    ("0_base_negro", "Silueta y cara (negro)", 3, 0.0, BASE, (36, 34, 48)),
    ("1_fez_boca_rojo", "Fez y sonrisa (rojo)", 2, BASE, PIEZAS_ALTO, (196, 52, 40)),
    ("2_ojos_blanco", "Ojos (blanco)", 1, BASE, PIEZAS_ALTO, (236, 238, 230)),
    ("3_borla_negro", "Borla (negro)", 3, BASE + PIEZAS_ALTO, BORLA_ALTO, (24, 24, 30)),
]


def vista_previa(niveles, ruta, px=14):
    x0, y0, x1, y1 = niveles[0].bounds
    m = 8
    ancho, alto = int((x1 - x0 + 2 * m) * px), int((y1 - y0 + 2 * m) * px)

    def pts(c):
        return [((x - x0 + m) * px, (y1 - y + m) * px) for x, y in c]

    img = Image.new("RGB", (ancho, alto), (232, 232, 228))
    for geom, capa in zip(niveles, CAPAS):
        mask = Image.new("L", (ancho, alto), 0)
        for p in poligonos(geom):
            tmp = Image.new("L", (ancho, alto), 0)
            dr = ImageDraw.Draw(tmp)
            dr.polygon(pts(p.exterior.coords), fill=255)
            for h in p.interiors:
                dr.polygon(pts(h.coords), fill=0)
            mask = Image.fromarray(np.maximum(np.asarray(mask), np.asarray(tmp)))
        sombra = Image.new("L", (ancho, alto), 0)
        sombra.paste(mask, (int(0.4 * px), int(0.5 * px)))
        sombra = sombra.filter(ImageFilter.GaussianBlur(px * 0.4)).point(lambda v: int(v * 0.4))
        img.paste((40, 40, 40), (0, 0), sombra)
        img.paste(capa[5], (0, 0), mask)
    img.save(ruta)


CAMA = 255.0

# Colores de los filamentos en el orden del ACE Pro (1 blanco, 2 rojo, 3 negro, 4 azul)
COLORES_ACE = ["#FFFFFF", "#C12E1F", "#161616", "#1E50BE"]

# Cambios sobre el perfil "0.20mm Standard @Anycubic Kobra 3 V2 0.4 nozzle" para esta pieza
PROCESO = {
    "layer_height": "0.2",                 # cada color cae justo en su capa (1,6 y 2,4 mm)
    "initial_layer_print_height": "0.2",
    "sparse_infill_density": "100%",       # pieza de 3 mm: maciza para que no se doble
    "sparse_infill_pattern": "zig-zag",
    "brim_type": "no_brim",                # pieza plana y ancha: no necesita borde
    "enable_prime_tower": "1",             # purga los cambios de color fuera de la pieza
    "outer_wall_speed": "100",             # contornos limpios en los detalles pequeños
    "top_surface_speed": "100",
    "seam_position": "back",               # la costura, en la parte de arriba del fez
}


def main():
    salida = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "salida")
    os.makedirs(salida, exist_ok=True)
    niveles = construir()
    piezas = []
    for geom, (archivo, nombre, filamento, z0, alto, _) in zip(niveles, CAPAS):
        malla = extruir(geom, z0, alto)
        malla.export(os.path.join(salida, f"paje_{archivo}.stl"))
        piezas.append((nombre, malla, filamento))
        print(f"{archivo}: {len(malla.faces)} triángulos, cerrada={malla.is_watertight}, "
              f"z {malla.bounds[0][2]:.1f}-{malla.bounds[1][2]:.1f} mm")
    x0, y0, x1, y1 = niveles[0].bounds
    print(f"medidas: {x1 - x0:.1f} x {y1 - y0:.1f} x {BASE + PIEZAS_ALTO + BORLA_ALTO:.1f} mm")
    vista_previa(niveles, os.path.join(salida, "paje_vista.png"))
    # La pieza va centrada en la cama y la torre de purga a su derecha
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    centradas = [(n, m.copy().apply_translation((-cx, -cy, 0)), f) for n, m, f in piezas]
    escribir_3mf(os.path.join(salida, "paje_multicolor.3mf"),
                 [dict(nombre="Adorno paje", posicion=(CAMA / 2, CAMA / 2), piezas=centradas)],
                 ajustes=ajustes_proyecto(COLORES_ACE, PROCESO, torre=(CAMA / 2 + 55, CAMA / 2 - 20)))


if __name__ == "__main__":
    main()

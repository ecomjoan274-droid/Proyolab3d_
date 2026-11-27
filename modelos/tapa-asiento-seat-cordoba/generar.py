#!/usr/bin/env python3
"""Tapa lateral del asiento del copiloto (derecho) del Seat Córdoba 6K, ref. VAG 191 881 478.

Uso: generar.py [carpeta_salida]

Copiada del vídeo (fotograma de frente a los 22,9 s). La pieza es una carcasa de
plástico: una placa con faldón alrededor, abierta por detrás, con

  - una cúpula redonda a la izquierda (tapa el mecanismo del respaldo), con un
    escalón en anillo alrededor y hueca por detrás, con un tetón en el centro;
  - dos agujeros arriba con su torreta por detrás y uno pequeño abajo;
  - una muesca en semicírculo abajo (por donde pasa el eje / la palanca);
  - el extremo derecho en punta, subiendo en diagonal;
  - por detrás, en relieve, el número 191 881 478 y >PE< (polietileno).

Se imprime con la cara vista hacia arriba y el faldón apoyado en la cama.

Las medidas del contorno están tomadas en píxeles sobre el vídeo y se pasan a mm
con el largo total (LARGO). Con las medidas reales de la pieza, se cambian las
constantes de abajo y se vuelve a generar.
"""
import math
import os
import sys

import numpy as np
import trimesh
import manifold3d
from manifold3d import CrossSection, Manifold
from matplotlib.font_manager import FontProperties
from matplotlib.textpath import TextPath
from shapely import affinity
from shapely.geometry import Point, Polygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(AQUI, "..", "bolas-navidad-personaje"))
from proyecto_3mf import escribir_3mf  # noqa: E402

sys.path.append(os.path.join(AQUI, "..", "perfiles-anycubic"))
from kobra3v2 import ajustes_proyecto  # noqa: E402

# ---------------------------------------------------------------- medidas (mm)
LARGO = 230.0        # de la punta de la cúpula a la punta derecha (ESTIMADO: falta la medida real)
FONDO = 12.0         # grosor total sin la cúpula: de la cama a la cara vista
PLACA = 2.5          # grosor de la placa (cara vista)
FALDON = 2.0         # grosor de la pared de alrededor
CANTO = 2.0          # radio del redondeo del canto de la cara vista
ANILLO_ALTO = 3.0    # escalón del anillo sobre la cara vista
CUPULA_ALTO = 7.5    # altura de la cúpula sobre la cara vista
AGUJERO_ARRIBA = 6.0 # diámetro de los dos agujeros de arriba
AGUJERO_ABAJO = 4.5  # diámetro del agujero pequeño de abajo
TORRETA = 11.0       # diámetro exterior de las torretas de los agujeros de arriba
TORRETA_ALTO = 6.0   # lo que bajan las torretas desde la placa
TEXTO_ALTO = 4.0     # altura de las letras de detrás
RELIEVE = 0.5        # lo que sobresalen las letras

# ------------------------------------------- contorno medido en el vídeo (píxeles)
# Fotograma de frente, ampliado x4; x hacia la derecha, y hacia abajo.
PX_IZQ, PX_DER, PX_ABAJO = 58, 1566, 745
S = LARGO / (PX_DER - PX_IZQ)                 # mm por píxel
ANILLO_C, ANILLO_R = (338, 352), 280          # borde de fuera del anillo (es el contorno a la izquierda)
CUPULA_R = 200                                # borde de la cúpula
# Contorno del cuerpo, de la cúpula hacia la derecha por arriba y vuelta por abajo
CUERPO = [(338, 72), (1480, 86), (1535, 98), (1560, 140), (1566, 300), (1546, 342),
          (1062, 590), (1000, 640), (840, 745), (470, 745), (330, 660), (200, 600), (200, 100)]
MUESCA = [(848, 722), (958, 545), (1062, 592)]  # tres puntos del arco de la muesca
AGUJEROS = [((810, 322), AGUJERO_ARRIBA, True), ((1192, 340), AGUJERO_ARRIBA, True),
            ((645, 680), AGUJERO_ABAJO, False)]   # (centro, diámetro, lleva torreta)
TEXTOS = [("191 881 478", (690, 615)), (">PE<", (690, 655))]  # centro, visto desde delante

CAMA = 255.0
NEGRO = "#161616"
PROCESO = {
    "layer_height": "0.2",
    "initial_layer_print_height": "0.2",
    "wall_loops": "3",                     # el faldón de 2 mm sale macizo
    "top_shell_layers": "6",
    "bottom_shell_layers": "4",
    "sparse_infill_density": "30%",
    "enable_support": "1",                 # la placa hace de techo sobre el hueco de detrás
    "support_type": "tree(auto)",
    "support_on_build_plate_only": "1",    # que no apoye soportes sobre la propia pieza
    "brim_type": "outer_only",             # pieza larga apoyada en un faldón fino: mejor con borde
    "brim_width": "6",
    "seam_position": "back",               # la costura, en el canto de arriba
}


def mm(p):
    x, y = p
    return ((x - PX_IZQ) * S, (PX_ABAJO - y) * S)


def circulo_3_puntos(a, b, c):
    (ax, ay), (bx, by), (cx, cy) = a, b, c
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    ux = ((ax**2 + ay**2) * (by - cy) + (bx**2 + by**2) * (cy - ay) + (cx**2 + cy**2) * (ay - by)) / d
    uy = ((ax**2 + ay**2) * (cx - bx) + (bx**2 + by**2) * (ax - cx) + (cx**2 + cy**2) * (bx - ax)) / d
    return (ux, uy), math.hypot(ax - ux, ay - uy)


def contorno():
    """Silueta de la pieza vista de frente, en mm, con las esquinas redondeadas."""
    anillo = Point(mm(ANILLO_C)).buffer(ANILLO_R * S, quad_segs=64)
    cuerpo = Polygon([mm(p) for p in CUERPO])
    (mx, my), mr = circulo_3_puntos(*[mm(p) for p in MUESCA])
    g = unary_union([anillo, cuerpo]).difference(Point(mx, my).buffer(mr, quad_segs=48))
    g = g.buffer(6, quad_segs=16).buffer(-6, quad_segs=16)   # rincones redondeados (r 6)
    g = g.buffer(-4, quad_segs=16).buffer(4, quad_segs=16)   # esquinas redondeadas (r 4)
    return g.simplify(0.02)


def seccion(g):
    polis = [g] if g.geom_type == "Polygon" else list(g.geoms)
    anillos = []
    for p in polis:
        p = orient(p, 1.0)       # exterior en sentido antihorario, huecos al revés
        anillos.append(np.asarray(p.exterior.coords)[:-1])
        anillos += [np.asarray(i.coords)[:-1] for i in p.interiors]
    return CrossSection(anillos)


def prisma(g, z0, alto):
    return Manifold.extrude(seccion(g), alto).translate((0, 0, z0))


def cilindro(c, d, z0, alto, n=64):
    return Manifold.cylinder(alto, d / 2, d / 2, n).translate((c[0], c[1], z0))


def girar(perfil, centro, z0, n=192):
    """Sólido de revolución de un perfil (r, z) alrededor del eje vertical que pasa por centro."""
    return Manifold.revolve(CrossSection([np.asarray(perfil)]), n).translate((centro[0], centro[1], z0))


def texto(cadena, centro, alto):
    """Letras en mm, centradas, escritas al revés para leerse mirando la pieza por detrás."""
    tp = TextPath((0, 0), cadena, size=alto, prop=FontProperties(family="DejaVu Sans", weight="bold"))
    g = Polygon()
    for p in tp.to_polygons():
        if len(p) >= 3:
            g = g.symmetric_difference(Polygon(p).buffer(0))
    x0, y0, x1, y1 = g.bounds
    g = affinity.translate(g, -(x0 + x1) / 2, -(y0 + y1) / 2)
    g = affinity.scale(g, -1, 1, origin=(0, 0))
    return affinity.translate(g, *centro)


def construir():
    sil = contorno()
    c = mm(ANILLO_C)
    R, r = ANILLO_R * S, CUPULA_R * S
    techo = FONDO - PLACA          # cara de dentro de la placa

    # Placa de la cara vista, con el canto redondeado
    piezas = [prisma(sil, techo, FONDO - CANTO - techo)]
    pasos = 8
    for i in range(pasos):
        a0, a1 = i / pasos * math.pi / 2, (i + 1) / pasos * math.pi / 2
        z0 = FONDO - CANTO + CANTO * math.sin(a0)
        z1 = FONDO - CANTO + CANTO * math.sin(a1)
        piezas.append(prisma(sil.buffer(-CANTO * (1 - math.cos(a1)), quad_segs=16), z0, z1 - z0))
    # Paredes de detrás: el faldón de alrededor y el nervio redondo del anillo
    # (algo más grueso por dentro: el hueco de la cúpula lo recorta a su medida)
    faldon = sil.difference(sil.buffer(-FALDON, quad_segs=16))
    nervio = Point(c).buffer(R + 1, quad_segs=64).difference(Point(c).buffer(R - FALDON - 0.4, quad_segs=64))
    paredes = unary_union([faldon, nervio.intersection(sil)])
    piezas.append(prisma(paredes, 0, techo + 0.05))
    carcasa = Manifold.batch_boolean(piezas, manifold3d.OpType.Add)

    # Anillo y cúpula sobre la cara vista (perfil r, z desde la cara vista)
    ra = R - CANTO - 0.2          # el anillo empieza donde acaba el redondeo del canto
    exterior = [(0, -PLACA), (ra, -PLACA), (ra, 0.0),
                (ra - 0.3, ANILLO_ALTO * 0.6), (ra - 0.9, ANILLO_ALTO * 0.92), (ra - 1.8, ANILLO_ALTO),
                (r + 1.2, ANILLO_ALTO), (r + 0.3, ANILLO_ALTO + 0.6)]
    for k in range(1, 13):        # hombro redondo de la cúpula, de r a r-4
        a = k / 12 * math.pi / 2
        exterior.append((r - 4 + 4 * math.cos(a) + 0.3 * (1 - math.sin(a)),
                         ANILLO_ALTO + 0.6 + (CUPULA_ALTO - 0.4 - ANILLO_ALTO - 0.6) * math.sin(a)))
    for k in range(1, 9):         # techo casi plano, algo abombado
        rr = (r - 4) * (1 - k / 8)
        exterior.append((max(rr, 0.0), CUPULA_ALTO - 0.4 * (rr / (r - 4)) ** 2))
    cupula = girar(exterior, c, FONDO)

    interior = [(0, -FONDO - 1), (R - FALDON, -FONDO - 1), (R - FALDON, ANILLO_ALTO - PLACA),
                (r - 0.5, ANILLO_ALTO - PLACA), (r - 2.5, CUPULA_ALTO - PLACA - 1.0),
                (r - 6, CUPULA_ALTO - PLACA), (0, CUPULA_ALTO - PLACA)]
    hueco_cupula = girar(interior, c, FONDO)
    pieza = carcasa + cupula - hueco_cupula

    # Tetón en el centro de la cúpula, por dentro
    pieza = pieza + cilindro(c, 9, FONDO + CUPULA_ALTO - PLACA - 3.5, 3.6)

    # Torretas de los agujeros de arriba, por detrás
    for p, d, torreta in AGUJEROS:
        if torreta:
            pieza = pieza + cilindro(mm(p), TORRETA, techo - TORRETA_ALTO, TORRETA_ALTO + 0.01)
    for p, d, _ in AGUJEROS:
        pieza = pieza - cilindro(mm(p), d, -1, FONDO + 2)

    # Número de pieza y material en relieve por detrás (se leen mirando por detrás)
    letras = unary_union([texto(t, mm(p), TEXTO_ALTO) for t, p in TEXTOS])
    pieza = pieza + prisma(letras, techo - RELIEVE, RELIEVE + 0.01)
    return pieza, sil


def a_trimesh(m):
    malla = m.to_mesh()
    return trimesh.Trimesh(np.asarray(malla.vert_properties)[:, :3], np.asarray(malla.tri_verts), process=True)


def vista(malla, ruta):
    """Dos vistas sombreadas (delante y detrás) con un z-buffer sencillo."""
    from PIL import Image

    def render(v, f, w=1400):
        x0, y0 = v[:, 0].min(), v[:, 1].min()
        esc = (w - 40) / (v[:, 0].max() - x0)
        h = int((v[:, 1].max() - y0) * esc) + 40
        tri = v[f]
        n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
        luz = np.array([-0.4, 0.5, 0.75]); luz /= np.linalg.norm(luz)
        brillo = np.clip(n @ luz, 0, 1) * 0.75 + 0.2
        zbuf = np.full((h, w), -np.inf); img = np.full((h, w), 0.96)
        p = np.empty_like(tri)
        p[..., 0] = (tri[..., 0] - x0) * esc + 20
        p[..., 1] = h - ((tri[..., 1] - y0) * esc + 20)
        p[..., 2] = tri[..., 2]
        for t, b in zip(p, brillo):
            (ax, ay, az), (bx, by, bz), (cx, cy, cz) = t
            mnx, mxx = int(max(min(ax, bx, cx), 0)), int(min(max(ax, bx, cx) + 1, w))
            mny, mxy = int(max(min(ay, by, cy), 0)), int(min(max(ay, by, cy) + 1, h))
            if mnx >= mxx or mny >= mxy:
                continue
            den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
            if abs(den) < 1e-9:
                continue
            X, Y = np.meshgrid(np.arange(mnx, mxx) + 0.5, np.arange(mny, mxy) + 0.5)
            l1 = ((by - cy) * (X - cx) + (cx - bx) * (Y - cy)) / den
            l2 = ((cy - ay) * (X - cx) + (ax - cx) * (Y - cy)) / den
            l3 = 1 - l1 - l2
            dentro = (l1 >= 0) & (l2 >= 0) & (l3 >= 0)
            z = l1 * az + l2 * bz + l3 * cz
            zb = zbuf[mny:mxy, mnx:mxx]
            ok = dentro & (z > zb)
            zb[ok] = z[ok]
            img[mny:mxy, mnx:mxx][ok] = b * 0.55
        return (np.clip(img, 0, 1) * 255).astype(np.uint8)

    v, f = np.asarray(malla.vertices, float), np.asarray(malla.faces)
    # Vista de delante: un poco inclinada para que se vea el relieve
    rot = trimesh.transformations.rotation_matrix(math.radians(-25), [1, 0, 0])[:3, :3]
    delante = render(v @ rot.T, f)
    # Vista de detrás: girada sobre el eje vertical de la imagen (se ve como en el vídeo)
    vb = v.copy(); vb[:, 0] *= -1; vb[:, 2] *= -1
    detras = render(vb @ rot.T, f)
    w = max(delante.shape[1], detras.shape[1])
    lienzo = np.full((delante.shape[0] + detras.shape[0], w), 245, np.uint8)
    lienzo[:delante.shape[0], :delante.shape[1]] = delante
    lienzo[delante.shape[0]:, :detras.shape[1]] = detras
    Image.fromarray(lienzo).save(ruta)


def main():
    salida = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "salida")
    os.makedirs(salida, exist_ok=True)
    pieza, sil = construir()
    malla = a_trimesh(pieza)
    malla.export(os.path.join(salida, "tapa_asiento_191881478.stl"))
    x0, y0, z0 = malla.bounds[0]
    x1, y1, z1 = malla.bounds[1]
    print(f"triángulos {len(malla.faces)}, cerrada={malla.is_watertight}, volumen {malla.volume / 1000:.1f} cm³")
    print(f"medidas: {x1 - x0:.1f} x {y1 - y0:.1f} x {z1 - z0:.1f} mm")
    vista(malla, os.path.join(salida, "tapa_vista.png"))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    centrada = malla.copy().apply_translation((-cx, -cy, 0))
    escribir_3mf(os.path.join(salida, "tapa_asiento_191881478.3mf"),
                 [dict(nombre="Tapa asiento 191 881 478", posicion=(CAMA / 2, CAMA / 2),
                       piezas=[("tapa", centrada, 1)])],
                 ajustes=ajustes_proyecto([NEGRO], PROCESO))


if __name__ == "__main__":

    main()

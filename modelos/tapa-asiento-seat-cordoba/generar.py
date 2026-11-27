#!/usr/bin/env python3
"""Tapa lateral del asiento del copiloto (derecho) del Seat Córdoba 6K, ref. VAG 191 881 478.

Uso: generar.py [carpeta_salida]

Es la misma pieza que llevan el Golf 2, Jetta 2, Scirocco, Corrado, Polo y Lupo
("Verkleidung Sitzgestell, rechts, ohne Loch"). Medidas del catálogo
Volkswagen Classic Parts: 210 x 95 x 15 mm.

El contorno, el anillo de la cúpula y los agujeros salen de la foto cenital de
una pieza nueva (anuncio de omecar.de), calcada con calcar_contorno.py y
escalada a 210 mm de largo: están en contorno.json. Lo que no se ve en esa foto
(grosores y la parte de detrás) sale del vídeo de la pieza.

La pieza es una carcasa de plástico abierta por detrás:
  - placa con el canto redondeado y faldón alrededor;
  - cúpula a la izquierda (tapa el mecanismo del respaldo): borde redondeado,
    un pequeño valle y una cúpula central; hueca por detrás, con tetón;
  - dos agujeros arriba con torreta por detrás y uno pequeño abajo;
  - la muesca de abajo y el extremo derecho en punta;
  - por detrás, en relieve, 191 881 478 y >PE< (polietileno).

Se imprime con la cara vista hacia arriba y el faldón apoyado en la cama.
"""
import json
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
from shapely.geometry import Point, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(AQUI, "..", "bolas-navidad-personaje"))
from proyecto_3mf import escribir_3mf  # noqa: E402

sys.path.append(os.path.join(AQUI, "..", "perfiles-anycubic"))
from kobra3v2 import ajustes_proyecto  # noqa: E402

with open(os.path.join(AQUI, "contorno.json"), encoding="utf-8") as _f:
    CALCO = json.load(_f)

# ---------------------------------------------------------------- medidas (mm)
ALTO_TOTAL = 15.0      # catálogo VW: de la cama a lo alto de la cúpula
CUPULA_ALTO = 4.5      # lo que sobresale la cúpula sobre la cara vista (vídeo)
FONDO = ALTO_TOTAL - CUPULA_ALTO   # de la cama a la cara vista
BORDE_ALTO = 3.0       # borde redondeado de la cúpula sobre la cara vista
VALLE_ALTO = 2.3       # el valle entre el borde y la cúpula central
PLACA = 2.2            # grosor de la placa
FALDON = 1.8           # grosor de la pared de alrededor
CANTO = 1.5            # radio del redondeo del canto de la cara vista
AGUJERO_ARRIBA = 5.5   # diámetro de los dos agujeros de arriba
AGUJERO_ABAJO = 4.5    # diámetro del agujero pequeño de abajo
TORRETA = 10.0         # diámetro exterior de las torretas de los agujeros de arriba
TORRETA_ALTO = 5.0     # lo que bajan las torretas desde la placa
TEXTO_ALTO = 3.5       # altura de las letras de detrás
RELIEVE = 0.5          # lo que sobresalen las letras

ANILLO_C = tuple(CALCO["anillo"]["centro"])
ANILLO_R = CALCO["anillo"]["radio"]
# Agujeros (centro, diámetro, lleva torreta): el de abajo es el de x menor
_ag = sorted(CALCO["agujeros"], key=lambda p: p[1])
AGUJEROS = [(tuple(_ag[0]), AGUJERO_ABAJO, False)] + [(tuple(p), AGUJERO_ARRIBA, True) for p in _ag[1:]]
# Centro de cada texto, en mm y visto desde delante (entre la cúpula y la muesca, sobre el agujero de abajo)
TEXTOS = [("191 881 478", (91.0, 22.0)), (">PE<", (91.0, 16.3))]

CAMA = 255.0
NEGRO = "#161616"
PROCESO = {
    "layer_height": "0.2",
    "initial_layer_print_height": "0.2",
    "wall_loops": "3",                     # el faldón sale macizo
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


def contorno():
    """Silueta de la pieza vista de frente, en mm (calcada de la foto)."""
    g = Polygon(CALCO["contorno"]).buffer(0)
    g = unary_union([g, Point(ANILLO_C).buffer(ANILLO_R, quad_segs=64)])
    g = g.buffer(3, quad_segs=16).buffer(-3, quad_segs=16)    # rellena las mellas del calco (textura de la foto)
    g = g.buffer(-2, quad_segs=16).buffer(2, quad_segs=16)    # y quita los picos
    return g.simplify(0.03)


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


def perfil_cupula(R):
    """Perfil (r, z) de la cara de fuera de la cúpula, con z desde la cara vista.
    Radios sacados de la foto: borde de fuera R, cresta del borde a 0,9 R,
    valle entre 0,74 R y 0,80 R, cúpula central hasta 0,74 R."""
    ra = R - CANTO - 0.2                 # empieza donde acaba el redondeo del canto
    pts = [(ra, 0.0)]
    cresta = 0.895 * R
    for k in range(1, 9):                # subida redonda del borde
        a = k / 8 * math.pi / 2
        pts.append((ra - (ra - cresta) * (1 - math.cos(a)), BORDE_ALTO * math.sin(a)))
    valle_ext, valle_int = 0.80 * R, 0.74 * R
    for k in range(1, 7):                # bajada del borde al valle
        t = k / 6
        pts.append((cresta - (cresta - valle_ext) * t,
                    VALLE_ALTO + (BORDE_ALTO - VALLE_ALTO) * (0.5 + 0.5 * math.cos(math.pi * t))))
    pts.append((valle_int, VALLE_ALTO))
    for k in range(1, 17):               # cúpula central
        rr = valle_int * (1 - k / 16)
        pts.append((rr, VALLE_ALTO + (CUPULA_ALTO - VALLE_ALTO) * (1 - (rr / valle_int) ** 2) ** 0.7))
    return pts


def construir():
    sil = contorno()
    c, R = ANILLO_C, ANILLO_R
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
    faldon = sil.difference(sil.buffer(-FALDON, quad_segs=16))
    nervio = Point(c).buffer(R + 1, quad_segs=64).difference(Point(c).buffer(R - FALDON - 0.4, quad_segs=64))
    paredes = unary_union([faldon, nervio.intersection(sil)])
    piezas.append(prisma(paredes, 0, techo + 0.05))
    carcasa = Manifold.batch_boolean(piezas, manifold3d.OpType.Add)

    # Cúpula sobre la cara vista
    fuera = perfil_cupula(R)
    cupula = girar([(0, -PLACA), (fuera[0][0], -PLACA)] + fuera, c, FONDO)

    # Hueco de la cúpula por detrás: la cara de fuera desplazada hacia dentro el grosor de la placa
    region = Polygon([(-p[0], p[1]) for p in reversed(fuera)] + fuera + [(fuera[0][0], -40), (-fuera[0][0], -40)])
    dentro = region.buffer(-PLACA, quad_segs=8).intersection(box(0, -40, R, 20))
    dentro = orient(dentro.simplify(0.01), 1.0)
    pts = np.asarray(dentro.exterior.coords)[:-1]
    pts[:, 0] = np.maximum(pts[:, 0], 0.0)
    hueco_cupula = girar(pts, c, FONDO)
    pieza = carcasa + cupula - hueco_cupula

    # Tetón en el centro de la cúpula, por dentro
    pieza = pieza + cilindro(c, 9, FONDO + CUPULA_ALTO - PLACA - 3.5, 3.6)

    # Torretas de los agujeros de arriba, por detrás
    for p, d, torreta in AGUJEROS:
        if torreta:
            pieza = pieza + cilindro(p, TORRETA, techo - TORRETA_ALTO, TORRETA_ALTO + 0.01)
    for p, d, _ in AGUJEROS:
        pieza = pieza - cilindro(p, d, -1, FONDO + 2)

    # Número de pieza y material en relieve por detrás (se leen mirando por detrás)
    letras = unary_union([texto(t, p, TEXTO_ALTO) for t, p in TEXTOS])
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

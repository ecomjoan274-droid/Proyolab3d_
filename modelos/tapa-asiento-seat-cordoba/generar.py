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
from shapely.geometry import LineString, Point, Polygon, box
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
# Alturas desde la cama, con la pieza boca arriba y apoyada en la pared alta.
# Sacadas de la foto de canto (canto de abajo): la pared alta (de la muesca a la punta)
# mide casi el doble que el borde del resto (90 px frente a 46 px), y con el alto total
# del catálogo (15 mm) quedan estas medidas.
ALTO_TOTAL = 15.0      # catálogo VW: de la cama a lo alto de la cúpula
CUPULA_ALTO = 3.5      # lo que sobresale la cúpula sobre la cara vista
FONDO = ALTO_TOTAL - CUPULA_ALTO   # 11,5: de la cama a la cara vista (alto de la pared alta)
FALDON_ALTO = 5.9      # alto del borde bajo, medido desde la cara vista hacia atrás
BORDE_ALTO = 2.4       # borde redondeado de la cúpula sobre la cara vista
VALLE_ALTO = 1.9       # el valle entre el borde y la cúpula central
PLACA = 2.2            # grosor de la placa
FALDON = 1.8           # grosor del borde bajo
PARED_ALTA = 5.0       # grosor de la pared alta (canto en diagonal y extremo derecho)
CANTO = 3.0            # radio del redondeo del canto de la cara vista
AGUJERO_ARRIBA = 5.5   # diámetro del segundo agujero de arriba
AGUJERO_ABAJO = 4.5    # diámetro del agujero pequeño de abajo
AGUJERO_PIVOTE = 3.0   # agujero que atraviesa el pivote
TORRETA = 9.0          # diámetro exterior de las torretas de los agujeros
PIVOTE = 6.5           # diámetro del pivote con dientes
PIVOTE_DIENTE = 8.5    # diámetro de los dientes del pivote
PIVOTE_PUNTA = 1.5     # altura de la punta del pivote sobre la cama
BLOQUE_ALTO = 3.5      # lo que bajan los bloques desde la placa

ANILLO_C = tuple(CALCO["anillo"]["centro"])
ANILLO_R = CALCO["anillo"]["radio"]
# Agujeros: el de abajo (y menor), el del pivote (cerca de la cúpula) y el segundo de arriba
_ag = sorted(CALCO["agujeros"], key=lambda p: p[1])
AG_ABAJO = tuple(_ag[0])
AG_PIVOTE, AG_ARRIBA = [tuple(p) for p in sorted(_ag[1:])]

# Detalles de detrás, medidos en la foto de la parte de detrás (con las flechas) y pasados a mm
# vistos desde delante (x de la cúpula a la punta, y de abajo arriba).
PARED_ALTA_RECORRIDO = ((141.0, 21.0), (206.5, 57.0), (210.0, 75.0), (208.0, 92.0))  # muesca -> punta -> arriba
BLOQUES = [  # (x0, y0, x1, y1)
    (77.0, 54.3, 96.5, 56.4),     # bloque largo, de la cúpula hacia el pivote
    (107.3, 61.5, 117.5, 63.7),   # bloque a la derecha del pivote
    (140.4, 61.5, 151.4, 63.3),   # bloque a la izquierda del segundo agujero
]
MEDIA_LUNA = dict(centro=(142.3, 57.0), radio=3.3, alto=2.0)   # relieve en media luna sobre ese bloque
PESTANAS = [(97.7, 83.0, 1.6, 4.5)]   # (x, y, grueso, largo): pestaña pegada al canto de arriba

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


def perfil_cupula(R):
    """Perfil (r, z) de la cara de fuera de la cúpula, con z desde la cara vista.
    El borde de fuera del anillo es el contorno de la pieza: sube recto desde el faldón
    (por eso, visto de canto, la zona de la cúpula es más alta y hay un escalón).
    Radios sacados de la foto: cresta del borde a 0,9 R, valle entre 0,74 R y 0,80 R."""
    ra = R + 0.15
    pts = [(ra, -CANTO - 0.5), (ra, BORDE_ALTO - 1.6)]
    cresta = 0.92 * R
    for k in range(1, 9):                # redondeo de arriba del borde
        a = k / 8 * math.pi / 2
        pts.append((ra - (ra - cresta) * (1 - math.cos(a)), BORDE_ALTO - 1.6 + 1.6 * math.sin(a)))
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


def pivote(c):
    """Pivote con dientes (clip de abeto): baja de la placa casi hasta la cama, hueco por dentro."""
    techo = FONDO - PLACA
    p = cilindro(c, PIVOTE, PIVOTE_PUNTA, techo - PIVOTE_PUNTA + 0.05)
    for k in range(3):                       # tres dientes cónicos cerca de la punta
        z0 = PIVOTE_PUNTA + 0.3 + k * 1.6
        p = p + Manifold.cylinder(1.4, PIVOTE / 2, PIVOTE_DIENTE / 2, 48).translate((c[0], c[1], z0))
    return p


def construir():
    sil = contorno()
    c, R = ANILLO_C, ANILLO_R
    techo = FONDO - PLACA            # cara de dentro de la placa
    bajo = FONDO - FALDON_ALTO       # donde acaba el borde bajo
    dentro_faldon = sil.buffer(-FALDON / 2, quad_segs=16)   # lo de dentro se solapa con el faldón

    # Pared alta: el canto en diagonal (de la muesca a la punta) y el extremo derecho
    recorrido = LineString(PARED_ALTA_RECORRIDO).buffer(9, cap_style=2, join_style=2)
    pared_alta = recorrido.intersection(sil).difference(sil.buffer(-PARED_ALTA, quad_segs=16))
    zona_alta = recorrido.intersection(sil.buffer(-0.02))   # 0,02 mm hacia dentro: sin caras repetidas

    # Bloque de fuera con el canto de la cara vista redondeado: en la zona de la pared alta
    # baja hasta la cama; en el resto, solo hasta el borde bajo
    piezas = [prisma(sil, bajo, FONDO - CANTO - bajo + 0.01), prisma(zona_alta, -0.5, bajo + 0.6)]
    pasos = 10
    for i in range(pasos):
        a0, a1 = i / pasos * math.pi / 2, (i + 1) / pasos * math.pi / 2
        z0 = FONDO - CANTO + CANTO * math.sin(a0)
        z1 = FONDO - CANTO + CANTO * math.sin(a1)
        piezas.append(prisma(sil.buffer(-CANTO * (1 - math.cos(a1)), quad_segs=16), z0, z1 - z0 + 0.005))
    bloque = Manifold.batch_boolean(piezas, manifold3d.OpType.Add)
    # Hueco de detrás: quedan la placa, el borde bajo y la pared alta
    hueco = prisma(sil.buffer(-FALDON, quad_segs=16).difference(pared_alta.buffer(0.3)), -1, techo + 1)
    carcasa = bloque - hueco

    # Nervio redondo del cuenco de la cúpula (alto como el borde bajo)
    nervio_anillo = Point(c).buffer(R + 1, quad_segs=64).difference(Point(c).buffer(R - FALDON - 0.8, quad_segs=64))
    carcasa = carcasa + prisma(nervio_anillo.intersection(dentro_faldon), bajo + 0.3, techo - bajo - 0.25)

    # Torretas del agujero de abajo y del segundo de arriba (altas como el borde bajo)
    torretas = unary_union([Point(p).buffer(TORRETA / 2, quad_segs=32) for p in (AG_ABAJO, AG_ARRIBA)])
    carcasa = carcasa + prisma(torretas.intersection(dentro_faldon), bajo + 0.3, techo - bajo - 0.25)

    # Bloques, media luna y pestaña de detrás
    bloques = unary_union([box(*b) for b in BLOQUES])
    carcasa = carcasa + prisma(bloques, techo - BLOQUE_ALTO, BLOQUE_ALTO + 0.05)
    ml = MEDIA_LUNA
    media_luna = Point(ml["centro"]).buffer(ml["radio"], quad_segs=24).intersection(
        box(ml["centro"][0] - 5, ml["centro"][1] - 5, ml["centro"][0] + 5, ml["centro"][1] + 0.0)).union(
        box(ml["centro"][0] - ml["radio"], ml["centro"][1], ml["centro"][0] + ml["radio"], ml["centro"][1] + 1.5))
    carcasa = carcasa + prisma(media_luna, techo - ml["alto"], ml["alto"] + 0.05)
    pestanas = unary_union([box(x - g / 2, y - l / 2, x + g / 2, y + l / 2 + 4) for x, y, g, l in PESTANAS])
    carcasa = carcasa + prisma(pestanas.intersection(dentro_faldon), bajo + 0.3, techo - bajo - 0.25)

    # Pivote con dientes en el agujero de arriba que está junto a la cúpula
    carcasa = carcasa + pivote(AG_PIVOTE)

    # Cúpula sobre la cara vista
    fuera = perfil_cupula(R)
    cupula = girar([(0, fuera[0][1])] + fuera, c, FONDO)

    # Hueco de la cúpula por detrás: la cara de fuera desplazada hacia dentro el grosor de la placa
    region = Polygon([(-p[0], p[1]) for p in reversed(fuera)] + fuera + [(fuera[0][0], -40), (-fuera[0][0], -40)])
    hueco_c = region.buffer(-PLACA, quad_segs=8).intersection(box(0, -40, R + 1, 20))
    hueco_c = orient(hueco_c.simplify(0.01), 1.0)
    pts = np.asarray(hueco_c.exterior.coords)[:-1]
    pts[:, 0] = np.maximum(pts[:, 0], 0.0)
    pieza = carcasa + cupula - girar(pts, c, FONDO)

    # Tetón en el centro de la cúpula, por dentro
    pieza = pieza + cilindro(c, 9, FONDO + CUPULA_ALTO - PLACA - 3.5, 3.6)

    # Agujeros
    for p, d in ((AG_ABAJO, AGUJERO_ABAJO), (AG_ARRIBA, AGUJERO_ARRIBA), (AG_PIVOTE, AGUJERO_PIVOTE)):
        pieza = pieza - cilindro(p, d, -1, ALTO_TOTAL + 2)

    # Recorte por la cama (z = 0): todo lo de abajo queda en un mismo plano limpio
    x0, y0, x1, y1 = sil.bounds
    pieza = pieza ^ Manifold.cube((x1 - x0 + 20, y1 - y0 + 20, ALTO_TOTAL + 10)).translate((x0 - 10, y0 - 10, 0))
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
    # De canto, mirando el canto de abajo (el de la muesca), como en la foto de canto:
    # se ve el borde bajo a la izquierda y la pared alta de la muesca a la punta
    canto = render(np.c_[v[:, 0], v[:, 2], -v[:, 1]], f)
    # Tres cuartos por detrás, para ver nervios, torretas y la pared de la muesca
    r2 = (trimesh.transformations.rotation_matrix(math.radians(-50), [1, 0, 0]) @
          trimesh.transformations.rotation_matrix(math.radians(180), [0, 1, 0]))[:3, :3]
    detras2 = render(v @ r2.T, f)
    vistas = [delante, canto, detras, detras2]
    w = max(x.shape[1] for x in vistas)
    lienzo = np.full((sum(x.shape[0] for x in vistas), w), 245, np.uint8)
    y = 0
    for x in vistas:
        lienzo[y:y + x.shape[0], :x.shape[1]] = x
        y += x.shape[0]
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

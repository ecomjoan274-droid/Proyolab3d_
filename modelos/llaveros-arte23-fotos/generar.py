#!/usr/bin/env python3
"""Llaveros para Arte23: Pont de Sant Jordi (ALCOI) y escudo FERRER.

Uso: generar.py [carpeta_salida]

Cada llavero es UNA sola pieza sólida (base y relieve unidos), pensada para
imprimirse tumbada, con el dibujo hacia arriba y un único cambio de filamento:

  Z 0,0 a 3,2 mm  base     negro mate       capas 1 a 16 (a 0,2 mm)
  Z 3,2 a 4,0 mm  relieve  marfil / ocre    capas 17 a 20

Las medidas salen de las fotos de `referencias/`:
  - Puente: la foto se ha enderezado con una homografía sobre las cuatro esquinas
    de la placa (56 x 30 mm) y se ha medido en mm sobre la imagen enderezada.
  - Escudo: la foto está casi de frente; se ha medido el borde dorado en píxeles
    (media de los dos lados, para que salga simétrico) y se pasa a mm.

Dentro de cada función, las coordenadas son las de la foto (x a la derecha,
y hacia abajo, en mm); al final se da la vuelta al eje y.
"""
import math
import os
import sys

import manifold3d as mf
import numpy as np
import shapely
import trimesh
from fontTools.pens.basePen import BasePen
from fontTools.ttLib import TTFont
from fontTools.ttLib.removeOverlaps import removeOverlaps
from fontTools.varLib import instancer
from PIL import Image, ImageDraw, ImageFilter
from shapely.affinity import scale as escalar, translate as mover
from shapely.geometry import LinearRing, Point, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

AQUI = os.path.dirname(os.path.abspath(__file__))
FUENTE = os.path.join(AQUI, "fuentes", "Montserrat[wght].ttf")

BASE = 3.2          # Z de la cara de arriba de la base
ALTO = 4.0          # Z de la cara de arriba del relieve
AGUJERO = 5.2       # diámetro del agujero de la anilla
MIN = 0.8           # trazo y separación mínimos para boquilla de 0,4


# ---------------------------------------------------------------- utilidades 2D

def poligonos(g):
    if g.is_empty:
        return []
    if isinstance(g, Polygon):
        return [g]
    return [p for p in getattr(g, "geoms", []) if isinstance(p, Polygon)]


def abrir(g, r):
    """Redondea esquinas salientes y quita lo más fino que 2r."""
    return g.buffer(-r, join_style=1, quad_segs=24).buffer(r, join_style=1, quad_segs=24)


def cerrar(g, r):
    """Redondea esquinas entrantes y rellena huecos más estrechos que 2r."""
    return g.buffer(r, join_style=1, quad_segs=24).buffer(-r, join_style=1, quad_segs=24)


def rect(x0, y0, x1, y1):
    return box(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))


def voltear(g, alto):
    """De coordenadas de foto (y hacia abajo) a coordenadas de modelo (y hacia arriba)."""
    return mover(escalar(g, 1, -1, origin=(0, 0)), 0, alto)


# -------------------------------------------------------------------- texto

class _Trazo(BasePen):
    """Convierte el contorno de una letra en polilíneas (curvas troceadas)."""

    def __init__(self, glyphset, pasos=14):
        super().__init__(glyphset)
        self.contornos, self.actual, self.pasos = [], [], pasos

    def _moveTo(self, p):
        self.actual = [p]

    def _lineTo(self, p):
        self.actual.append(p)

    def _qCurveToOne(self, p1, p2):
        p0 = self.actual[-1]
        for t in np.linspace(0, 1, self.pasos + 1)[1:]:
            self.actual.append(((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
                                (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]))

    def _curveToOne(self, p1, p2, p3):
        p0 = self.actual[-1]
        for t in np.linspace(0, 1, self.pasos + 1)[1:]:
            a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
            self.actual.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0],
                                a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))

    def _closePath(self):
        if len(self.actual) > 2:
            self.contornos.append(self.actual)
        self.actual = []

    _endPath = _closePath


_fuentes = {}


def fuente(peso):
    if peso not in _fuentes:
        f = TTFont(FUENTE)
        instancer.instantiateVariableFont(f, {"wght": peso}, inplace=True)
        removeOverlaps(f)  # la fuente variable trae trazos solapados
        _fuentes[peso] = f
    return _fuentes[peso]


def letra(ch, peso):
    """Contorno de una letra en unidades de la fuente (y hacia arriba)."""
    f = fuente(peso)
    gs = f.getGlyphSet()
    pen = _Trazo(gs)
    gs[f.getBestCmap()[ord(ch)]].draw(pen)
    # TrueType: los contornos en sentido horario son macizos y los antihorarios, agujeros
    llenos, huecos = [], []
    for c in pen.contornos:
        p = Polygon(c)
        (huecos if shapely.is_ccw(LinearRing(c)) else llenos).append(p.buffer(0))
    return unary_union(llenos).difference(unary_union(huecos)).buffer(0)


def palabra(texto, peso, alto_mayus, centro_x, base_y, ancho=None, hueco=None, estrecho=1.0):
    """Palabra en coordenadas de foto (y hacia abajo), centrada en centro_x, con la
    línea de base en base_y y las mayúsculas de alto_mayus mm.
    hueco: separación fija entre cajas de letras (mm). ancho: ancho total buscado;
    si se da con hueco, se estrechan las letras para que quepa."""
    cap = fuente(peso)["OS/2"].sCapHeight
    k = alto_mayus / cap
    glifos = [escalar(letra(c, peso), k, -k, origin=(0, 0)) for c in texto]
    anchos = [g.bounds[2] - g.bounds[0] for g in glifos]
    if ancho is not None and hueco is not None:
        estrecho = (ancho - hueco * (len(texto) - 1)) / sum(anchos)
    glifos = [escalar(g, estrecho, 1, origin=(0, 0)) for g in glifos]
    anchos = [a * estrecho for a in anchos]
    if hueco is None:  # espaciado de la fuente, con el tracking que haga falta para el ancho
        avances = [fuente(peso)["hmtx"][fuente(peso).getBestCmap()[ord(c)]][0] * k * estrecho for c in texto]
        izq = [g.bounds[0] for g in glifos]
        natural = sum(avances[:-1]) + izq[-1] + anchos[-1] - izq[0]
        track = 0 if ancho is None else (ancho - natural) / (len(texto) - 1)
        x, colocados = 0.0, []
        for g, av in zip(glifos, avances):
            colocados.append(mover(g, x, 0))
            x += av + track
    else:
        x, colocados = 0.0, []
        for g, a in zip(glifos, anchos):
            colocados.append(mover(g, x - g.bounds[0], 0))
            x += a + hueco
    p = unary_union(colocados)
    x0, _, x1, _ = p.bounds
    return mover(p, centro_x - (x0 + x1) / 2, base_y)


# -------------------------------------------------------- pieza 1: el puente

PLACA_W, PLACA_H, PLACA_R = 56.0, 30.0, 3.0
OREJA_X, OREJA_Y, OREJA_R = -2.0, 15.0, 5.4     # oreja a la izquierda, centrada en alto

# Pilares: centro x y medias anchuras (mm) de cada tramo, de arriba abajo.
# Los dos de los extremos son algo más anchos que los del centro, como en la foto.
PILAR_EXT = dict(remate=0.80, escalon=1.35, hombro=1.90, fuste=1.45, zocalo=1.95, pie=2.27)
PILAR_INT = dict(remate=0.70, escalon=1.25, hombro=1.70, fuste=1.10, zocalo=1.50, pie=1.85)
PILARES = [(4.0, PILAR_EXT), (20.4, PILAR_INT), (35.6, PILAR_INT), (52.0, PILAR_EXT)]
Y_REMATE, Y_ESCALON, Y_HOMBRO = 3.1, 4.3, 5.4   # arranque de cada escalón del remate
Y_ZOCALO, Y_PIE, Y_SUELO = 16.0, 18.1, 19.7

TABLERO = (1.7, 54.3, 7.35, 8.6)      # x0, x1, y arriba, y abajo
BARANDA = (5.5, 6.3)                  # pasamanos (0,8 mm, en la foto 0,35)
BALAUSTRE, PASO_BALAUSTRE = 0.8, 1.7  # en la foto 0,35 mm cada 1,1: no se imprimiría
ARRANQUE = 15.6                       # y donde el intradós toca el pilar
ROSCA = 1.6                           # grueso del arco
CLAVE_EXT = 9.5                       # y de la clave por fuera (0,9 mm por debajo del tablero)
MONTANTE = 0.9                        # ancho de los montantes (en la foto ~0,5)

TEXTO_ALCOI = dict(peso=700, alto=5.8, base=26.8, ancho=28.9)


def placa_con_oreja(cuerpo, oreja_c, oreja_r, hacia, radio_union):
    """Une una oreja redonda al cuerpo y redondea la unión. hacia: (dx, dy) unitario
    desde el centro de la oreja hacia el cuerpo."""
    cx, cy = oreja_c
    dx, dy = hacia
    largo = 3 * oreja_r
    cuello = Polygon([(cx - dy * oreja_r, cy + dx * oreja_r), (cx + dy * oreja_r, cy - dx * oreja_r),
                      (cx + dy * oreja_r + dx * largo, cy - dx * oreja_r + dy * largo),
                      (cx - dy * oreja_r + dx * largo, cy + dx * oreja_r + dy * largo)])
    oreja = unary_union([Point(cx, cy).buffer(oreja_r, quad_segs=48), cuello])
    juntos = cerrar(unary_union([cuerpo, oreja]), radio_union)
    agujero = Point(cx, cy).buffer(AGUJERO / 2, quad_segs=64)
    return juntos.difference(agujero), agujero


def pilar(cx, d):
    tramos = [
        (d["remate"], Y_REMATE, Y_ESCALON + 0.01),
        (d["escalon"], Y_ESCALON, Y_HOMBRO + 0.01),
        (d["hombro"], Y_HOMBRO, TABLERO[2] + 0.3),
        (d["fuste"], Y_HOMBRO + 0.5, Y_ZOCALO + 0.01),
        (d["zocalo"], Y_ZOCALO, Y_PIE + 0.01),
        (d["pie"], Y_PIE, Y_SUELO),
    ]
    return unary_union([rect(cx - hw, y0, cx + hw, y1) for hw, y0, y1 in tramos])


def media_elipse(c, a, b, y0, n=181):
    """Mitad de arriba de una elipse de semiejes a, b con el centro en (c, y0)."""
    t = np.linspace(0, math.pi, n)
    pts = [(c + a * math.cos(v), y0 - b * math.sin(v)) for v in t]
    return Polygon(pts)


def arco(c, a_in):
    b_ext = ARRANQUE - CLAVE_EXT
    b_in = b_ext - ROSCA
    a_ext = a_in + ROSCA
    rosca = media_elipse(c, a_ext, b_ext, ARRANQUE).difference(media_elipse(c, a_in, b_in, ARRANQUE))
    piezas = [rosca, rect(c - 1.1, TABLERO[3] - 0.1, c + 1.1, CLAVE_EXT + 0.4)]  # unión de la clave con el tablero
    # Dos montantes a cada lado, entre el arco y el tablero
    s2 = a_in - MONTANTE - MIN / 2 - MONTANTE / 2 + 0.05
    for s in (s2, s2 - 2 * MONTANTE):
        for lado in (-1, 1):
            x = c + lado * s
            borde = min(abs(s) - MONTANTE / 2, a_ext - 0.01)
            y_ext = ARRANQUE - b_ext * math.sqrt(max(0.0, 1 - (borde / a_ext) ** 2))
            piezas.append(rect(x - MONTANTE / 2, TABLERO[3] - 0.1, x + MONTANTE / 2, y_ext + 0.6))
    return unary_union(piezas)


def baranda(x0, x1):
    """Pasamanos con balaustres entre x0 y x1 (bordes de los hombros de dos pilares)."""
    largo = x1 - x0
    n = max(1, round((largo + BALAUSTRE) / PASO_BALAUSTRE))  # número de huecos
    hueco = (largo - (n - 1) * BALAUSTRE) / n
    piezas = [rect(x0 - 0.05, BARANDA[0], x1 + 0.05, BARANDA[1])]
    for i in range(1, n):
        x = x0 + i * hueco + (i - 1) * BALAUSTRE
        piezas.append(rect(x, BARANDA[1] - 0.05, x + BALAUSTRE, TABLERO[2] + 0.05))
    return unary_union(piezas), hueco


def puente():
    cuerpo = abrir(rect(0, 0, PLACA_W, PLACA_H), PLACA_R)
    base, agujero = placa_con_oreja(cuerpo, (OREJA_X, OREJA_Y), OREJA_R, (1, 0), 1.6)

    piezas = [pilar(cx, d) for cx, d in PILARES]
    piezas.append(rect(TABLERO[0], TABLERO[2], TABLERO[1], TABLERO[3]))
    huecos_baranda = []
    for (c0, d0), (c1, d1) in zip(PILARES[:-1], PILARES[1:]):
        x0, x1 = c0 + d0["fuste"], c1 - d1["fuste"]          # el arco va de fuste a fuste
        piezas.append(arco((x0 + x1) / 2, (x1 - x0) / 2))
        b, h = baranda(c0 + d0["hombro"], c1 - d1["hombro"])
        piezas.append(b)
        huecos_baranda.append(h)
    dibujo = unary_union(piezas)

    t = TEXTO_ALCOI
    texto = palabra("ALCOI", t["peso"], t["alto"], PLACA_W / 2, t["base"], ancho=t["ancho"])

    relieve = unary_union([dibujo, texto])
    relieve = abrir(relieve, 0.12)          # quita aristas vivas de 90° (salen igual al imprimir)
    info = dict(huecos_baranda=huecos_baranda)
    return base, relieve.intersection(base.buffer(-0.6)), agujero, info


# -------------------------------------------------------- pieza 2: el escudo

# Borde de fuera de la banda dorada, medido en la foto (píxeles): media anchura
# por fila, tomada como la media de los dos lados.
SX, SY = 35.0 / 611, 45.0 / 775      # mm por píxel: 35 mm de ancho y 45 mm de alto en total
ESC_ARRIBA = 412                     # y (px) de lo más alto de la banda dorada
ESC_HOMBRO = (288, 472)              # esquina de los hombros
ESC_COSTADO = [(288, 480), (289, 630), (290, 730), (289.5, 780), (288, 805), (284, 830), (278, 855),
               (270, 880), (260, 905), (247, 930), (232.5, 955), (215.5, 980), (196, 1005),
               (174, 1030), (149, 1055), (121, 1080), (90, 1105), (53.5, 1130)]
ESC_PUNTA = 1166.6                   # punta prolongando el último tramo; se redondea
BORDE_FUERA = 0.85                   # negro entre el canto y la banda dorada
BORDE_ANCHO = 1.2                    # banda dorada
TEXTO_FERRER = dict(peso=800, alto=5.95, base_px=595, ancho=27.8, hueco=0.85)
# Torre (px, desde el eje)
TORRE = dict(arriba=635, almena_fondo=674, almena_abajo=700, cuello=722, suelo=982,
             ancho=120.5, almena_ext=64.5, almena_med=28.5, cuello_ancho=91, suelo_ancho=149,
             puerta_ancho=46, puerta_arranque=880)
ESTRELLAS = dict(dx=187, y=740.5, ancho=57.5, alto=64, dentro=(13.5, 15.0))
OREJA_ESC = dict(r=4.8, sobre=3.6, union=1.8)   # radio, altura del centro sobre el canto, radio de la unión


def px(dx, y):
    return dx * SX, (y - ESC_ARRIBA) * SY


def escudo():
    # Banda dorada por fuera: arco de arriba (parábola), costados y punta
    mitad = [px(dx, ESC_ARRIBA + 0.0007 * dx * dx) for dx in np.linspace(0, ESC_HOMBRO[0], 30)]
    mitad += [px(dx, y) for dx, y in ESC_COSTADO] + [px(0, ESC_PUNTA)]
    contorno = mitad + [(-x, y) for x, y in reversed(mitad[1:-1])]
    g = Polygon(contorno).buffer(0)
    y_medio = px(0, 760)[1]
    g = unary_union([abrir(g, 1.0).intersection(rect(-30, -5, 30, y_medio)),
                     abrir(g, 2.2)])            # hombros con radio 1 mm y punta con radio 2,2 mm
    cuerpo = g.buffer(BORDE_FUERA, join_style=1, quad_segs=32)
    banda = g.difference(g.buffer(-BORDE_ANCHO, join_style=1, quad_segs=32))

    # Oreja centrada arriba
    o = OREJA_ESC
    arriba = cuerpo.bounds[1]
    base, agujero = placa_con_oreja(cuerpo, (0.0, arriba - o["sobre"]), o["r"], (0, 1), o["union"])

    t = TEXTO_FERRER
    texto = palabra("FERRER", t["peso"], t["alto"], 0.0, px(0, t["base_px"])[1],
                    ancho=t["ancho"], hueco=t["hueco"])

    T = TORRE
    torre = Polygon([px(-T["ancho"], T["arriba"]), px(T["ancho"], T["arriba"]),
                     px(T["ancho"], T["almena_abajo"]), px(T["cuello_ancho"], T["cuello"]),
                     px(T["suelo_ancho"], T["suelo"]), px(-T["suelo_ancho"], T["suelo"]),
                     px(-T["cuello_ancho"], T["cuello"]), px(-T["ancho"], T["almena_abajo"])])
    almenas = [rect(*px(-T["almena_ext"], T["arriba"] - 5), *px(-T["almena_med"], T["almena_fondo"])),
               rect(*px(T["almena_med"], T["arriba"] - 5), *px(T["almena_ext"], T["almena_fondo"]))]
    r_puerta = T["puerta_ancho"] * SX
    cx, ya = px(0, T["puerta_arranque"])
    puerta = unary_union([Point(cx, ya).buffer(r_puerta, quad_segs=48),
                          rect(-r_puerta, ya, r_puerta, px(0, T["suelo"] + 20)[1])])
    torre = abrir(torre.difference(unary_union(almenas)), 0.25).difference(puerta)

    E = ESTRELLAS
    estrellas = []
    for lado in (-1, 1):
        cx, cy = px(lado * E["dx"], E["y"])
        a, b = E["ancho"] * SX, E["alto"] * SY
        di, dj = E["dentro"][0] * SX, E["dentro"][1] * SY
        estrellas.append(Polygon([(cx, cy - b), (cx + di, cy - dj), (cx + a, cy), (cx + di, cy + dj),
                                  (cx, cy + b), (cx - di, cy + dj), (cx - a, cy), (cx - di, cy - dj)]))
    estrellas = abrir(unary_union(estrellas), 0.2)   # puntas romas: lo más fino que sale es ~0,4 mm

    relieve = unary_union([banda, abrir(texto, 0.12), torre, estrellas])
    # Pasar a modelo: y hacia arriba, con lo más bajo en y = 0 y centrado en x
    info = {}
    return base, relieve, agujero, info


# -------------------------------------------------------- 3D: extruir y unir

def seccion(g):
    contornos = []
    for p in poligonos(g):
        p = orient(p, 1.0)
        contornos.append(np.asarray(p.exterior.coords)[:-1])
        contornos += [np.asarray(h.coords)[:-1] for h in p.interiors]
    return mf.CrossSection(contornos, mf.FillRule.EvenOdd)


def solido(base, relieve):
    """Base de Z 0 a 3,2 y relieve de 3,2 a 4,0 (se extruye desde 3,0 para que se
    funda con la base), unidos en un único sólido."""
    b = mf.Manifold.extrude(seccion(base), BASE)
    r = mf.Manifold.extrude(seccion(relieve), ALTO - BASE + 0.2).translate((0, 0, BASE - 0.2))
    m = (b + r).to_mesh()
    malla = trimesh.Trimesh(np.asarray(m.vert_properties)[:, :3], np.asarray(m.tri_verts), process=True)
    trimesh.repair.fix_normals(malla)
    return malla


# ---------------------------------------------------------------- vistas

def pintar(malla, ruta, inclinacion=0.0, px_mm=24, colores=None, fondo=(236, 232, 224), margen=4.0):
    """Render ortográfico con z-buffer, hecho a partir de los triángulos del STL.
    inclinacion: grados que se gira la pieza alrededor del eje x (0 = vista frontal)."""
    colores = colores or {"base": (34, 34, 36), "relieve": (232, 220, 186)}
    t = math.radians(inclinacion)
    R = np.array([[1, 0, 0], [0, math.cos(t), -math.sin(t)], [0, math.sin(t), math.cos(t)]])
    v = malla.vertices @ R.T
    n = malla.face_normals @ R.T
    s = px_mm * 2  # se pinta al doble y se reduce (antialias)
    x0, y0 = v[:, 0].min() - margen, v[:, 1].min() - margen
    x1, y1 = v[:, 0].max() + margen, v[:, 1].max() + margen
    W, H = int((x1 - x0) * s), int((y1 - y0) * s)
    sx = (v[:, 0] - x0) * s
    sy = (y1 - v[:, 1]) * s
    zb = np.full((H, W), -1e9)
    img = np.zeros((H, W, 3))
    img[:] = fondo
    luz = np.array([-0.35, 0.45, 0.82])
    luz /= np.linalg.norm(luz)
    zmax = malla.vertices[malla.faces][:, :, 2].max(1)
    for f, cara in enumerate(malla.faces):
        if n[f, 2] <= 1e-6:
            continue
        xs, ys, zs = sx[cara], sy[cara], v[cara, 2]
        bx0, bx1 = max(int(xs.min()), 0), min(int(xs.max()) + 1, W - 1)
        by0, by1 = max(int(ys.min()), 0), min(int(ys.max()) + 1, H - 1)
        if bx1 < bx0 or by1 < by0:
            continue
        gx, gy = np.meshgrid(np.arange(bx0, bx1 + 1) + 0.5, np.arange(by0, by1 + 1) + 0.5)
        (ax, bx_, cx), (ay, by_, cy) = xs, ys
        den = (by_ - cy) * (ax - cx) + (cx - bx_) * (ay - cy)
        if abs(den) < 1e-12:
            continue
        l1 = ((by_ - cy) * (gx - cx) + (cx - bx_) * (gy - cy)) / den
        l2 = ((cy - ay) * (gx - cx) + (ax - cx) * (gy - cy)) / den
        l3 = 1 - l1 - l2
        dentro = (l1 >= -1e-4) & (l2 >= -1e-4) & (l3 >= -1e-4)
        if not dentro.any():
            continue
        z = l1 * zs[0] + l2 * zs[1] + l3 * zs[2]
        sub = zb[by0:by1 + 1, bx0:bx1 + 1]
        poner = dentro & (z > sub)
        if not poner.any():
            continue
        sub[poner] = z[poner]
        col = np.array(colores["relieve"] if zmax[f] > BASE + 0.05 else colores["base"], float)
        k = 0.55 + 0.45 * max(0.0, float(n[f] @ luz))
        if abs(malla.face_normals[f, 2]) < 0.5:   # paredes: algo más oscuras
            k *= 0.8
        img[by0:by1 + 1, bx0:bx1 + 1][poner] = col * k
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).resize((W // 2, H // 2), Image.LANCZOS)
    im.save(ruta)
    return im, (x0, y1, px_mm)


# ---------------------------------------------------------------- comprobaciones

def comprobar(nombre, malla, base, relieve, agujero):
    x0, y0, z0 = malla.bounds[0]
    x1, y1, z1 = malla.bounds[1]
    cuerpos = malla.split(only_watertight=False)
    print(f"\n== {nombre}")
    print(f"  medidas: {x1 - x0:.2f} x {y1 - y0:.2f} x {z1 - z0:.2f} mm (z {z0:.3f} a {z1:.3f})")
    print(f"  triángulos: {len(malla.faces)}, cerrada: {malla.is_watertight}, volumen válido: {malla.is_volume}, "
          f"piezas: {len(cuerpos)}, volumen: {malla.volume:.0f} mm³")
    # El agujero atraviesa: ningún triángulo cruza la vertical del centro del agujero
    c = agujero.centroid
    rayo = trimesh.ray.ray_triangle.RayMeshIntersector(malla)
    golpes = rayo.intersects_location([[c.x, c.y, 10]], [[0, 0, -1]])[0]
    print(f"  agujero Ø{2 * math.sqrt(agujero.area / math.pi):.2f} mm en ({c.x:.2f}, {c.y:.2f}): "
          f"{'pasante' if len(golpes) == 0 else 'TAPADO'}; plástico alrededor mínimo "
          f"{base.exterior.distance(c) - AGUJERO / 2:.2f} mm")
    # La cara de abajo está entera en z = 0
    abajo = malla.section(plane_origin=[0, 0, 0.01], plane_normal=[0, 0, 1])
    print(f"  sección a z=0,01: área {abajo.to_2D()[0].area:.1f} mm² (base 2D {base.area:.1f} mm²)")
    arriba = malla.section(plane_origin=[0, 0, BASE + 0.1], plane_normal=[0, 0, 1])
    print(f"  sección a z=3,3: área {arriba.to_2D()[0].area:.1f} mm² (relieve 2D {relieve.area:.1f} mm²)")
    # Trazos finos y huecos estrechos del relieve
    fino = relieve.difference(abrir(relieve, MIN / 2 - 0.01))
    estrecho = cerrar(relieve, MIN / 2 - 0.01).difference(relieve).intersection(base.buffer(-0.3))
    for etiqueta, g in (("trazos < 0,8 mm", fino), ("huecos < 0,8 mm", estrecho)):
        trozos = [p for p in poligonos(g) if p.area > 0.03]
        grandes = sorted(trozos, key=lambda p: -p.area)[:4]
        desc = ", ".join(f"{p.area:.2f} mm² en ({p.centroid.x:.1f}, {p.centroid.y:.1f})" for p in grandes)
        print(f"  {etiqueta}: {len(trozos)} zonas > 0,03 mm² {('-> ' + desc) if desc else ''}")
    return dict(cerrada=malla.is_watertight, piezas=len(cuerpos))


def a_modelo(base, relieve, agujero, alto_foto=None):
    """Voltea y deja la pieza con la esquina de abajo a la izquierda en (0, 0)."""
    gs = [base, relieve, agujero]
    if alto_foto is not None:
        gs = [voltear(g, alto_foto) for g in gs]
    else:
        gs = [escalar(g, 1, -1, origin=(0, 0)) for g in gs]
    bx0, by0, _, _ = gs[0].bounds
    return [shapely.set_precision(mover(g, -bx0, -by0), 0.0005).buffer(0) for g in gs], (bx0, by0)


# ---------------------------------------------------------------- comparación con la foto

# Esquinas de la cara de arriba de la placa del puente en la foto (px), en el orden
# (0,0) (56,0) (56,30) (0,30) mm: con ellas se endereza la foto.
FOTO_PUENTE = ("pont_alcoi.jpg", [(305, 438), (1195, 370), (1212, 800), (318, 865)])
FOTO_ESCUDO = "escudo_ferrer.jpg"


def _homografia(origen, destino):
    A, B = [], []
    for (x, y), (u, v) in zip(origen, destino):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]
        B += [u, v]
    h = np.linalg.solve(np.array(A, float), np.array(B, float))
    return np.append(h, 1).reshape(3, 3)


def foto_a_px(nombre, x, y):
    """Coordenadas de foto en mm (y hacia abajo) -> píxeles de la foto original."""
    if nombre.startswith("Pont"):
        H = _homografia([(0, 0), (PLACA_W, 0), (PLACA_W, PLACA_H), (0, PLACA_H)], FOTO_PUENTE[1])
        w = H[2, 0] * x + H[2, 1] * y + H[2, 2]
        return (H[0, 0] * x + H[0, 1] * y + H[0, 2]) / w, (H[1, 0] * x + H[1, 1] * y + H[1, 2]) / w
    v = ESC_ARRIBA + y / SY
    eje = 600 + (v - 430) * 0.0279        # la foto del escudo está girada ~1,6°
    return eje + x / SX, v


def comparar(nombre, vista, marco, desplazamiento, relieve, base, ruta):
    """Foto enderezada a la misma escala que la vista, con el contorno del modelo encima."""
    from scipy.ndimage import map_coordinates
    x0, y1, px_mm = marco
    W, H = vista.size
    X, Y = np.meshgrid((np.arange(W) + 0.5) / px_mm + x0, y1 - (np.arange(H) + 0.5) / px_mm)
    bx0, by0 = desplazamiento
    xf = X + bx0
    yf = (PLACA_H - (Y + by0)) if nombre.startswith("Pont") else -(Y + by0)
    u, v = foto_a_px(nombre, xf, yf)
    foto = np.asarray(Image.open(os.path.join(AQUI, "referencias",
                                              FOTO_PUENTE[0] if nombre.startswith("Pont") else FOTO_ESCUDO)).convert("RGB"))
    canales = [map_coordinates(foto[:, :, c].astype(float), [v - 0.5, u - 0.5], order=1, mode="nearest") for c in range(3)]
    enderezada = Image.fromarray(np.clip(np.dstack(canales), 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(enderezada)

    def linea(g, color, ancho):
        for p in poligonos(g):
            for anillo in [p.exterior, *p.interiors]:
                d.line([((x - x0) * px_mm, (y1 - y) * px_mm) for x, y in anillo.coords], fill=color, width=ancho)
    linea(base, (80, 200, 255), 2)
    linea(relieve, (255, 40, 200), 2)
    hueco = 16
    lienzo = Image.new("RGB", (2 * W + hueco, H + 34), (255, 255, 255))
    lienzo.paste(enderezada, (0, 34))
    lienzo.paste(vista, (W + hueco, 34))
    dl = ImageDraw.Draw(lienzo)
    dl.text((8, 10), "Foto enderezada + contorno del modelo (azul: base, rosa: relieve)", fill=(0, 0, 0))
    dl.text((W + hueco + 8, 10), "Vista frontal del STL", fill=(0, 0, 0))
    lienzo.save(ruta)


def main():
    salida = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "salida")
    os.makedirs(salida, exist_ok=True)

    piezas = [
        ("Pont_de_Sant_Jordi_ALCOI", puente, PLACA_H, {"base": (30, 30, 32), "relieve": (234, 222, 188)}),
        ("Escudo_FERRER", escudo, None, {"base": (30, 30, 32), "relieve": (236, 168, 40)}),
    ]
    for nombre, fn, alto_foto, colores in piezas:
        base, relieve, agujero, info = fn()
        (base, relieve, agujero), desplazamiento = a_modelo(base, relieve, agujero, alto_foto)
        malla = solido(base, relieve)
        malla.export(os.path.join(salida, f"{nombre}.stl"))
        comprobar(nombre, malla, base, relieve, agujero)
        for k, val in info.items():
            print(f"  {k}: {np.round(val, 2).tolist()}")
        vista, marco = pintar(malla, os.path.join(salida, f"{nombre}_vista_frontal.png"), 0, colores=colores)
        pintar(malla, os.path.join(salida, f"{nombre}_vista_3d.png"), -35, colores=colores)
        comparar(nombre, vista, marco, desplazamiento, relieve, base,
                 os.path.join(salida, f"{nombre}_comparacion.png"))


if __name__ == "__main__":
    main()

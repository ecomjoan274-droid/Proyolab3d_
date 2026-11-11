"""Dibujo vectorial del Tirisiti para las bolas de Navidad.

Las formas se dibujan con curvas suaves sobre la foto `personaje.png` (en su
tamaño x4: 628 x 2168 px, el personaje centrado en x = 290) y se pasan a mm.
Cada forma lleva un contorno negro de grosor uniforme, como una ilustración.

El resultado es un dict color -> geometría (shapely, en mm), con las zonas de
cada color sin solaparse. Lo que no tiene color se queda en el blanco de la base.
"""
import math

import numpy as np
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

COLORES = ("rojo", "negro", "azul")
X_CENTRO = 290
TRAZO_MIN = 0.5  # mm


def curva(pts, cerrada=True, pasos=12):
    """Curva Catmull-Rom que pasa por los puntos. Un punto con tercer valor 'p' es una esquina."""
    if not cerrada:
        pts = [pts[0]] + list(pts) + [pts[-1]]
    n = len(pts)
    res = []
    rango = range(n) if cerrada else range(1, n - 2)
    for i in rango:
        p0, p1, p2, p3 = (pts[(i + k - 1) % n] for k in range(4))
        if len(p1) > 2:   # esquina: sale recta
            p0 = p1
        if len(p2) > 2:
            p3 = p2
        p0, p1, p2, p3 = (np.array(p[:2], float) for p in (p0, p1, p2, p3))
        for t in np.linspace(0, 1, pasos, endpoint=False):
            t2, t3 = t * t, t * t * t
            res.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    if not cerrada:
        res.append(np.array(pts[-2][:2], float))
    return res


def espejo(pts):
    """Refleja puntos respecto al centro del personaje (para hacer el lado derecho)."""
    return [(2 * X_CENTRO - p[0],) + tuple(p[1:]) for p in pts]


class Lienzo:
    def __init__(self, escala, y_arriba, contorno):
        self.s, self.y0, self.w = escala, y_arriba, contorno
        self.zonas = {c: Polygon() for c in COLORES}

    def mm(self, pts):
        return [((p[0] - X_CENTRO) * self.s, self.y0 - p[1] * self.s) for p in pts]

    def pintar(self, geom, color):
        geom = geom.buffer(0)
        for c in COLORES:
            self.zonas[c] = self.zonas[c].difference(geom)
        if color != "blanco":
            self.zonas[color] = self.zonas[color].union(geom)

    def forma(self, pts, color, contorno=True, suave=True):
        p = Polygon(self.mm(curva(pts) if suave else pts)).buffer(0)
        self.pintar(p, color)
        if contorno:
            self.pintar(p.exterior.buffer(self.w / 2, join_style=1), "negro")
        return p

    def trazo(self, pts, ancho=None, color="negro", suave=True, cap=1):
        linea = LineString(self.mm(curva(pts, cerrada=False) if suave else pts))
        ancho = max(ancho or self.w, TRAZO_MIN)  # más fino no lo hace una boquilla de 0,4
        self.pintar(linea.buffer(ancho / 2, cap_style=cap), color)

    def circulo(self, x, y, r_px, color):
        (cx, cy), = self.mm([(x, y)])
        self.pintar(Point(cx, cy).buffer(r_px * self.s, 32), color)


# ---------------------------------------------------------------- personaje

def cabeza(L, detalle):
    # Pelo (detrás de la cara)
    L.forma([(150, 392), (143, 300), (148, 190), (178, 122), (240, 86), (300, 80), (365, 88),
             (412, 115), (437, 170), (442, 270), (436, 392), (420, 400), (300, 300), (165, 400)], "negro")
    # Boina, ladeada hacia la izquierda
    L.forma([(122, 178), (114, 110), (128, 52), (172, 22), (232, 24), (290, 30), (338, 10),
             (395, 8), (430, 38), (436, 82), (410, 108), (360, 98), (290, 92), (225, 104),
             (180, 128), (156, 170), (140, 192)], "rojo")
    if detalle:  # pliegue de la boina
        L.trazo([(330, 22), (345, 55), (368, 92)], L.w * 0.8)
    # Cuello
    L.forma([(238, 440, "p"), (346, 440, "p"), (350, 528, "p"), (234, 528, "p")], "blanco", suave=False)
    # Cara: entradas del pelo con pico en el centro y mandíbula de muñeco tallado
    L.forma([(162, 262), (166, 205), (190, 150), (240, 128), (292, 152), (342, 126), (392, 140),
             (418, 190), (424, 262), (418, 360), (402, 425), (368, 475), (300, 500), (240, 492),
             (200, 450), (176, 390)], "blanco")
    # Cejas, gruesas y caídas hacia fuera
    ceja = [(176, 238), (192, 200), (230, 180), (276, 178), (284, 196), (240, 200), (205, 214), (186, 240)]
    L.forma(ceja, "negro", contorno=False)
    L.forma(espejo(ceja), "negro", contorno=False)
    # Ojos
    ojo = [(188, 250), (206, 228), (236, 220), (266, 228), (282, 248), (262, 264), (232, 270), (202, 263)]
    for pts, px in ((ojo, 240), (espejo(ojo), 340)):
        if detalle:
            L.forma(pts, "blanco")
            L.circulo(px, 246, 21, "negro")
            L.circulo(px + 6, 238, 6.5, "blanco")   # brillo
            L.trazo(pts[:5], L.w * 1.4)              # párpado de arriba más grueso
        else:
            L.circulo(px, 246, 26, "negro")
    # Nariz larga: un lado y la base
    L.trazo([(306, 236), (314, 290), (322, 340)], L.w * 0.8)
    L.trazo([(266, 350), (292, 358), (324, 348)], L.w)
    # Boca
    labios = [(252, 406), (272, 392), (290, 398), (308, 392), (328, 406), (310, 420), (290, 424), (270, 420)]
    if detalle:
        L.forma(labios, "rojo", contorno=False)
        L.trazo([(254, 406), (290, 409), (326, 406)], L.w * 0.7)
    else:
        L.forma(labios, "negro", contorno=False)


def torso(L, entero, detalle):
    abajo = 1070 if entero else 1500
    manga = 1172 if entero else 1500
    # Chaqueta con las mangas pegadas al cuerpo
    L.forma([(18, 900), (28, 640), (64, 560), (130, 530), (215, 520), (290, 538, "p"), (365, 520),
             (450, 530), (516, 560), (552, 640), (566, 900), (578, manga, "p"), (470, manga, "p"),
             (466, abajo, "p"), (290, abajo + 6), (114, abajo, "p"), (110, manga, "p"), (6, manga, "p")], "rojo")
    # Costuras de las mangas
    L.trazo([(112, 640), (106, 900), (110, manga)], L.w * 0.8)
    L.trazo([(468, 640), (474, 900), (470, manga)], L.w * 0.8)
    # Abertura en V con la camisa
    v = [(212, 522, "p"), (290, 544), (368, 522, "p"), (338, 640), (300, 820), (290, 836, "p"),
         (280, 820), (242, 640)]
    L.forma(v, "blanco")
    # Cuello de la camisa
    L.forma([(222, 504, "p"), (358, 504, "p"), (370, 548), (330, 566), (290, 556, "p"), (250, 566),
             (210, 548)], "blanco")
    # Corbata: nudo y pala
    L.forma([(270, 554, "p"), (312, 554, "p"), (304, 600, "p"), (278, 600, "p")], "azul", suave=False)
    L.forma([(278, 600, "p"), (304, 600, "p"), (320, 740), (296, 812, "p"), (268, 742)], "azul")
    # Solapas
    solapa = [(166, 530), (214, 640), (250, 742), (282, 826)]
    L.trazo(solapa, L.w * 0.8)
    L.trazo(espejo(solapa), L.w * 0.8)
    if detalle:  # botones
        for y in (900, 1010):
            L.circulo(290, y, 16, "negro")
    else:
        L.circulo(290, 930, 22, "negro")
    if entero:
        # Bajo de la chaqueta
        L.trazo([(114, 1020), (290, 1028), (466, 1020)], L.w * 0.8)


def piernas(L):
    # Manos
    mano = [(44, 1172, "p"), (100, 1172, "p"), (96, 1260), (84, 1300), (62, 1302), (50, 1270)]
    L.forma(mano, "blanco")
    L.forma(espejo(mano), "blanco")
    # Pantalón: dos perneras con una raya blanca entre ellas
    L.forma([(124, 1068, "p"), (456, 1068, "p"), (462, 1450), (446, 1868, "p"), (134, 1868, "p"),
             (120, 1450)], "negro", contorno=False)
    L.trazo([(290, 1250), (290, 1868)], L.w * 1.1, "blanco", suave=False, cap=2)
    L.trazo([(124, 1850), (456, 1850)], L.w * 1.1, "blanco", suave=False, cap=2)
    # Zapatos
    zapato = [(282, 1878, "p"), (282, 1946, "p"), (110, 1946), (92, 1915), (120, 1882)]
    L.forma(zapato, "negro", contorno=False)
    L.forma(espejo(zapato), "negro", contorno=False)


def personaje(escala, y_arriba, contorno, entero, detalle):
    L = Lienzo(escala, y_arriba, contorno)
    torso(L, entero, detalle)
    if entero:
        piernas(L)
    cabeza(L, detalle)
    return L.zonas


# ---------------------------------------------------------------- adornos

def copo(cx, cy, r, ancho=0.7):
    """Copo de nieve de seis brazos; los grandes llevan ramitas."""
    partes = []
    for i in range(6):
        a = math.pi / 2 + i * math.pi / 3
        dx, dy = math.cos(a), math.sin(a)
        partes.append(LineString([(cx, cy), (cx + r * dx, cy + r * dy)]))
        if r >= 3.5:
            for f, l in ((0.55, 0.38), (0.8, 0.22)):
                bx, by = cx + f * r * dx, cy + f * r * dy
                for s in (-1, 1):
                    b = a + s * math.pi / 3
                    partes.append(LineString([(bx, by), (bx + l * r * math.cos(b), by + l * r * math.sin(b))]))
    return unary_union(partes).buffer(ancho / 2, cap_style=1, join_style=1)

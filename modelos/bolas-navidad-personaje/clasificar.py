"""Separa el dibujo del personaje en 4 colores imprimibles.

Devuelve un mapa de niveles por píxel:
  -1 fuera del personaje, 0 blanco, 1 rojo, 2 piel, 3 negro
"""
import colorsys

import numpy as np
from PIL import Image

FUERA, BLANCO, ROJO, PIEL, NEGRO = -1, 0, 1, 2, 3
FILA_CUELLO = 126     # por encima: cabeza
FILA_PANTALON = 264   # por debajo: pantalón, manos y zapatos
FILA_FIN = 478        # por debajo: peana, que se descarta


def clasificar(ruta):
    im = np.asarray(Image.open(ruta).convert("RGBA")).astype(float)
    h, w, _ = im.shape
    out = np.full((h, w), FUERA, dtype=int)
    for y in range(min(h, FILA_FIN)):
        for x in range(w):
            r, g, b, a = im[y, x]
            if a < 128:
                continue
            hh, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            hue = hh * 360
            rojizo = hue < 20 or hue > 335
            if y < FILA_CUELLO:  # cabeza: boina, pelo, cara
                en_ojo = 52 <= y <= 70 and (44 <= x <= 70 or 78 <= x <= 100)
                en_boina = y < 45 or (x < 38 and y < 52)
                if s < 0.28 and v > 0.72:
                    c = BLANCO if en_ojo else PIEL
                elif rojizo and s > 0.62 and r > 2.6 * g and v > 0.27:
                    if en_boina:
                        c = ROJO
                    elif 84 <= y <= 92 and 62 <= x <= 84:
                        c = NEGRO  # base de la nariz
                    else:
                        c = PIEL
                elif v < 0.50 and not (rojizo and s > 0.5 and v > 0.38):
                    c = NEGRO
                elif b > 0.95 * r and v < 0.62:
                    c = NEGRO
                else:
                    c = PIEL
            elif y < FILA_PANTALON:  # camisa, corbata, chaqueta
                if s < 0.25 and v > 0.70:
                    c = BLANCO
                elif b >= 0.92 * r and v < 0.75:
                    c = NEGRO
                elif y < FILA_CUELLO + 5 and 50 <= x <= 95:
                    c = PIEL  # sombra del cuello, no es chaqueta
                else:
                    c = ROJO
            else:  # pantalón, manos, zapatos
                mano = x < 30 or x > 116
                naranja = 14 <= hue <= 55 and s > 0.5 and v > 0.45
                if mano:
                    if y > 305:
                        continue
                    c = PIEL if (y >= 270 or (v > 0.5 and g > 0.35 * r)) else ROJO
                elif y >= 440 and naranja:
                    continue  # peana
                elif rojizo and s > 0.7 and v > 0.45 and y < 275:
                    c = ROJO  # bajo de la chaqueta
                else:
                    c = NEGRO
            out[y, x] = c
    _agrandar_ojos(out)
    _engordar_nariz(out)
    return out


def _agrandar_ojos(out):
    """En el dibujo el blanco del ojo es una rendija; se ensancha para que se pueda imprimir."""
    from scipy import ndimage
    for fila, col in ((61, 58), (61, 88)):
        if out[fila, col] != NEGRO:
            continue
        y0, y1, x0, x1 = fila - 9, fila + 9, col - 15, col + 15
        zona = out[y0:y1, x0:x1]
        etiquetas, _ = ndimage.label(zona == NEGRO)
        pupila = etiquetas == etiquetas[fila - y0, col - x0]
        etiquetas, _ = ndimage.label(pupila | (zona == BLANCO))
        ojo = etiquetas == etiquetas[fila - y0, col - x0]
        ojo = ndimage.binary_dilation(ojo, structure=np.ones((1, 3), bool)) & (
            pupila | (zona == BLANCO) | (zona == PIEL))
        nueva = ndimage.binary_erosion(pupila, structure=np.ones((1, 5), bool))
        zona[(zona == BLANCO) & ~ojo] = PIEL
        zona[ojo] = BLANCO
        zona[nueva] = NEGRO


def _engordar_nariz(out):
    zona = out[83:94, 60:86]
    ys, xs = np.nonzero(zona == NEGRO)
    for y, x in zip(ys, xs):
        if y + 1 < zona.shape[0] and zona[y + 1, x] == PIEL:
            zona[y + 1, x] = NEGRO


COLORES = {FUERA: (120, 200, 120), BLANCO: (245, 245, 245), ROJO: (200, 30, 35),
           PIEL: (232, 160, 125), NEGRO: (25, 25, 30)}

if __name__ == "__main__":
    import sys
    m = clasificar(sys.argv[1])
    rgb = np.zeros(m.shape + (3,), dtype=np.uint8)
    for k, col in COLORES.items():
        rgb[m == k] = col
    Image.fromarray(rgb).resize((m.shape[1] * 4, m.shape[0] * 4), Image.NEAREST).save(sys.argv[2])

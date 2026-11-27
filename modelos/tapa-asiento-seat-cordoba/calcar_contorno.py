#!/usr/bin/env python3
"""Calca el contorno de la tapa 191 881 478 de una foto cenital sobre fondo claro.

Uso: calcar_contorno.py foto.jpg [contorno.json]

Foto usada: la del anuncio de omecar.de (pieza nueva, plana y vista desde arriba):
https://omecar.de/wp-content/uploads/imported/3/VW-Golf-2-GT-GTI-16V-G60-Rallye-Verkleidung-Blende-Abdeckung-Sitz-191881478-LX6-326428267383.jpg

1. Separa la pieza (oscura) del fondo (claro) y se queda con la mancha más grande.
2. Gira la foto para que el canto de arriba (el largo y recto) quede horizontal.
3. Escala a LARGO_REAL mm (medida del catálogo Volkswagen Classic Parts: 210 x 95 x 15 mm).
4. Saca el contorno, el círculo del anillo de la cúpula y los centros de los tres agujeros.

Guarda todo en mm en contorno.json, que es lo que usa generar.py.
"""
import json
import os
import sys

import contourpy
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

LARGO_REAL = 210.0   # mm, Volkswagen Classic Parts
ABAJO_FUERA = 925    # en la foto de omecar, por debajo de esta fila está la etiqueta de la tienda


def main():
    foto = sys.argv[1]
    salida = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                                 "contorno.json")
    gris = np.asarray(Image.open(foto).convert("L"), float)
    gris[ABAJO_FUERA:, :] = 255

    # 1. La pieza
    m = gris < 140
    lab, n = ndi.label(m)
    m = lab == (np.argmax(ndi.sum(m, lab, range(1, n + 1))) + 1)
    m = ndi.binary_opening(ndi.binary_fill_holes(m), iterations=2)

    # 2. Ángulo del canto de arriba (columnas del tramo recto)
    ys, xs = np.nonzero(m)
    x0, x1 = xs.min(), xs.max()
    col = np.arange(int(x0 + 0.42 * (x1 - x0)), int(x0 + 0.92 * (x1 - x0)))
    arriba = np.array([np.argmax(m[:, x]) for x in col])
    pend = np.polyfit(col, arriba, 1)[0]
    ang = float(np.degrees(np.arctan(pend)))
    mr = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).rotate(ang, Image.BICUBIC, expand=True)) > 127
    gr = np.asarray(Image.fromarray(gris.astype(np.uint8)).rotate(ang, Image.BICUBIC, expand=True, fillcolor=255), float)

    ys, xs = np.nonzero(mr)
    x0, x1, y1 = xs.min(), xs.max(), ys.max()
    s = LARGO_REAL / (x1 - x0)

    def a_mm(x, y):
        return [round(float((x - x0) * s), 3), round(float((y1 - y) * s), 3)]

    # 3. Contorno: se suaviza el borde (textura y ruido de la foto) y se saca la línea de 0,5
    suave = ndi.gaussian_filter(mr.astype(float), 2.5)
    lineas = contourpy.contour_generator(z=suave).lines(0.5)
    borde = max(lineas, key=len)
    # Suavizado a lo largo del borde (la textura de la pieza deja mellas de ~1 mm en la foto)
    borde = ndi.gaussian_filter1d(borde[:-1], 9, axis=0, mode="wrap")
    contorno = [a_mm(x, y) for x, y in borde[::3]]
    # Techo de la muesca: en la foto la textura lo deja ondulado; se cambia por una curva suave
    c_np = np.array(contorno)
    techo = (c_np[:, 0] > 112) & (c_np[:, 0] < 141) & (c_np[:, 1] > 18) & (c_np[:, 1] < 0.4 * c_np[:, 1].max())
    if techo.sum() > 10:
        coef = np.polyfit(c_np[techo, 0], c_np[techo, 1], 4)
        for i in np.nonzero(techo)[0]:
            contorno[i][1] = round(float(np.polyval(coef, contorno[i][0])), 3)

    # 4. Círculo del anillo: ajuste por mínimos cuadrados al borde izquierdo
    pts = []
    for y in range(int(ys.min() + 20), int(y1 - 40), 4):
        fila = np.nonzero(mr[y])[0]
        if len(fila) and fila[0] - x0 < 0.115 * (x1 - x0):
            pts.append((fila[0], y))
    p = np.array(pts, float)
    A = np.c_[2 * p[:, 0], 2 * p[:, 1], np.ones(len(p))]
    cx, cy, c = np.linalg.lstsq(A, (p ** 2).sum(1), rcond=None)[0]
    r = float(np.sqrt(c + cx ** 2 + cy ** 2))

    # 5. Agujeros: manchas muy oscuras dentro de la pieza, fuera de la cúpula
    oscuro = (ndi.gaussian_filter(gr, 2) < 35) & ndi.binary_erosion(mr, iterations=15)
    lab, n = ndi.label(oscuro)
    agujeros = []
    for i in range(1, n + 1):
        yy, xx = np.nonzero(lab == i)
        if 300 < len(yy) < 3000 and np.hypot(xx.mean() - cx, yy.mean() - cy) > r * 1.1:
            agujeros.append(a_mm(xx.mean(), yy.mean()))
    agujeros.sort()

    datos = {
        "fuente": "foto cenital de omecar.de, escalada al largo del catálogo VW Classic Parts (210 mm)",
        "giro_grados": round(ang, 3),
        "mm_por_pixel": round(s, 5),
        "medidas_mm": [round(float((x1 - x0) * s), 2), round(float((y1 - ys.min()) * s), 2)],
        "anillo": {"centro": a_mm(cx, cy), "radio": round(float(r * s), 3)},
        "agujeros": agujeros,
        "contorno": contorno,
    }
    with open(salida, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=1)
    print(f"giro {ang:.2f}°, {datos['medidas_mm'][0]} x {datos['medidas_mm'][1]} mm, "
          f"anillo r {r * s:.2f} mm en {datos['anillo']['centro']}, agujeros {agujeros}, "
          f"{len(contorno)} puntos")


if __name__ == "__main__":
    main()

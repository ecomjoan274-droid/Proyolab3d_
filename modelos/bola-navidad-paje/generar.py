#!/usr/bin/env python3
"""Genera la bola de Navidad plana del paje, lista para imprimir en 3D.

Uso: generar.py [carpeta_salida]

Mismo formato que las bolas del Tirisiti (../bolas-navidad-personaje): disco de
80 mm con anilla, relieve por escalones y un color por escalón:

  0,0 a 1,6 mm  base    blanco   filamento 1 (fondo y ojos)
  1,6 a 2,2 mm  nivel 1 rojo     filamento 2 (fez, sonrisa, aro y puntos)
  2,2 a 2,8 mm  nivel 2 negro    filamento 3 (cara, borla, pupilas, contornos y filete del aro)
  2,8 a 3,4 mm  nivel 3 azul     filamento 4 (copos de nieve)
"""
import os
import sys

import numpy as np
import shapely
import trimesh
from shapely.geometry import Point, box
from shapely.ops import unary_union

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "bolas-navidad-personaje"))

from diseno import copo  # noqa: E402
from generar import (AGUJERO, ARO, BASE, CAMA, DIAMETRO, ESCALON, NOMBRES,  # noqa: E402
                     extruir, limpiar, vista_previa)
from proyecto_3mf import escribir_3mf  # noqa: E402
from dibujo_paje import paje  # noqa: E402

PIEZAS = ["Base y ojos (blanco)", "Fez, sonrisa y aro (rojo)",
          "Cara, borla y pupilas (negro)", "Copos de nieve (azul)"]
TITULO = "Bola paje"

COPOS = [(-29.5, -7, 4.6), (29.5, -7, 4.6), (-26, 16, 3.4), (26, 16, 3.4),
         (-19, -27.5, 2.8), (19, -27.5, 2.8)]
PUNTOS = [(-20, 29, 0.9), (20, 29, 0.9), (-32.5, 6, 0.8), (32.5, 6, 0.8),
          (-28.5, -19, 0.8), (28.5, -19, 0.8), (0, -33, 0.8)]


def construir():
    r = DIAMETRO / 2
    disco = Point(0, 0).buffer(r, 128)
    interior = Point(0, 0).buffer(r - ARO, 128)
    hueco = Point(0, r + 4.5).buffer(AGUJERO / 2, 48)
    tapa = box(-8.5, r - 3, 8.5, r + 7.5).buffer(2.0, 16)
    silueta = disco.union(tapa).difference(hueco)

    zonas = {c: g.intersection(interior) for c, g in paje().items()}
    figura = unary_union(list(zonas.values()))

    filete = Point(0, 0).buffer(r - ARO - 0.8, 128).difference(Point(0, 0).buffer(r - ARO - 1.4, 128))
    filete = filete.difference(figura.buffer(0.8))
    banda = box(-10.5, r + 0.6, 10.5, r + 1.4).intersection(tapa)
    copos = unary_union([copo(x, y, rr) for x, y, rr in COPOS]).difference(figura.buffer(1.2))
    puntos = unary_union([Point(x, y).buffer(rr, 24) for x, y, rr in PUNTOS]).difference(figura.buffer(1.2))
    aro = silueta.difference(interior)

    rojo = unary_union([zonas["rojo"], aro, puntos])
    negro = unary_union([zonas["negro"], filete, banda])
    azul = unary_union([zonas["azul"], copos])
    # Cada nivel apoya en el de debajo. Los ojos no están en ningún nivel: se ve el blanco de la base.
    n3 = limpiar(azul)
    n2 = limpiar(negro.union(n3))
    n1 = limpiar(rojo.union(n2))
    n2, n3 = n2.intersection(n1), n3.intersection(n2)
    return [shapely.set_precision(g.buffer(0), 0.002).buffer(0) for g in (silueta, n1, n2, n3)]


def main():
    salida = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "salida")
    os.makedirs(salida, exist_ok=True)
    niveles = construir()
    mallas = []
    for i, geom in enumerate(niveles):
        z0 = 0 if i == 0 else BASE + (i - 1) * ESCALON
        alto = BASE if i == 0 else ESCALON
        m = extruir(geom, z0, alto)
        m.export(os.path.join(salida, f"bola_paje_{NOMBRES[i]}.stl"))
        mallas.append(m)
        print(f"{NOMBRES[i]}: {len(m.faces)} triángulos, cerrada={m.is_watertight}, "
              f"z {m.bounds[0][2]:.1f}-{m.bounds[1][2]:.1f} mm")
    entera = trimesh.boolean.union(mallas, engine="manifold")
    entera.export(os.path.join(salida, "bola_paje_completa.stl"))
    print(f"completa: {len(entera.faces)} triángulos, cerrada={entera.is_watertight}, "
          f"medidas {np.round(entera.extents, 1)} mm")
    vista_previa(niveles, os.path.join(salida, "bola_paje_vista.png"))
    escribir_3mf(os.path.join(salida, "bola_paje_multicolor.3mf"), [
        dict(nombre=TITULO, posicion=(CAMA / 2, CAMA / 2),
             piezas=[(PIEZAS[i], m, i + 1) for i, m in enumerate(mallas)])])


if __name__ == "__main__":
    main()

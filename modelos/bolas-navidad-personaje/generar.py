#!/usr/bin/env python3
"""Genera bolas de Navidad planas con el personaje, listas para imprimir en 3D.

Uso: generar.py [carpeta_salida]

Cada bola es un disco con anilla para colgar. El personaje está dibujado con
curvas (diseno.py) y va en relieve por escalones; cada escalón es de un solo
color (filamento):

  0,0 a 1,6 mm  base    blanco   filamento 1 (fondo, cara, manos y camisa)
  1,6 a 2,2 mm  nivel 1 rojo     filamento 2 (chaqueta, boina, aro y estrellas)
  2,2 a 2,8 mm  nivel 2 negro    filamento 3 (pelo, ojos, contornos, pantalón y filete del aro)
  2,8 a 3,4 mm  nivel 3 azul     filamento 4 (corbata y copos de nieve)

Cuatro colores, uno por cada hueco del ACE Pro. La cara y las manos van en
blanco con un contorno negro, para que se distingan del fondo blanco.

Como en cada capa solo hay un color, la impresora cambia de filamento tres
veces en toda la impresión y casi no gasta material en purgas.

Salida: STL por color, STL de una pieza y 3MF con cada pieza ya asignada a su
filamento (formato de proyecto de Anycubic Slicer Next / OrcaSlicer).
"""
import math
import os
import sys

import shapely
import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFilter
from shapely.geometry import MultiPolygon, Point, Polygon, box
from shapely.ops import unary_union

from diseno import copo, personaje
from proyecto_3mf import escribir_3mf

AQUI = os.path.dirname(os.path.abspath(__file__))

DIAMETRO = 80.0      # mm
ARO = 2.5            # ancho del borde en relieve
BASE = 1.6           # grosor de la base blanca
ESCALON = 0.6        # altura de cada color (3 capas de 0,2 mm)
AGUJERO = 4.4        # diámetro del agujero para el hilo
NOMBRES = ["0_base_blanco", "1_rojo", "2_negro", "3_azul"]
PIEZAS = ["Base, cara y camisa (blanco)", "Chaqueta, boina y aro (rojo)", "Pelo, ojos, contornos y pantalon (negro)", "Corbata y copos de nieve (azul)"]
COLORES = [(246, 246, 244), (200, 30, 36), (28, 28, 32), (30, 80, 190)]

VERSIONES = {
    # escala: mm por píxel del dibujo de referencia (x4); y_arriba: altura (mm) de la fila 0
    "busto": dict(escala=0.085, y_arriba=34.0, contorno=0.7, entero=False, detalle=True,
                  copos=[(-27, 17, 4.6), (27, 17, 4.6), (-31.5, 2, 2.6), (31.5, 2, 2.6)],
                  puntos=[(-21, 28, 0.9), (21, 28, 0.9), (-24, 7.5, 0.8), (24, 7.5, 0.8),
                          (-33, 11, 0.7), (33, 11, 0.7)]),
    "cuerpo_entero": dict(escala=0.0355, y_arriba=34.0, contorno=0.5, entero=True, detalle=False,
                          copos=[(-21, 15, 5.0), (21, 15, 5.0), (-25, -6, 3.8), (25, -6, 3.8),
                                 (-17, -23, 3.0), (17, -23, 3.0)],
                          puntos=[(-13, 27, 1.0), (13, 27, 1.0), (-30, 5, 0.9), (30, 5, 0.9),
                                  (-14, -9, 0.9), (14, -9, 0.9), (-27, -17, 0.9), (27, -17, 0.9)]),
}


def poligonos(geom):
    if geom.is_empty:
        return []
    if isinstance(geom, Polygon):
        return [geom]
    return [g for g in getattr(geom, "geoms", []) if isinstance(g, Polygon)]


def limpiar(geom, ancho_min=0.4, area_min=0.3):
    """Quita trozos más finos que la boquilla puede hacer y migas sueltas."""
    g = geom.buffer(-ancho_min / 2, join_style=1).buffer(ancho_min / 2, join_style=1)
    return unary_union([p for p in poligonos(g) if p.area >= area_min]).buffer(0)


def extruir(geom, z0, alto):
    partes = []
    for p in poligonos(geom):
        if p.area < 0.01:
            continue
        m = trimesh.creation.extrude_polygon(p, alto)
        for retoque in (0.003, 0.01, 0.03):  # si la malla no cierra, se retoca el contorno
            if m.is_watertight:
                break
            q = max(poligonos(p.buffer(retoque).simplify(retoque)), key=lambda g: g.area)
            m = trimesh.creation.extrude_polygon(q, alto)
        if not m.is_watertight:  # último recurso: se trocea en franjas, que sí cierran
            x0, _, x1, _ = p.bounds
            franjas = np.arange(x0, x1 + 3, 3)
            trozos = [p.intersection(box(a, -999, b, 999)) for a, b in zip(franjas[:-1], franjas[1:])]
            partes.append(extruir(MultiPolygon([t for g in trozos for t in poligonos(g)]), 0, alto))
            continue
        partes.append(m)
    malla = trimesh.util.concatenate(partes)
    malla.apply_translation((0, 0, z0))
    return malla


def construir(nombre, cfg):
    r = DIAMETRO / 2
    disco = Point(0, 0).buffer(r, 128)
    interior = Point(0, 0).buffer(r - ARO, 128)
    hueco = Point(0, r + 4.5).buffer(AGUJERO / 2, 48)
    tapa = box(-8.5, r - 3, 8.5, r + 7.5).buffer(2.0, 16)
    silueta = disco.union(tapa).difference(hueco)

    zonas = personaje(cfg["escala"], cfg["y_arriba"], cfg["contorno"], cfg["entero"], cfg["detalle"])
    zonas = {c: g.intersection(interior) for c, g in zonas.items()}
    figura = unary_union(list(zonas.values()))

    # Marco: aro rojo, filete negro por dentro y una banda negra en la base de la anilla
    filete = Point(0, 0).buffer(r - ARO - 0.8, 128).difference(Point(0, 0).buffer(r - ARO - 1.4, 128))
    filete = filete.difference(figura.buffer(0.8))
    banda = box(-10.5, r + 0.6, 10.5, r + 1.4).intersection(tapa)
    copos = unary_union([copo(x, y, rr) for x, y, rr in cfg["copos"]]).difference(figura.buffer(1.2))
    puntos = unary_union([Point(x, y).buffer(rr, 24) for x, y, rr in cfg["puntos"]]).difference(figura.buffer(1.2))
    aro = silueta.difference(interior)

    rojo = unary_union([zonas["rojo"], aro, puntos])
    negro = unary_union([zonas["negro"], filete, banda])
    azul = unary_union([zonas["azul"], copos])
    # Cada nivel apoya en el de debajo: el rojo lleva debajo lo negro y lo azul, y el negro lo azul
    n3 = limpiar(azul)
    n2 = limpiar(negro.union(n3))
    n1 = limpiar(rojo.union(n2))
    n2, n3 = n2.intersection(n1), n3.intersection(n2)
    return [shapely.set_precision(g.buffer(0), 0.002).buffer(0) for g in (silueta, n1, n2, n3)]


def vista_previa(niveles, ruta, px=12):
    lado = int((DIAMETRO + 24) * px)
    cx, cy = lado / 2, lado / 2 + 4 * px

    def pts(c):
        return [(cx + x * px, cy - y * px) for x, y in c]

    img = Image.new("RGB", (lado, lado), (226, 232, 230))
    for geom, color in zip(niveles, COLORES):
        mask = Image.new("L", (lado, lado), 0)
        for p in poligonos(geom):
            tmp = Image.new("L", (lado, lado), 0)
            d = ImageDraw.Draw(tmp)
            d.polygon(pts(p.exterior.coords), fill=255)
            for h in p.interiors:
                d.polygon(pts(h.coords), fill=0)
            mask = Image.fromarray(np.maximum(np.asarray(mask), np.asarray(tmp)))
        sombra = Image.new("L", (lado, lado), 0)
        sombra.paste(mask, (int(0.35 * px), int(0.45 * px)))
        sombra = sombra.filter(ImageFilter.GaussianBlur(px * 0.35)).point(lambda v: int(v * 0.45))
        img.paste((40, 40, 40), (0, 0), sombra)
        img.paste(color, (0, 0), mask)
    img.save(ruta)


TITULOS = {"busto": "Bola Tirisiti busto", "cuerpo_entero": "Bola Tirisiti cuerpo entero"}
CAMA = 255.0  # lado de la cama de la Kobra 3, en mm


def main():
    salida = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "salida")
    os.makedirs(salida, exist_ok=True)
    objetos = {}
    for nombre, cfg in VERSIONES.items():
        niveles = construir(nombre, cfg)
        mallas = []
        for i, geom in enumerate(niveles):
            z0 = 0 if i == 0 else BASE + (i - 1) * ESCALON
            alto = BASE if i == 0 else ESCALON
            m = extruir(geom, z0, alto)
            m.export(os.path.join(salida, f"bola_{nombre}_{NOMBRES[i]}.stl"))
            mallas.append(m)
            print(f"{nombre} {NOMBRES[i]}: {len(m.faces)} triángulos, cerrada={m.is_watertight}, "
                  f"z {m.bounds[0][2]:.1f}-{m.bounds[1][2]:.1f} mm")
        entera = trimesh.boolean.union(mallas, engine="manifold")
        entera.export(os.path.join(salida, f"bola_{nombre}_completa.stl"))
        print(f"{nombre} completa: {len(entera.faces)} triángulos, cerrada={entera.is_watertight}, "
              f"medidas {np.round(entera.extents, 1)} mm")
        vista_previa(niveles, os.path.join(salida, f"bola_{nombre}_vista.png"))

        piezas = [(PIEZAS[i], m, i + 1) for i, m in enumerate(mallas)]
        objetos[nombre] = piezas
        escribir_3mf(os.path.join(salida, f"bola_{nombre}_multicolor.3mf"),
                     [dict(nombre=TITULOS[nombre], posicion=(CAMA / 2, CAMA / 2), piezas=piezas)])

    vistas = [Image.open(os.path.join(salida, f"bola_{n}_vista.png")) for n in VERSIONES]
    juntas = Image.new("RGB", (sum(v.width for v in vistas), vistas[0].height))
    for i, v in enumerate(vistas):
        juntas.paste(v, (i * vistas[0].width, 0))
    juntas.save(os.path.join(salida, "vista_las_dos_bolas.png"))

    # Las dos bolas en la misma placa: comparten los cambios de color
    escribir_3mf(os.path.join(salida, "bolas_tirisiti_multicolor.3mf"), [
        dict(nombre=TITULOS["busto"], posicion=(CAMA / 2 - 55, CAMA / 2), piezas=objetos["busto"]),
        dict(nombre=TITULOS["cuerpo_entero"], posicion=(CAMA / 2 + 55, CAMA / 2), piezas=objetos["cuerpo_entero"]),
    ])


if __name__ == "__main__":
    main()

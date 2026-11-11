#!/usr/bin/env python3
"""Genera bolas de Navidad planas con el personaje, listas para imprimir en 3D.

Uso: generar.py [carpeta_salida]

Cada bola es un disco con anilla para colgar. El dibujo va en relieve por
escalones, y cada escalón es de un solo color (filamento):

  0,0 a 1,6 mm  base    blanco   filamento 1
  1,6 a 2,2 mm  nivel 1 rojo     filamento 2
  2,2 a 2,8 mm  nivel 2 piel     filamento 3
  2,8 a 3,4 mm  nivel 3 negro    filamento 4
  3,4 a 4,0 mm  nivel 4 azul     filamento 5 (corbata)

Como en cada capa solo hay un color, la impresora cambia de filamento cuatro
veces en toda la impresión y casi no gasta material en purgas.

Salida: STL por color, STL de una pieza y 3MF con cada pieza ya asignada a su
filamento (formato de proyecto de Anycubic Slicer Next / OrcaSlicer).
"""
import math
import os
import sys

import cv2
import shapely
import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFilter
from shapely import affinity
from shapely.geometry import MultiPolygon, Point, Polygon, box
from shapely.ops import unary_union

from clasificar import clasificar
from proyecto_3mf import escribir_3mf

AQUI = os.path.dirname(os.path.abspath(__file__))

DIAMETRO = 80.0      # mm
ARO = 2.5            # ancho del borde en relieve
BASE = 1.6           # grosor de la base blanca
ESCALON = 0.6        # altura de cada color (3 capas de 0,2 mm)
AGUJERO = 4.4        # diámetro del agujero para el hilo
NOMBRES = ["0_base_blanco", "1_rojo", "2_piel", "3_negro", "4_azul"]
PIEZAS = ["Base (blanco)", "Chaqueta, boina y aro (rojo)", "Cara y manos (piel)", "Pelo, ojos y pantalon (negro)", "Corbata (azul)"]
COLORES = [(246, 246, 244), (200, 30, 36), (233, 164, 128), (28, 28, 32), (30, 80, 190)]

VERSIONES = {
    # mm_px: tamaño de cada píxel del dibujo; y_arriba: altura (mm) de la fila 0
    "busto": dict(mm_px=0.34, y_arriba=34.0,
                  estrellas=[(-27, 17, 4.2), (27, 17, 4.2), (-31, 2, 2.6), (31, 2, 2.6)],
                  puntos=[(-22, 27, 1.1), (22, 27, 1.1), (-25, 7, 0.9), (25, 7, 0.9)]),
    "cuerpo_entero": dict(mm_px=0.142, y_arriba=34.0,
                          estrellas=[(-21, 14, 5.0), (21, 14, 5.0), (-25, -6, 3.6), (25, -6, 3.6),
                                     (-17, -22, 3.0), (17, -22, 3.0)],
                          puntos=[(-14, 26, 1.2), (14, 26, 1.2), (-30, 6, 1.0), (30, 6, 1.0),
                                  (-15, -8, 1.0), (15, -8, 1.0), (-27, -18, 1.0), (27, -18, 1.0)]),
}


def estrella(cx, cy, r, puntas=5):
    pts = []
    for i in range(puntas * 2):
        ang = math.pi / 2 + i * math.pi / puntas
        rr = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    return Polygon(pts).buffer(0.25).buffer(-0.1)


def poligonos(geom):
    if geom.is_empty:
        return []
    if isinstance(geom, Polygon):
        return [geom]
    return [g for g in getattr(geom, "geoms", []) if isinstance(g, Polygon)]


def mascara_a_geom(mask, mm_px, x_centro, y_arriba, escala=8):
    """Convierte una máscara de píxeles en polígonos suaves, en milímetros."""
    m = np.pad(mask.astype(np.float32), 2)
    m = cv2.resize(m, None, fx=escala, fy=escala, interpolation=cv2.INTER_CUBIC)
    m = cv2.GaussianBlur(m, (0, 0), escala * 0.8)
    binaria = (m > 0.5).astype(np.uint8)
    contornos, jer = cv2.findContours(binaria, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    if jer is None:
        return Polygon()

    def a_mm(c):
        pts = c[:, 0, :].astype(float) / escala - 2
        return [((x - x_centro) * mm_px, y_arriba - y * mm_px) for x, y in pts]

    polys = []
    for i, c in enumerate(contornos):
        if jer[0][i][3] != -1 or len(c) < 4:
            continue
        huecos, j = [], jer[0][i][2]
        while j != -1:
            if len(contornos[j]) >= 4:
                huecos.append(a_mm(contornos[j]))
            j = jer[0][j][0]
        p = Polygon(a_mm(c), huecos).buffer(0)
        polys.extend(poligonos(p))
    return unary_union(polys).simplify(0.04)


def limpiar(geom, ancho_min, area_min):
    """Quita lo que es demasiado fino o pequeño para una boquilla de 0,4 mm."""
    g = geom.buffer(ancho_min / 2).buffer(-ancho_min / 2)       # cierra rendijas
    g = g.buffer(-ancho_min / 2).buffer(ancho_min / 2)          # quita pelos finos
    res = []
    for p in poligonos(g):
        if p.area < area_min:
            continue
        huecos = [h for h in p.interiors if Polygon(h).area >= area_min]
        res.append(Polygon(p.exterior, huecos))
    return unary_union(res).buffer(0)


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
        partes.append(m)
    malla = trimesh.util.concatenate(partes)
    malla.apply_translation((0, 0, z0))
    return malla


def construir(nombre, cfg, clases):
    r = DIAMETRO / 2
    disco = Point(0, 0).buffer(r, 128)
    interior = Point(0, 0).buffer(r - ARO, 128)
    hueco = Point(0, r + 4.5).buffer(AGUJERO / 2, 48)
    tapa = box(-8.5, r - 3, 8.5, r + 7.5).buffer(2.0, 16)
    silueta = disco.union(tapa).difference(hueco)

    x_centro = 73.0  # columna central del personaje en el dibujo
    fig = []
    for k in (1, 2, 3, 4):
        g = mascara_a_geom(clases >= k, cfg["mm_px"], x_centro, cfg["y_arriba"])
        g = limpiar(g, 0.45 if k < 3 else 0.6, 0.5 if k < 3 else 0.7)
        fig.append(g.intersection(interior.buffer(0.1)))
    # Cierre negro donde el blanco del personaje (cuello de la camisa) toca el fondo blanco
    sil = limpiar(mascara_a_geom(clases >= 0, cfg["mm_px"], x_centro, cfg["y_arriba"]), 0.45, 0.5)
    blanco = sil.difference(fig[0])
    cierre = sil.difference(sil.buffer(-0.7)).intersection(blanco.buffer(0.05))
    cierre = limpiar(cierre, 0.4, 0.3).intersection(interior)
    fig[:3] = [f.union(cierre) for f in fig[:3]]
    for k in (1, 2, 3):
        fig[k] = fig[k].intersection(fig[k - 1])
    fig = [shapely.set_precision(f.buffer(0), 0.002).buffer(0) for f in fig]

    adornos = [estrella(*e) for e in cfg["estrellas"]] + [Point(x, y).buffer(rr, 24) for x, y, rr in cfg["puntos"]]
    adornos = unary_union(adornos).difference(fig[0].buffer(1.2))
    aro = silueta.difference(interior)
    nivel1 = unary_union([aro, fig[0], adornos]).buffer(0)
    return [silueta, nivel1, fig[1], fig[2], fig[3]]


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
    clases = clasificar(os.path.join(AQUI, "personaje.png"))
    objetos = {}
    for nombre, cfg in VERSIONES.items():
        niveles = construir(nombre, cfg, clases)
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

    # Las dos bolas en la misma placa: comparten los cambios de color
    escribir_3mf(os.path.join(salida, "bolas_tirisiti_multicolor.3mf"), [
        dict(nombre=TITULOS["busto"], posicion=(CAMA / 2 - 55, CAMA / 2), piezas=objetos["busto"]),
        dict(nombre=TITULOS["cuerpo_entero"], posicion=(CAMA / 2 + 55, CAMA / 2), piezas=objetos["cuerpo_entero"]),
    ])


if __name__ == "__main__":
    main()

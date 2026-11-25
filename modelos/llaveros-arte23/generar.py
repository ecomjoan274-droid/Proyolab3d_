"""Llaveros Arte23: genera los STL con OpenSCAD, los comprueba, dibuja la vista
frontal de cada uno y prepara una placa 3MF para Anycubic Slicer Next.

    python3 generar.py            # todo
    python3 generar.py --sin-stl  # solo comprobaciones, vistas y 3MF con los STL ya hechos

Necesita OpenSCAD (2021.01 o posterior) en el PATH y:
    pip install trimesh shapely manifold3d pillow numpy
"""
import os
import subprocess
import sys
import tempfile

import numpy as np
import shapely
import trimesh
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from shapely.geometry import Point
from shapely.ops import polygonize, unary_union

AQUI = os.path.dirname(os.path.abspath(__file__))
FUENTES = os.path.join(AQUI, "fuentes")
SALIDA = os.path.join(AQUI, "salida")
sys.path.append(os.path.join(AQUI, "..", "bolas-navidad-personaje"))
sys.path.append(os.path.join(AQUI, "..", "perfiles-anycubic"))
from proyecto_3mf import escribir_3mf  # noqa: E402
from kobra3v2 import ajustes_proyecto  # noqa: E402

BASE, RELIEVE, CAPA = 3.2, 0.6, 0.2
D_AGUJERO, PARED_MIN = 5.0, 2.5
DENSIDAD_PLA = 1.24  # g/cm³

# Huecos del ACE Pro, igual que en los proyectos anteriores: 1 blanco, 2 rojo, 3 negro, 4 azul
COLORES_ACE = ["#FFFFFF", "#C0272D", "#1A1A1A", "#1F3B73"]
FIL_BASE, FIL_RELIEVE = 1, 3     # base blanca y relieve negro: un único cambio, blanco → negro
COLOR_VISTA = {"base": (250, 248, 243), "relieve": (38, 38, 40), "fondo": (226, 229, 233)}

LLAVEROS = [
    dict(clave="pont_sant_jordi", scad="llavero_pont_sant_jordi.scad", nombre="Llavero Pont de Sant Jordi",
         medidas=(55.0, 30.0), agujero=(6.6, 15.0), titulo="Pont de Sant Jordi · ALCOI"),
    dict(clave="escudo_mostra", scad="llavero_escudo.scad", nombre="Llavero escudo MOSTRA",
         medidas=(42.0, 48.0), agujero=(21.0, 42.6), titulo="Escudo personalizable · MOSTRA"),
]

# Ajustes de laminado sobre el perfil 0.20mm Standard @Anycubic Kobra 3 V2 0.4 nozzle
PROCESO = {
    "layer_height": "0.2",
    "initial_layer_print_height": "0.2",   # 16 capas de base exactas: el relieve empieza en la capa 17
    "sparse_infill_density": "100%",       # macizo: aguanta el uso diario y no se dobla
    "sparse_infill_pattern": "zig-zag",
    "top_surface_pattern": "monotonicline",
    "brim_type": "no_brim",
    "enable_support": "0",
    "enable_prime_tower": "1",
    "outer_wall_speed": "80",              # contornos limpios en letras y arcos
    "top_surface_speed": "100",
    "seam_position": "back",
}


def openscad(scad, salida, parte="todo"):
    subprocess.run(["openscad", "-o", salida, "-D", f'PARTE="{parte}"', os.path.join(FUENTES, scad)],
                   check=True, capture_output=True)
    trimesh.load(salida).export(salida)   # OpenSCAD 2021 escribe STL de texto: se guarda en binario


def seccion(m, z):
    """Contorno de la malla a la altura z, como (Multi)Polygon de shapely (con huecos)."""
    import manifold3d
    mf = manifold3d.Manifold(manifold3d.Mesh(vert_properties=np.asarray(m.vertices, np.float32),
                                             tri_verts=np.asarray(m.faces, np.uint32)))
    area = shapely.geometry.Polygon()
    for anillo in mf.slice(z).to_polygons():   # anillos cerrados; par-impar da los huecos
        if len(anillo) >= 3:
            area = area.symmetric_difference(shapely.geometry.Polygon(anillo))
    return area.buffer(0)


def comprobar(m, ll):
    r = []
    ok = True

    def linea(bien, texto):
        nonlocal ok
        ok &= bien
        r.append(f"  [{'OK' if bien else 'FALLO'}] {texto}")

    (x0, y0, z0), (x1, y1, z1) = m.bounds
    ax, ay = ll["medidas"]
    linea(abs(x1 - x0 - ax) < 0.05 and abs(y1 - y0 - ay) < 0.05 and abs(z1 - (BASE + RELIEVE)) < 0.01 and abs(z0) < 1e-6,
          f"Medidas: {x1 - x0:.2f} × {y1 - y0:.2f} × {z1 - z0:.2f} mm (objetivo {ax:g} × {ay:g} × {BASE + RELIEVE:.1f})")

    import manifold3d
    mf = manifold3d.Manifold(manifold3d.Mesh(vert_properties=np.asarray(m.vertices, np.float32),
                                             tri_verts=np.asarray(m.faces, np.uint32)))
    cuerpos = len(m.split(only_watertight=False))
    linea(m.is_watertight and m.is_winding_consistent and m.is_volume and cuerpos == 1
          and str(mf.status()).endswith("NoError"),
          f"Malla cerrada: estanca={m.is_watertight}, normales coherentes={m.is_winding_consistent}, "
          f"volumen válido={m.is_volume}, cuerpos={cuerpos}, manifold3d={str(mf.status()).split('.')[-1]}, "
          f"{len(m.faces)} triángulos")

    c = Point(ll["agujero"])
    libre = all(seccion(m, z).intersection(c.buffer(D_AGUJERO / 2 - 0.01, 64)).area < 1e-6
                for z in np.arange(0.05, BASE + RELIEVE, 0.1))
    linea(libre, f"Orificio Ø{D_AGUJERO:g} mm libre de material en toda la altura (cortes cada 0,1 mm)")
    medio = seccion(m, BASE / 2)
    exterior = shapely.geometry.Polygon(max(shapely.get_parts(medio), key=lambda p: p.area).exterior)
    pared = exterior.exterior.distance(c) - D_AGUJERO / 2
    linea(pared >= PARED_MIN, f"Material alrededor del orificio: {pared:.2f} mm (mínimo {PARED_MIN:g})")

    zs = np.unique(m.vertices[:, 2].round(4))
    arriba = zs[zs > BASE + 1e-3]
    linea(list(arriba) == [round(BASE + RELIEVE, 4)],
          f"Relieve: todo empieza en z = {BASE:.1f} mm y acaba en {BASE + RELIEVE:.1f} mm "
          f"(cambio de color al empezar la capa {round(BASE / CAPA) + 1})")
    rel = seccion(m, BASE + RELIEVE / 2)
    rel_bajo = seccion(m, BASE + 0.05)
    linea(abs(rel.area - rel_bajo.area) < 0.01, f"Relieve de paredes verticales: {rel.area:.1f} mm² de superficie en relieve")
    abierto = rel.buffer(-0.4, join_style="mitre").buffer(0.4, join_style="mitre")
    fino = [p for p in shapely.get_parts(rel.difference(abierto.buffer(0.05))) if p.area > 0.15]
    linea(not fino, f"Trazos del relieve de al menos 0,8 mm (2 líneas de 0,4): "
          f"{'sin zonas finas' if not fino else str(len(fino)) + ' zonas finas'}")
    # Huecos de menos de 0,6 mm: si separan dos piezas distintas del relieve (letras que se
    # tocarían) es un fallo; si son la muesca de un ángulo agudo dentro de una misma letra
    # (la M, la A) solo se rellena esa punta y la letra se sigue leyendo.
    hueco = rel.buffer(0.3).buffer(-0.3).difference(rel)
    piezas = list(shapely.get_parts(rel))
    union_, muesca = [], []
    for p in shapely.get_parts(hueco):
        if p.area <= 0.15:
            continue
        tocan = sum(1 for q in piezas if q.distance(p) < 1e-3)
        (union_ if tocan > 1 else muesca).append(p)
    linea(not union_, f"Separación entre piezas del relieve de al menos 0,6 mm: "
          f"{'ninguna pieza se junta con otra' if not union_ else str(len(union_)) + ' sitios donde se juntan'}")
    if muesca:
        r.append(f"  [INFO] {len(muesca)} muescas de ángulo agudo dentro de una misma letra de menos de 0,6 mm "
                 "(la punta se rellena; no afecta a la lectura)")

    n = m.face_normals
    cz = m.triangles_center[:, 2]
    colgado = (n[:, 2] < -0.75) & (cz > 0.01) & (m.area_faces > 1e-4)  # ignora triángulos degenerados
    linea(not colgado.any(), "Sin voladizos de más de 45° ni techos sueltos: se imprime plano sin soportes "
          f"({int(colgado.sum())} caras colgadas)")

    vol = m.volume / 1000
    r.append(f"  [INFO] Volumen {vol:.2f} cm³ → {vol * DENSIDAD_PLA:.1f} g de PLA con relleno al 100 % "
             f"(sin purga ni torre); base {(vol - rel.area * RELIEVE / 1000) * DENSIDAD_PLA:.1f} g, "
             f"relieve {rel.area * RELIEVE / 1000 * DENSIDAD_PLA:.2f} g")
    return ok, r, dict(rel=rel, medio=medio, arriba=seccion(m, BASE - 0.01), volumen=vol)


def vista(m, ll, info, ruta, px=24):
    """Vista frontal (desde arriba, como se ve el llavero) a escala, con cotas."""
    (x0, y0, _), (x1, y1, _) = m.bounds
    margen, cab, pie = 6.0, 9.0, 9.0
    W = int((x1 - x0 + 2 * margen + 6) * px)
    H = int((y1 - y0 + 2 * margen + cab + pie) * px)
    ss = 3
    img = Image.new("RGB", (W * ss, H * ss), COLOR_VISTA["fondo"])

    def xy(p):
        return [((x - x0 + margen) * px * ss, (y1 - y + margen + cab) * px * ss) for x, y in p]

    def mascara(geom, dx=0.0, dy=0.0):
        """Máscara de una geometría con sus huecos (par-impar sobre todos los anillos)."""
        mk = Image.new("1", img.size, 0)
        for p in shapely.get_parts(shapely.affinity.translate(geom, dx, dy)):
            capa = Image.new("1", img.size, 0)
            dc = ImageDraw.Draw(capa)
            dc.polygon(xy(p.exterior.coords), fill=1)
            for h in p.interiors:
                dc.polygon(xy(h.coords), fill=0)
            mk.paste(1, mask=capa)
        return mk

    def pintar(geom, color, dx=0.0, dy=0.0):
        img.paste(color, mask=mascara(geom, dx, dy))

    # sombra de la pieza sobre la mesa
    sombra = mascara(info["medio"], 0.5, -0.6).convert("L").point(lambda v: 90 if v else 0)
    sombra = sombra.filter(ImageFilter.GaussianBlur(px * ss * 0.5))
    img.paste((0, 0, 0), mask=sombra)

    cb = COLOR_VISTA["base"]
    canto = tuple(int(v * 0.86) for v in cb)
    pintar(info["medio"], canto)                                  # canto redondeado
    pintar(info["arriba"], cb)                                    # cara superior plana
    pintar(shapely.affinity.translate(info["rel"], 0.18, -0.22).difference(info["rel"]),
           tuple(int(v * 0.72) for v in cb))                      # sombra corta del relieve
    pintar(info["rel"], COLOR_VISTA["relieve"])
    # el orificio se ve a través, con el chaflán de la boca
    c = Point(ll["agujero"])
    pintar(c.buffer(D_AGUJERO / 2 + 0.4, 64), canto)
    pintar(c.buffer(D_AGUJERO / 2, 64), COLOR_VISTA["fondo"])

    img = img.resize((W, H), Image.LANCZOS)
    d = ImageDraw.Draw(img)
    try:
        f_tit = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", int(px * 2.4))
        f_txt = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", int(px * 1.7))
    except OSError:
        f_tit = f_txt = ImageFont.load_default()
    gris = (90, 90, 90)
    d.text((margen * px, 2.0 * px), ll["titulo"], font=f_tit, fill=(30, 30, 30))
    # cotas
    def X(x): return (x - x0 + margen) * px
    def Y(y): return (y1 - y + margen + cab) * px
    yc = Y(y0) + 3.5 * px
    d.line([X(x0), yc, X(x1), yc], fill=gris, width=2)
    for x in (x0, x1):
        d.line([X(x), yc - 0.8 * px, X(x), yc + 0.8 * px], fill=gris, width=2)
    t = f"{x1 - x0:.1f} mm".replace(".", ",")
    d.text(((X(x0) + X(x1)) / 2, yc + 0.6 * px), t, font=f_txt, fill=gris, anchor="mt")
    xc = X(x1) + 3.0 * px
    d.line([xc, Y(y0), xc, Y(y1)], fill=gris, width=2)
    for y in (y0, y1):
        d.line([xc - 0.8 * px, Y(y), xc + 0.8 * px, Y(y)], fill=gris, width=2)
    t = f"{y1 - y0:.1f}".replace(".", ",")
    d.text((xc + 0.6 * px, (Y(y0) + Y(y1)) / 2), t, font=f_txt, fill=gris, anchor="lm")
    d.text((margen * px, H - 5.6 * px), f"Base {BASE:.1f} mm blanca + relieve {RELIEVE:.1f} mm negro".replace(".", ","),
           font=f_txt, fill=gris)
    d.text((margen * px, H - 3.2 * px), f"Orificio Ø5 mm · grosor total {BASE + RELIEVE:.1f} mm".replace(".", ","),
           font=f_txt, fill=gris)
    img.save(ruta)


def main():
    os.makedirs(SALIDA, exist_ok=True)
    hacer_stl = "--sin-stl" not in sys.argv
    informe = ["Comprobaciones de los llaveros Arte23 (generado por generar.py)", ""]
    objetos = []
    todo_ok = True
    with tempfile.TemporaryDirectory() as tmp:
        for i, ll in enumerate(LLAVEROS):
            stl = os.path.join(SALIDA, f"llavero_{ll['clave']}.stl")
            if hacer_stl:
                print("OpenSCAD:", ll["scad"])
                openscad(ll["scad"], stl)
            m = trimesh.load(stl)
            ok, lineas, info = comprobar(m, ll)
            todo_ok &= ok
            informe += [f"{ll['nombre']} — {os.path.basename(stl)}"] + lineas + [""]
            print("\n".join(informe[-len(lineas) - 2:]))
            vista(m, ll, info, os.path.join(SALIDA, f"vista_{ll['clave']}.png"))
            # partes para la placa: base (filamento 1) y relieve (filamento 3)
            partes = []
            for parte, fil in (("base", FIL_BASE), ("relieve", FIL_RELIEVE)):
                ruta = os.path.join(tmp, f"{ll['clave']}_{parte}.stl")
                openscad(ll["scad"], ruta, parte)
                partes.append((parte, trimesh.load(ruta), fil))
            (bx0, by0, _), (bx1, by1, _) = m.bounds
            cx, cy = (bx0 + bx1) / 2, (by0 + by1) / 2
            partes = [(n, p.copy().apply_translation((-cx, -cy, 0)), f) for n, p, f in partes]
            objetos.append(dict(nombre=ll["nombre"], posicion=(127.5 + (-30 if i == 0 else 22), 127.5),
                                piezas=partes))
    escribir_3mf(os.path.join(SALIDA, "placa_llaveros_arte23.3mf"), objetos,
                 ajustes=ajustes_proyecto(COLORES_ACE, PROCESO, torre=(150.0, 165.0)))
    informe.append("Placa: placa_llaveros_arte23.3mf (los dos llaveros, base en el filamento 1 y relieve en el 3).")
    informe.append("Resultado: " + ("todas las comprobaciones geométricas correctas." if todo_ok else "HAY FALLOS."))
    with open(os.path.join(SALIDA, "comprobaciones.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(informe) + "\n")
    print(informe[-1])
    return 0 if todo_ok else 1


if __name__ == "__main__":
    sys.exit(main())

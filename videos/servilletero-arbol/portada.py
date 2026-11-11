#!/usr/bin/env python3
"""Genera las portadas (miniaturas) del Reel del servilletero árbol de Navidad.

Uso: portada.py foto.jpg carpeta_salida
Crea:
  portada_9x16.jpg  1080x1920  TikTok, Instagram Reels y Facebook Reels
  portada_4x5.jpg   1080x1350  publicación normal de Instagram / Facebook
Todo el texto queda dentro de la zona central, que es la que se ve en la
cuadrícula del perfil de TikTok e Instagram.
"""
import sys

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

FONT = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
W, H = 1080, 1920
OSCURO = (4, 44, 38)
MENTA = (64, 232, 200)
ROJO = (226, 48, 62)
BLANCO = (255, 255, 255)

# Recorte de la foto (fracciones del ancho/alto) para que el servilletero llene la portada
RECORTE = (0.071, 0.015, 0.801, 0.745)  # izquierda, arriba, derecha, abajo


def fuente_que_quepa(texto, ancho, maximo):
    size = maximo
    while size > 20:
        f = ImageFont.truetype(FONT, size)
        if f.getlength(texto) <= ancho:
            return f
        size -= 2
    return ImageFont.truetype(FONT, size)


def degradado(alto, alfa_ini, alfa_fin, color):
    capa = Image.new("RGBA", (W, alto), color + (0,))
    px = capa.load()
    for y in range(alto):
        t = y / max(1, alto - 1)
        a = int(255 * (alfa_ini + (alfa_fin - alfa_ini) * t ** 1.4))
        for x in range(W):
            px[x, y] = color + (a,)
    return capa


def texto_centrado(d, y, texto, fuente, color, borde=8):
    w = fuente.getlength(texto)
    d.text(((W - w) / 2, y), texto, font=fuente, fill=color,
           stroke_width=borde, stroke_fill=OSCURO)


def main():
    foto, salida = sys.argv[1], sys.argv[2]
    img = ImageOps.exif_transpose(Image.open(foto)).convert("RGB")
    iw, ih = img.size
    l, t, r, b = RECORTE
    img = img.crop((int(l * iw), int(t * ih), int(r * iw), int(b * ih)))
    img = ImageOps.fit(img, (W, H), Image.LANCZOS, centering=(0.5, 0.5))
    img = ImageEnhance.Color(img).enhance(1.22)
    img = ImageEnhance.Contrast(img).enhance(1.08)
    img = ImageEnhance.Brightness(img).enhance(1.06)

    # Fondo de arriba desenfocado para que el título se lea y la cocina no distraiga
    borroso = img.filter(ImageFilter.GaussianBlur(14))
    mascara = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mascara).rectangle((0, 0, W, 640), fill=255)
    mascara = mascara.filter(ImageFilter.GaussianBlur(60))
    img = Image.composite(borroso, img, mascara).convert("RGBA")

    img.alpha_composite(degradado(900, 0.97, 0.0, OSCURO), (0, 0))
    abajo = degradado(640, 0.0, 0.95, OSCURO)
    img.alpha_composite(abajo, (0, H - 640))

    d = ImageDraw.Draw(img)

    # Etiqueta roja
    f_et = ImageFont.truetype(FONT, 50)
    et = "IMPRESO EN 3D"
    ew = f_et.getlength(et)
    ex, ey = (W - ew) / 2 - 38, 338
    d.rounded_rectangle((ex, ey, ex + ew + 76, ey + 88), radius=44, fill=ROJO)
    d.text((ex + 38, ey + 14), et, font=f_et, fill=BLANCO)

    # Título
    f1 = fuente_que_quepa("SERVILLETERO", 960, 150)
    texto_centrado(d, 452, "SERVILLETERO", f1, BLANCO)
    f2 = fuente_que_quepa("ÁRBOL DE NAVIDAD", 960, 120)
    texto_centrado(d, 452 + f1.size + 14, "ÁRBOL DE NAVIDAD", f2, MENTA)

    # Marca
    f3 = ImageFont.truetype(FONT, 92)
    texto_centrado(d, 1452, "PROTOLAB3D", f3, BLANCO, borde=6)
    f4 = ImageFont.truetype(FONT, 40)
    texto_centrado(d, 1562, "Hecho con Anycubic Kobra 3", f4, MENTA, borde=4)

    final = img.convert("RGB")
    final.save(f"{salida}/portada_9x16.jpg", quality=92, optimize=True)
    final.crop((0, 285, W, 285 + 1350)).save(f"{salida}/portada_4x5.jpg", quality=92, optimize=True)
    print(f"{salida}/portada_9x16.jpg\n{salida}/portada_4x5.jpg")


if __name__ == "__main__":
    main()

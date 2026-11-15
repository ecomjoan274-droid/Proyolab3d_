#!/usr/bin/env python3
"""Portada 9:16 del Reel "¿Eres de Alcoi?" con el mismo estilo que la primera portada de Tirisiti.

Uso: portada.py foto.jpg salida.jpg [fuente.ttf]
La fuente por defecto es Anton (Google Fonts, licencia OFL).
"""
import sys
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

W, H = 1080, 1920
BLANCO, ROJO = (255, 255, 255), (255, 59, 48)
LINEAS = [("¿ERES DE ALCOI?", BLANCO), ("ESTO ES PARA TI", ROJO)]


def cubrir(img):
    """Escala y recorta la foto para llenar 1080x1920."""
    r = max(W / img.width, H / img.height)
    img = img.resize((round(img.width * r), round(img.height * r)), Image.LANCZOS)
    x, y = (img.width - W) // 2, (img.height - H) // 2
    return img.crop((x, y, x + W, y + H))


def degradado(base, y0, y1, alfa_max, hacia_abajo=True):
    capa = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(capa)
    for y in range(y0, y1):
        t = (y - y0) / max(1, y1 - y0)
        a = t if hacia_abajo else 1 - t
        d.line([(0, y), (W, y)], fill=int(alfa_max * min(1, a * 1.4)))
    negro = Image.new("RGB", (W, H), (0, 0, 0))
    return Image.composite(negro, base, capa)


def main():
    foto, salida = sys.argv[1], sys.argv[2]
    fuente = sys.argv[3] if len(sys.argv) > 3 else "Anton-Regular.ttf"
    img = cubrir(Image.open(foto).convert("RGB"))
    img = ImageEnhance.Contrast(img).enhance(1.06)
    img = ImageEnhance.Color(img).enhance(1.12)
    img = degradado(img, 1080, H, 245)            # fondo oscuro para el texto de abajo
    img = degradado(img, 0, 330, 170, hacia_abajo=False)  # sombra suave para la marca de arriba
    d = ImageDraw.Draw(img)

    marca = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", 46)
    texto = "PROTOLAB"
    esp = 22
    anchos = [d.textlength(c, font=marca) for c in texto]
    x = (W - (sum(anchos) + esp * (len(texto) - 1))) / 2
    for c, a in zip(texto, anchos):
        d.text((x, 150), c, font=marca, fill=BLANCO)
        x += a + esp

    # Las dos líneas con el mismo tamaño, el mayor que cabe en 960 px de ancho
    size = 260
    while True:
        f = ImageFont.truetype(fuente, size)
        if max(d.textlength(t, font=f) for t, _ in LINEAS) <= 960:
            break
        size -= 4
    alto = f.getbbox("ÁG")[3] - f.getbbox("ÁG")[1]
    y = H - 140 - 2 * alto - 40
    for t, color in LINEAS:
        sombra = Image.new("L", (W, H), 0)
        ImageDraw.Draw(sombra).text(((W - d.textlength(t, font=f)) / 2, y + 6), t, font=f, fill=150)
        img.paste((0, 0, 0), mask=sombra.filter(ImageFilter.GaussianBlur(8)))
        d = ImageDraw.Draw(img)
        d.text(((W - d.textlength(t, font=f)) / 2, y), t, font=f, fill=color)
        y += alto + 40
    img.save(salida, quality=92)
    print(salida, size)


if __name__ == "__main__":
    main()

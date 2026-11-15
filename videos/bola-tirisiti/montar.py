#!/usr/bin/env python3
"""Monta el Reel de la bola de Navidad de Tirisiti (1080x1920, 30 fps) con la voz.

Uso: montar.py [salida.mp4]
Espera en $PROTOLAB_WORKDIR:
  media/  clips de Drive (20261112_*.mp4, 20261113_*.mp4) y foto_bola.jpg (foto de la bola en la mano)
  voz/    a1.ogg ... a5.ogg (notas de voz en orden)
  build/  temporales
"""
import json
import os
import re
import subprocess
import sys

S = os.environ.get(
    "PROTOLAB_WORKDIR",
    "/tmp/claude-0/-home-user-Proyolab3d-/f91bc3a6-35d2-5c48-817d-3278018c574d/scratchpad/tirisiti",
)
M, V, B = f"{S}/media", f"{S}/voz", f"{S}/build"
FONT = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
W, H, FPS = 1080, 1920, 30

# Planos: (fuente, inicio en el clip, duración en el vídeo, velocidad, texto en pantalla)
SEG = [
    ("20261113_063745.mp4", 2.6, 2.8, 1.0, "El Tirisiti\nen tu árbol de Navidad"),
    ("20261112_214651.mp4", 2.2, 2.5, 1.0, "Impresa en 3D\ncon mi Anycubic Kobra 3"),
    ("20261112_233212.mp4", 0.5, 2.7, 3.0, "Capa a capa\na 4 colores"),
    ("20261112_233212.mp4", 17.0, 2.6, 1.0, "Sin pintar nada"),
    ("20261113_063822.mp4", 5.5, 3.0, 2.0, "Recién salidas\nde la impresora"),
    ("foto_bola.jpg", 0, 3.6, 1.0, "¿Quieres la tuya?\nEscríbeme por mensaje"),
]

# Voz: (archivo, inicio de la voz en la nota, fin de la voz, segundo del vídeo donde entra)
VOZ = [
    ("a1.ogg", 0.50, 2.85, 0.30),
    ("a2.ogg", 0.20, 2.75, 3.00),
    ("a3.ogg", 0.45, 2.45, 5.80),
    ("a4.ogg", 0.10, 2.45, 8.60),
    ("a5.ogg", 0.30, 2.70, 13.80),
]
OBJETIVO_LUFS = -14.0  # volumen estándar de Reels / TikTok


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)


def txtfilter(i, text, y):
    p = f"{B}/t{i}.txt"
    with open(p, "w") as f:
        f.write(text)
    return (
        f"drawtext=fontfile={FONT}:textfile={p}:fontsize=74:fontcolor=white:"
        f"line_spacing=14:text_align=C:x=(w-text_w)/2:y={y}:borderw=6:bordercolor=black@0.85:"
        f"shadowcolor=black@0.5:shadowx=0:shadowy=6:alpha='min(1,t/0.25)'"
    )


def render(i, src, ss, dur, speed, text):
    out = f"{B}/seg{i}.mp4"
    n = int(round(dur * FPS))
    look = "eq=brightness=0.03:contrast=1.06:saturation=1.15"
    if src.endswith(".jpg"):
        vf = (
            f"scale={W*2}:{H*2}:force_original_aspect_ratio=increase,crop={W*2}:{H*2},"
            f"zoompan=z='1+0.0009*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s={W}x{H}:fps={FPS},"
            f"{look},{txtfilter(i, text, 250)}"
        )
        cmd = ["ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", f"{M}/{src}", "-t", str(dur)]
    else:
        vf = (
            f"setpts=PTS/{speed},fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
            f"{look},{txtfilter(i, text, 250)}"
        )
        cmd = ["ffmpeg", "-y", "-v", "error", "-ss", str(ss), "-t", str(dur * speed + 0.2), "-i", f"{M}/{src}"]
    if i == 0:
        vf += ",fade=t=in:st=0:d=0.3"
    if i == len(SEG) - 1:
        vf += (
            f",drawtext=fontfile={FONT}:text='PROTOLAB3D':fontsize=96:fontcolor=white:x=(w-text_w)/2:y=h-420:"
            f"borderw=6:bordercolor=0x0b6e5f:alpha='min(1,max(0,(t-0.5)/0.4))',"
            f"fade=t=out:st={dur-0.6}:d=0.6"
        )
    cmd += ["-vf", vf, "-an", "-frames:v", str(n), "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-pix_fmt", "yuv420p", "-r", str(FPS), out]
    run(cmd)
    return out


def volumen_medio(path):
    r = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "volumedetect", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    return float(re.search(r"mean_volume: (-?[\d.]+) dB", r.stderr).group(1))


def pista_voz(total):
    """Limpia cada nota, las iguala de volumen y las coloca en su segundo."""
    limpias = []
    for i, (f, ini, fin, _) in enumerate(VOZ):
        tmp = f"{B}/voz{i}_raw.wav"
        run(["ffmpeg", "-y", "-v", "error", "-i", f"{V}/{f}", "-af",
             f"atrim={ini}:{fin},asetpts=PTS-STARTPTS,highpass=f=90,afftdn=nf=-28,"
             f"acompressor=threshold=-20dB:ratio=3:attack=5:release=120",
             "-ar", "48000", "-ac", "1", tmp])
        gan = -18.0 - volumen_medio(tmp)
        d = fin - ini
        out = f"{B}/voz{i}.wav"
        run(["ffmpeg", "-y", "-v", "error", "-i", tmp, "-af",
             f"volume={gan:.2f}dB,afade=t=in:st=0:d=0.02,afade=t=out:st={d-0.06:.2f}:d=0.06", out])
        limpias.append(out)

    cmd = ["ffmpeg", "-y", "-v", "error"]
    for p in limpias:
        cmd += ["-i", p]
    fc = "".join(f"[{i}:a]adelay={int(t*1000)}:all=1[a{i}];" for i, (_, _, _, t) in enumerate(VOZ))
    fc += "".join(f"[a{i}]" for i in range(len(VOZ)))
    fc += f"amix=inputs={len(VOZ)}:normalize=0,apad=whole_dur={total}[m]"
    mezcla = f"{B}/voz_mezcla.wav"
    run(cmd + ["-filter_complex", fc, "-map", "[m]", "-t", str(total), mezcla])

    r = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", mezcla, "-af",
         "loudnorm=I=-14:TP=-1.5:print_format=json", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    medido = float(json.loads(r.stderr[r.stderr.rindex("{"):])["input_i"])
    final = f"{B}/voz_final.wav"
    run(["ffmpeg", "-y", "-v", "error", "-i", mezcla, "-af",
         f"volume={OBJETIVO_LUFS - medido:.2f}dB,alimiter=limit=0.84:level=false", final])
    return final


def main():
    salida = sys.argv[1] if len(sys.argv) > 1 else f"{S}/reel_bola_tirisiti.mp4"
    os.makedirs(B, exist_ok=True)
    segs = [render(i, *s) for i, s in enumerate(SEG)]
    total = round(sum(s[2] for s in SEG), 2)
    lst = f"{B}/list.txt"
    with open(lst, "w") as f:
        f.write("".join(f"file '{p}'\n" for p in segs))
    voz = pista_voz(total)
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-i", voz,
         "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-t", str(total), "-movflags", "+faststart", salida])
    print(salida)


if __name__ == "__main__":
    main()

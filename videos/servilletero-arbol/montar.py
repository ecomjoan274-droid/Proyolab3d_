#!/usr/bin/env python3
"""Monta el Reel del servilletero árbol de Navidad (1080x1920, 30 fps) con la voz.

Uso: montar.py [salida.mp4]
Espera en $PROTOLAB_WORKDIR:
  media/  clips y fotos originales de Drive
  voz/    a1.ogg ... a5.ogg (notas de voz, una por bloque del guion)
  build/  temporales
"""
import json
import os
import re
import subprocess
import sys

S = os.environ.get(
    "PROTOLAB_WORKDIR",
    "/tmp/claude-0/-home-user-Proyolab3d-/498bf61e-7e99-569b-a322-03be1765cae5/scratchpad",
)
M, V, B = f"{S}/media", f"{S}/voz", f"{S}/build"
FONT = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
W, H, FPS = 1080, 1920, 30

# Planos: (fuente, inicio en el clip, duración en el vídeo, velocidad, texto en pantalla)
SEG = [
    ("20261109_063808.mp4", 18.4, 2.9, 1.0, "¿A tu mesa de Navidad\nle falta esto?"),
    ("20261108_222257.mp4", 7.0, 2.4, 1.0, "Impreso en 3D\ncon mi Anycubic Kobra 3"),
    ("20261108_222257.mp4", 40.0, 2.3, 2.0, "Capa a capa\ntoda la noche"),
    ("20261109_063411.mp4", 2.0, 1.9, 1.0, "Recién salido\nde la impresora"),
    ("20261109_063354.mp4", 6.2, 2.5, 1.0, "3 piezas:\ndos árboles y una base"),
    ("20261109_063449.mp4", 3.2, 3.6, 1.0, "Doblas la placa\ny salen solas"),
    ("20261109_063808.mp4", 1.8, 5.2, 1.0, "Decorativo\ny práctico"),
    ("foto_servilletero2.jpg", 0, 3.8, 1.0, "¿Quieres uno?\nEscríbeme por mensaje"),
]

# Voz: (archivo, inicio de la voz en la nota, fin de la voz, segundo del vídeo donde entra)
VOZ = [
    ("a1.ogg", 0.00, 2.12, 0.35),   # gancho
    ("a2.ogg", 0.20, 3.86, 3.10),   # impresión
    ("a3.ogg", 0.34, 3.70, 7.85),   # recién salido, 3 piezas
    ("a4.ogg", 0.00, 2.20, 12.50),  # doblas la placa
    ("a5.ogg", 0.65, 4.93, 16.00),  # en uso
]
OBJETIVO_LUFS = -14.0  # volumen estándar de Reels / TikTok


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)


def txtfilter(i, text):
    p = f"{B}/t{i}.txt"
    with open(p, "w") as f:
        f.write(text)
    return (
        f"drawtext=fontfile={FONT}:textfile={p}:fontsize=74:fontcolor=white:"
        f"line_spacing=14:text_align=C:x=(w-text_w)/2:y=330:borderw=6:bordercolor=black@0.85:"
        f"shadowcolor=black@0.5:shadowx=0:shadowy=6:alpha='min(1,t/0.25)'"
    )


def render(i, src, ss, dur, speed, text):
    out = f"{B}/seg{i}.mp4"
    look = "eq=brightness=0.03:contrast=1.06:saturation=1.15"
    if src.endswith(".jpg"):
        n = int(dur * FPS)
        vf = (
            f"scale={W*2}:{H*2}:force_original_aspect_ratio=increase,crop={W*2}:{H*2},"
            f"zoompan=z='1+0.0009*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s={W}x{H}:fps={FPS},"
            f"{look},{txtfilter(i, text)},"
            f"drawtext=fontfile={FONT}:text='PROTOLAB3D':fontsize=96:fontcolor=white:x=(w-text_w)/2:y=h-560:"
            f"borderw=6:bordercolor=0x0b6e5f:alpha='min(1,max(0,(t-0.5)/0.4))',"
            f"fade=t=out:st={dur-0.6}:d=0.6"
        )
        cmd = ["ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", f"{M}/{src}", "-t", str(dur), "-vf", vf]
    else:
        vf = (
            f"setpts=PTS/{speed},fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
            f"{look},{txtfilter(i, text)}"
        )
        if i == 0:
            vf += ",fade=t=in:st=0:d=0.3"
        cmd = ["ffmpeg", "-y", "-v", "error", "-ss", str(ss), "-t", str(dur * speed), "-i", f"{M}/{src}", "-vf", vf]
    cmd += ["-an", "-t", str(dur), "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", out]
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
    salida = sys.argv[1] if len(sys.argv) > 1 else f"{S}/servilletero_arbol_final.mp4"
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

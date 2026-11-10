#!/usr/bin/env python3
"""Monta el Reel del servilletero árbol de Navidad (1080x1920, 30 fps).
Uso: montar.py [audio_voz] [salida.mp4]"""
import subprocess, sys, os, json
S = os.environ.get("PROTOLAB_WORKDIR", "/tmp/claude-0/-home-user-Proyolab3d-/498bf61e-7e99-569b-a322-03be1765cae5/scratchpad")  # carpeta con media/ y build/
M, B = f"{S}/media", f"{S}/build"
FONT = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
W, H, FPS = 1080, 1920, 30

# (fuente, inicio, duración_salida, velocidad, texto)
SEG = [
    ("20261109_063808.mp4", 18.4, 3.4, 1.0, "¿A tu mesa de Navidad\nle falta esto?"),
    ("20261108_222257.mp4", 7.0,  4.5, 1.0, "Impreso en 3D\ncon mi Anycubic Kobra 3"),
    ("20261108_222257.mp4", 40.0, 4.0, 2.0, "Capa a capa\ntoda la noche"),
    ("20261109_063411.mp4", 2.0,  3.0, 1.0, "Recién salido\nde la impresora"),
    ("20261109_063354.mp4", 6.2,  4.5, 1.0, "3 piezas:\ndos árboles y una base"),
    ("20261109_063449.mp4", 2.8,  5.0, 1.0, "Doblas la placa\ny salen solas"),
    ("20261109_063808.mp4", 1.8,  7.2, 1.0, "Decorativo\ny práctico"),
    ("foto_servilletero2.jpg", 0, 4.4, 1.0, "¿Quieres uno?\nEscríbeme por mensaje"),
]

def txtfilter(i, text):
    p = f"{B}/t{i}.txt"; open(p, "w").write(text)
    return (f"drawtext=fontfile={FONT}:textfile={p}:fontsize=74:fontcolor=white:"
            f"line_spacing=14:text_align=C:x=(w-text_w)/2:y=330:borderw=6:bordercolor=black@0.85:"
            f"shadowcolor=black@0.5:shadowx=0:shadowy=6:alpha='min(1,t/0.25)'")

def render(i, src, ss, dur, speed, text):
    out = f"{B}/seg{i}.mp4"
    look = "eq=brightness=0.03:contrast=1.06:saturation=1.15"
    if src.endswith(".jpg"):
        n = int(dur * FPS)
        vf = (f"scale={W*2}:{H*2}:force_original_aspect_ratio=increase,crop={W*2}:{H*2},"
              f"zoompan=z='1+0.0009*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s={W}x{H}:fps={FPS},"
              f"{look},{txtfilter(i, text)},"
              f"drawtext=fontfile={FONT}:text='PROTOLAB3D':fontsize=96:fontcolor=white:x=(w-text_w)/2:y=h-560:"
              f"borderw=6:bordercolor=0x0b6e5f:alpha='min(1,max(0,(t-0.6)/0.4))',"
              f"fade=t=out:st={dur-0.6}:d=0.6")
        cmd = ["ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", f"{M}/{src}", "-t", str(dur), "-vf", vf]
    else:
        vf = (f"setpts=PTS/{speed},fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
              f"{look},{txtfilter(i, text)}")
        if i == 0: vf += ",fade=t=in:st=0:d=0.3"
        cmd = ["ffmpeg", "-y", "-v", "error", "-ss", str(ss), "-t", str(dur * speed), "-i", f"{M}/{src}", "-vf", vf]
    cmd += ["-an", "-t", str(dur), "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", out]
    subprocess.run(cmd, check=True)
    return out

def main():
    voz = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] != "-" else None
    salida = sys.argv[2] if len(sys.argv) > 2 else f"{S}/servilletero_arbol_borrador.mp4"
    segs = [render(i, *s) for i, s in enumerate(SEG)]
    lst = f"{B}/list.txt"; open(lst, "w").write("".join(f"file '{p}'\n" for p in segs))
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst]
    if voz:
        cmd += ["-i", voz, "-map", "0:v", "-map", "1:a", "-af", "loudnorm=I=-14:TP=-1.5,afade=t=out:st=35:d=1",
                "-c:a", "aac", "-b:a", "192k", "-shortest"]
    cmd += ["-c:v", "copy", "-movflags", "+faststart", salida]
    subprocess.run(cmd, check=True)
    print(salida)

if __name__ == "__main__":
    main()

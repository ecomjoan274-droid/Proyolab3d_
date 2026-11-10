# Reel: Servilletero Árbol de Navidad

- `montar.py`: monta el Reel vertical (1080x1920, 30 fps, 36 s) a partir de los clips de Drive ("Protolab3D Contenido/00_Subir aqui").
  - Espera los clips originales en `$PROTOLAB_WORKDIR/media/` y escribe los temporales en `$PROTOLAB_WORKDIR/build/`.
  - Sin argumentos genera el borrador sin voz: `python3 montar.py`
  - Con voz: `python3 montar.py voz.m4a salida.mp4` (normaliza el volumen a -14 LUFS, el estándar de Reels/TikTok).
- La lista `SEG` define cada plano: clip, segundo de inicio, duración, velocidad y texto en pantalla.
- El guion v2 está en Drive, en "01_Guiones para grabar".

# Reel: Bola de Navidad de Tirisiti

Carpeta de trabajo (`$PROTOLAB_WORKDIR`): `media/` con los clips de Drive (`20261112_214651.mp4`, `20261112_233212.mp4`, `20261113_063745.mp4`, `20261113_063822.mp4`) y `foto_bola.jpg` (foto de la bola en la mano), `voz/` con las notas de voz `a1.ogg` a `a8.ogg` en orden y `build/` para temporales.

- `montar.py`: monta el Reel vertical (1080x1920, 30 fps, 25 s) con la voz.
  - `python3 montar.py [salida.mp4]`
  - `SEG` define cada plano: clip, segundo de inicio, duración, velocidad y texto en pantalla.
  - `VOZ` define cada nota de voz: tramo que se usa y segundo del vídeo donde entra. El volumen se ajusta a -14 LUFS.

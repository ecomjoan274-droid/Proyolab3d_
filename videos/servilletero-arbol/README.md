# Reel: Servilletero Árbol de Navidad

Carpeta de trabajo (`$PROTOLAB_WORKDIR`): `media/` con los clips y fotos de Drive ("Protolab3D Contenido/00_Subir aqui"), `voz/` con las notas de voz `a1.ogg` a `a5.ogg` y `build/` para temporales.

- `montar.py`: monta el Reel vertical (1080x1920, 30 fps, 24,6 s) con la voz.
  - `python3 montar.py [salida.mp4]`
  - `SEG` define cada plano: clip, segundo de inicio, duración, velocidad y texto en pantalla.
  - `VOZ` define cada nota de voz: tramo que se usa y segundo del vídeo donde entra. El volumen se ajusta a -14 LUFS.
- `portada.py`: genera las miniaturas a partir de una foto del producto.
  - `python3 portada.py foto.jpg carpeta_salida` crea `portada_9x16.jpg` (TikTok y Reels) y `portada_4x5.jpg` (publicación normal).
- `descripcion.md`: texto y hashtags para publicar.

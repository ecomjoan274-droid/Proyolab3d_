# Reel: Bola de Navidad de Tirisiti

Carpeta de trabajo (`$PROTOLAB_WORKDIR`): `media/` con `foto_bola.jpg` (foto de la bola impresa) y `bola_busto_vista.png` (render de `modelos/bolas-navidad-personaje/salida/`), `voz/` con las notas de voz `a1.ogg` a `a5.ogg` en orden y `build/` para temporales.

- `montar.py`: monta el Reel vertical (1080x1920, 30 fps, 15,6 s) con la voz.
  - `python3 montar.py [salida.mp4]`
  - `SEG` define cada plano: imagen, duración, zoom inicial y final, centro del encuadre y texto en pantalla.
  - `VOZ` define cada nota de voz: tramo que se usa y segundo del vídeo donde entra. El volumen se ajusta a -14 LUFS.

# Llaveros para Arte23 (copiados de las fotos)

Dos llaveros copiados de las fotos de `referencias/`, enderezadas para quitar la perspectiva.
Cada STL es **una sola pieza sólida**, con el relieve unido a la base. Se imprime tumbada, con el dibujo hacia arriba y sin soportes.

| Archivo (`salida/`) | Pieza | Medidas |
|---|---|---|
| `Pont_de_Sant_Jordi_ALCOI.stl` | Pont de Sant Jordi + ALCOI | 56 × 30 mm de cuerpo (63,4 mm con la oreja) × 4 mm |
| `Escudo_FERRER.stl` | Escudo con torre + FERRER | 35 × 45 mm de cuerpo (53,4 mm con la oreja) × 4 mm |

Para cada pieza hay estas imágenes, sacadas del STL ya terminado:

- `*_vista_frontal.png`: vista de frente.
- `*_vista_3d.png`: vista inclinada.
- `*_comparacion.png`: la foto enderezada con el contorno del modelo encima, al lado de la vista frontal.

## Alturas y cambio de filamento

| Z | Qué | Color | Capas (a 0,2 mm, primera capa también de 0,2) |
|---|---|---|---|
| 0 a 3,2 mm | base | negro mate | 1 a 16 |
| 3,2 a 4,0 mm | todo el relieve | marfil (puente) / ocre (escudo) | 17 a 20 |

**Cambio de filamento en la capa 17 (Z = 3,40 mm).** En Anycubic Slicer Next, en la vista previa, sube el deslizador de capas hasta la 17 (3,40). Pulsa el «+» y elige *Cambiar filamento* → la ranura del ACE Pro con el marfil o el ocre. La base usa la ranura del negro.

## Comprobaciones (salen al ejecutar `generar.py`)

- Malla cerrada, normales coherentes, un solo cuerpo. Las únicas alturas son Z = 0, 3,2 y 4,0, y toda la cara de abajo está en Z = 0.
- El agujero de Ø5,2 mm atraviesa la oreja. Queda un mínimo de 2,8 mm de plástico alrededor en el puente y 2,2 mm en el escudo. La unión entre la oreja y el cuerpo está redondeada (radio de 1,6 y 1,8 mm).
- Los textos salen de la fuente Montserrat: ALCOI en Bold y FERRER en ExtraBold.

## Ajustes para que se imprima con boquilla de 0,4

- **Barandilla del puente:** en la foto los balaustres miden unos 0,35 mm y van cada 1,1 mm. Ahora miden 0,8 mm, y los huecos entre ellos 0,9 a 1,0 mm. Por eso hay unos 8 huecos por tramo en lugar de 11. El pasamanos pasa de 0,35 a 0,8 mm.
- **Montantes entre arco y tablero:** pasan de unos 0,5 a 0,9 mm, dos a cada lado de cada arco. Se han separado un poco de los pilares para dejar al menos 0,9 mm de hueco.
- **Clave de los arcos:** el arco queda 0,9 mm por debajo del tablero (en la foto, 0,4 mm) y se une a él con un taco de 2,2 mm, como en la foto.
- **Pilares:** las estrías verticales de la foto no se han modelado. Con una sola altura de relieve saldrían como rayas negras. La silueta escalonada de los remates sí está.
- **FERRER:** en la foto las letras están separadas 0,4 a 0,75 mm. Ahora están separadas 0,85 mm, y las letras son un 5 % más estrechas para que la palabra quepa dentro del borde dorado.
- **Oreja del escudo:** es algo mayor que en la foto (radio de 4,8 mm) para que quepa el agujero de 5,2 mm con 2 mm de plástico alrededor.
- **Puntas de las estrellas:** están algo redondeadas. Lo más fino de la punta lo hará el laminador como pueda.
- El dibujo se ha hecho simétrico (en la foto, el pilar derecho y las estrellas están algo desplazados).

## Regenerar

```
pip install trimesh shapely manifold3d fonttools skia-pathops scipy networkx rtree pillow
python3 generar.py
```

En `generar.py` están las medidas tomadas sobre las fotos, en mm o en píxeles, con un comentario por bloque.
La fuente es Montserrat (`fuentes/`, licencia SIL OFL).

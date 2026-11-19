# Adorno de Navidad del paje

Copia de la pieza de la foto `referencia.jpg` (la de arriba): silueta del paje con fez, sin disco ni marco.
Donde en la foto sale el cordón hay un **agujero de 4 mm** para pasarlo.

- Medidas: 59,8 x 80 mm y 3 mm de grosor.
- Vista previa: `salida/paje_vista.png`.

## Archivos (carpeta `salida/`)

| Archivo | Para qué |
|---|---|
| `paje_multicolor.3mf` | La pieza con cada parte ya asignada a su filamento. |
| `paje_0_base_negro.stl` … `paje_3_borla_negro.stl` | Una pieza por parte, por si el 3MF no se abre bien. |

## Capas y filamentos

Mismo orden de filamentos que el Tirisiti (1 blanco, 2 rojo, 3 negro, 4 azul; el azul no se usa):

| Parte | Filamento | Altura | Capas (a 0,2 mm) |
|---|---|---|---|
| Silueta y cara | 3 negro | 0 a 1,6 mm | 1 a 8 |
| Fez y sonrisa | 2 rojo | 1,6 a 2,4 mm | 9 a 12 |
| Ojos | 1 blanco | 1,6 a 2,4 mm | 9 a 12 |
| Borla | 3 negro | 2,4 a 3,0 mm | 13 a 15 |

- El centro de los ojos y la raya de la boca son huecos: se ve el negro de la cara, como en la foto.
- El fez, la boca y los ojos están en relieve sobre la cara; la borla, en relieve sobre el fez.
- En las capas 9 a 12 hay rojo y blanco a la vez, así que ahí la impresora cambia de filamento en cada capa.

Ajustes de Anycubic Slicer Next: los mismos que el Tirisiti (proceso 0,20 mm Standard, sin soportes, relieve hacia arriba). Para cambiar el tamaño, escala solo X e Y.

## Regenerar

```
pip install trimesh shapely mapbox-earcut manifold3d pillow
python3 generar.py
```

En `generar.py` están las medidas tomadas sobre la foto (en píxeles) y, al principio, la altura total (`ALTO`), el diámetro del agujero y el grosor de cada capa. Usa las utilidades de `../bolas-navidad-personaje` para extruir y escribir el 3MF.

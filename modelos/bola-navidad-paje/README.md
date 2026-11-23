# Adorno de Navidad del paje

Copia de la pieza de la foto `referencia.jpg` (la de arriba): silueta del paje con fez, sin disco ni marco.
Donde en la foto sale el cordón hay un **agujero de 4 mm** para pasarlo.

- Medidas: 59,8 x 80 mm y 3 mm de grosor.
- Vista previa: `salida/paje_vista.png`.

## Archivos (carpeta `salida/`)

| Archivo | Para qué |
|---|---|
| `paje_multicolor.3mf` | La pieza con cada parte asignada a su filamento y los ajustes de impresión dentro. |
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

## Ajustes de impresión (ya van dentro del 3MF)

`paje_multicolor.3mf` lleva la impresora, el proceso y los filamentos, sacados de los perfiles oficiales de Anycubic en OrcaSlicer (carpeta `../perfiles-anycubic`):

- **Impresora:** Anycubic Kobra 3 V2 0.4 nozzle, cama Textured PEI a 60 °C.
- **Proceso:** 0.20mm Standard @Anycubic Kobra 3 V2 0.4 nozzle, con estos cambios para esta pieza:
  - capa de 0,2 mm, también la primera (cada color cae justo en su capa);
  - relleno al 100 % (pieza de 3 mm, maciza para que no se doble);
  - sin borde (brim);
  - torre de purga activada, a la derecha de la pieza;
  - perímetro exterior y superficie de arriba a 100 mm/s, para que los detalles salgan limpios;
  - costura atrás, en lo alto del fez.
- **Filamentos:** los 4 con el perfil Anycubic PLA (210 °C, 220 °C en la primera capa). Sirve también para el rojo Elegoo y el azul eSUN.

Al abrirlo, el laminador puede preguntar si quieres cargar los ajustes del proyecto: di que sí.
Comprueba que los filamentos del laminador coinciden con los huecos del ACE Pro (1 blanco, 2 rojo, 3 negro, 4 azul).

## Regenerar

```
pip install trimesh shapely mapbox-earcut manifold3d pillow
python3 generar.py
```

En `generar.py` están las medidas tomadas sobre la foto (en píxeles) y, al principio, la altura total (`ALTO`), el diámetro del agujero y el grosor de cada capa. Usa las utilidades de `../bolas-navidad-personaje` para extruir y escribir el 3MF.

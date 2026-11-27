# Tapa lateral del asiento del copiloto — Seat Córdoba 6K (ref. 191 881 478)

Copia de la pieza del vídeo: la tapa de plástico del lateral del asiento delantero derecho, la que tapa el mecanismo del respaldo.

- Vista previa (arriba, la cara vista; abajo, por detrás): `salida/tapa_vista.png`.
- Fotogramas del vídeo usados: `referencia_delante.jpg`, `referencia_detras.jpg`, `referencia_codigo.jpg`.

## Lo que pone en la pieza

| Marca | Qué es |
|---|---|
| **191 881 478** | Número de recambio original del grupo VAG (Seat/VW). `881` = piezas del asiento delantero, y el número **par (478)** = lado **derecho** (el impar, 477, sería el izquierdo). En los catálogos sale para Seat Córdoba e Ibiza 6K. El recambio nuevo lleva detrás un código de color, p. ej. `191881478 P21` (beige); el negro llevaría otro. |
| **>PE<** | El material: **polietileno**. |
| **Tabla 1–12 / 94–98** | No es una referencia: es el **reloj de fecha** del molde. Las columnas son los meses y las filas los años 1994 a 1998; la marca dice cuándo se fabricó la pieza. |

## Archivos (carpeta `salida/`)

| Archivo | Para qué |
|---|---|
| `tapa_asiento_191881478.3mf` | La pieza con los ajustes de impresión dentro (Kobra 3 V2, boquilla 0,4). |
| `tapa_asiento_191881478.stl` | La misma pieza, por si el 3MF no se abre bien. |

## Cómo es la pieza (y cómo está hecha aquí)

- Carcasa abierta por detrás: placa de 2,5 mm, faldón de 2 mm alrededor y 12 mm de fondo total.
- Cúpula redonda a la izquierda (vista de frente) con un escalón en anillo alrededor; por detrás es hueca, con un tetón en el centro y un nervio redondo.
- Dos agujeros arriba (6 mm) con torreta por detrás, y uno pequeño abajo (4,5 mm).
- Muesca en semicírculo abajo y el extremo derecho en punta.
- Detrás, en relieve, `191 881 478` y `>PE<` en el mismo sitio que la original.

**Medidas ahora: 230 × 103 × 19,5 mm. Son una estimación sacada del vídeo** (la escala sale de la mano). La forma está calcada del fotograma de frente, pero el tamaño hay que confirmarlo con la pieza real.

Lo que aún no lleva: el gancho/clip de detrás y la ligera curva a lo largo que se ve de canto en el vídeo. Se añaden en cuanto haya fotos y medidas de esas zonas.

## Medidas que hacen falta para dejarla exacta

Con un pie de rey o una regla:

1. Largo total, de la punta de la cúpula a la punta derecha.
2. Alto máximo (por la cúpula, de arriba abajo).
3. Diámetro de fuera del anillo y diámetro de la cúpula.
4. Fondo de la pieza apoyada en la mesa boca abajo, y cuánto sobresale la cúpula.
5. Grosor de la placa y del faldón.
6. Diámetro de los 3 agujeros y distancia entre los dos de arriba.
7. Ancho de la muesca de abajo.

Y, si se puede, una foto de cada cara **desde arriba, con la pieza plana en la mesa y una regla al lado**: con eso el contorno sale al milímetro.

## Ajustes de impresión (ya van dentro del 3MF)

- **Impresora:** Anycubic Kobra 3 V2 0.4 nozzle, perfiles oficiales de OrcaSlicer (`../perfiles-anycubic`).
- **Proceso:** 0.20mm Standard con estos cambios:
  - se imprime con la cara vista hacia arriba y el faldón sobre la cama;
  - soportes en árbol solo desde la cama (la placa hace de techo sobre el hueco de detrás);
  - 3 perímetros (el faldón sale macizo), 6 capas arriba, relleno al 30 %;
  - borde (brim) de 6 mm por fuera, porque la pieza es larga y apoya en un faldón fino;
  - costura atrás, en el canto de arriba.
- **Filamento:** el perfil del 3MF es PLA, pero **para el coche mejor PETG o ASA**: dentro de un coche al sol se pasa de 60 °C y el PLA se deforma. La original es de polietileno.

## Regenerar

```
pip install trimesh shapely mapbox-earcut manifold3d matplotlib pillow scipy
python3 generar.py
```

En `generar.py`, al principio, están `LARGO` (lo que escala todo el contorno), los grosores, la altura de la cúpula y los diámetros de los agujeros. Al tener las medidas reales, se cambian ahí y se vuelve a generar.

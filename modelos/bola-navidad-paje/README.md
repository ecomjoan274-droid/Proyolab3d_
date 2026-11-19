# Bola de Navidad plana con el paje

Mismo formato que las bolas del Tirisiti (`../bolas-navidad-personaje`): adorno plano de 80 mm de diámetro (89,5 mm con la anilla) y 3,4 mm de grosor, en 4 colores (uno por cada hueco del ACE Pro).

El paje sigue la foto `referencia.jpg`: cara redonda, fez rojo con borla negra, ojos redondos blancos con la pupila en el centro y sonrisa roja con una raya negra.

Vista previa: `salida/bola_paje_vista.png`.

## Archivos (carpeta `salida/`)

| Archivo | Para qué |
|---|---|
| `bola_paje_multicolor.3mf` | La bola con cada pieza ya asignada a su filamento. |
| `bola_paje_0_base_blanco.stl` … `_3_azul.stl` | Una pieza por color, por si el 3MF no se abre bien. |
| `bola_paje_completa.stl` | Una sola pieza, para cambio de filamento por capa. |

## Filamentos

Los mismos que el Tirisiti y en el mismo orden, así que se pueden imprimir juntas sin tocar el ACE Pro:

| Nº | Color | Pieza | Altura | Capas (a 0,2 mm) |
|---|---|---|---|---|
| 1 | Blanco | Base y ojos | 0 a 1,6 mm | 1 a 8 |
| 2 | Rojo | Fez, sonrisa, aro y puntos | 1,6 a 2,2 mm | 9 a 11 |
| 3 | Negro | Cara, borla, pupilas, contornos y filete del aro | 2,2 a 2,8 mm | 12 a 14 |
| 4 | Azul | Copos de nieve | 2,8 a 3,4 mm | 15 a 17 |

Los ojos son huecos en la cara que dejan ver el blanco de la base; la sonrisa queda un escalón por debajo de la cara.
Los ajustes de Anycubic Slicer Next son los mismos que los del Tirisiti (ver su README).

## Regenerar

```
pip install trimesh shapely mapbox-earcut manifold3d pillow
python3 generar.py
```

- `dibujo_paje.py` tiene el dibujo (medidas en mm: cara, fez, borla, ojos y sonrisa al principio).
- `generar.py` construye la bola usando las piezas del generador del Tirisiti; los copos y los puntos se cambian al principio.

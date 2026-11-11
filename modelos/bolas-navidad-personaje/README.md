# Bolas de Navidad planas con el personaje

Dos adornos planos de 80 mm de diámetro (89,5 mm con la anilla) y 3,4 mm de grosor:

- `bola_busto_*`: retrato del personaje.
- `bola_cuerpo_entero_*`: el personaje de cuerpo entero, sin la peana.

Vista previa: `salida/vista_las_dos_bolas.png`.

## Archivos (carpeta `salida/`)

| Archivo | Para qué |
|---|---|
| `bola_<versión>_completa.stl` | Una sola pieza. Para imprimir con cambio de filamento por capa. |
| `bola_<versión>_0_base_blanco.stl`, `_1_rojo`, `_2_piel`, `_3_negro` | Una pieza por color. Para multicolor (ACE Pro). |

## Cómo imprimir

Altura de capa 0,2 mm (también la primera), sin soportes, con el relieve hacia arriba.

| Color | Altura | Capas |
|---|---|---|
| Blanco | 0 a 1,6 mm | 1 a 8 |
| Rojo | 1,6 a 2,2 mm | 9 a 11 |
| Piel (beige) | 2,2 a 2,8 mm | 12 a 14 |
| Negro | 2,8 a 3,4 mm | 15 a 17 |

- **Con una sola boquilla:** abre `bola_<versión>_completa.stl` y añade un cambio de filamento al empezar las capas 9, 12 y 15.
- **Con multicolor:** arrastra los cuatro STL de una versión a la vez, acepta cargarlos como un solo objeto con varias piezas y asigna un filamento a cada pieza.
- **Para cambiar el tamaño:** escala solo X e Y. Si escalas Z, las alturas de la tabla dejan de coincidir con las capas.

## Regenerar

```
pip install trimesh shapely mapbox-earcut opencv-python-headless manifold3d scipy pillow
python3 generar.py
```

`clasificar.py` separa el dibujo `personaje.png` en los cuatro colores y `generar.py` construye los modelos. El diámetro, el grosor y los adornos se cambian al principio de `generar.py`.

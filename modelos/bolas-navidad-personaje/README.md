# Bolas de Navidad planas con Tirisiti

Dos adornos planos de 80 mm de diámetro (89,5 mm con la anilla) y 3,4 mm de grosor, en 4 colores (uno por cada hueco del ACE Pro):

- **Busto:** retrato del personaje.
- **Cuerpo entero:** el personaje completo, sin la peana.

Vista previa: `salida/vista_las_dos_bolas.png`.

## Archivos (carpeta `salida/`)

| Archivo | Para qué |
|---|---|
| `bolas_tirisiti_multicolor.3mf` | Las dos bolas en una placa, con cada pieza ya asignada a su filamento. |
| `bola_busto_multicolor.3mf`, `bola_cuerpo_entero_multicolor.3mf` | Cada bola por separado, también con los filamentos asignados. |
| `bola_<versión>_0_base_blanco.stl` … `_3_azul.stl` | Una pieza por color, por si el 3MF no se abre bien. |
| `bola_<versión>_completa.stl` | Una sola pieza, para cambio de filamento por capa. |

Los 3MF no llevan impresora ni perfil dentro: el laminador conserva los que tengas elegidos.

## Filamentos

El 3MF asigna las piezas a estos números de filamento. Pon los filamentos en este orden en el ACE Pro:

| Nº | Color | Pieza | Altura | Capas (a 0,2 mm) |
|---|---|---|---|---|
| 1 | Blanco | Base, cara, manos y camisa | 0 a 1,6 mm | 1 a 8 |
| 2 | Rojo | Chaqueta, boina, aro y estrellas | 1,6 a 2,2 mm | 9 a 11 |
| 3 | Negro | Pelo, cejas, ojos, nariz, boca, pantalón y contornos | 2,2 a 2,8 mm | 12 a 14 |
| 4 | Azul | Corbata | 2,8 a 3,4 mm | 15 a 17 |

La cara y las manos van en blanco con un contorno negro para que se distingan del fondo.
Cada color ocupa sus propias capas, así que la impresora solo cambia de filamento tres veces en toda la impresión.

Al abrir el 3MF, comprueba que en la lista de filamentos del laminador el 1 es blanco, el 2 rojo, el 3 negro y el 4 azul.
Si ves el modelo solo en blanco y rojo, es que el laminador tiene esos colores puestos en los huecos 3 y 4; cámbialos ahí y la vista se corrige.

## Ajustes en Anycubic Slicer Next

- **Impresora:** Anycubic Kobra 3 V2 con ACE Pro (4 filamentos), boquilla de 0,4 mm.
- **Proceso:** 0,20 mm Standard. Con 0,2 mm cada color ocupa exactamente tres capas.
- **Blanco y negro (Anycubic PLA):** el perfil "Anycubic PLA" tal cual.
- **Rojo (Elegoo) y azul (eSUN):** perfil de PLA genérico a 210 °C. Si el eSUN es PLA+, 215 °C.
- **Torre de purga:** activada, con los volúmenes de purga por defecto.
- **Soportes y balsa:** no hacen falta. Relieve hacia arriba.
- **Para cambiar el tamaño:** escala solo X e Y. Si escalas Z, las alturas de la tabla dejan de coincidir con las capas.

## Regenerar

```
pip install trimesh shapely mapbox-earcut opencv-python-headless manifold3d scipy pillow
python3 generar.py
```

- `clasificar.py` separa el dibujo `personaje.png` por colores (la piel se imprime en blanco).
- `generar.py` construye los modelos. El diámetro, el grosor y los adornos se cambian al principio.
- `proyecto_3mf.py` escribe el 3MF con los filamentos asignados.

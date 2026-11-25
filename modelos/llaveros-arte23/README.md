# Llaveros para Arte23

Dos llaveros a dos colores para llevar como muestra a Arte23 (artesanía, recuerdos de Alcoi y heráldica personalizada).
Ambos tienen una base de 3,2 mm y un relieve de 0,6 mm, y llevan un orificio pasante de 5 mm.
Se imprimen planos, sin soportes, con boquilla de 0,4 mm y capas de 0,20 mm.

| | Pont de Sant Jordi | Escudo personalizable |
|---|---|---|
| Vista | `salida/vista_pont_sant_jordi.png` | `salida/vista_escudo_mostra.png` |
| STL | `salida/llavero_pont_sant_jordi.stl` | `salida/llavero_escudo_mostra.stl` |
| Fuente editable | `fuentes/llavero_pont_sant_jordi.scad` | `fuentes/llavero_escudo.scad` |
| Medidas | 55,0 × 30,0 × 3,8 mm | 42,0 × 48,0 × 3,8 mm |
| Material alrededor del orificio | 4,1 mm | 2,9 mm |
| PLA (relleno 100 %, sin purga) | 6,8 g | 6,3 g |

`fuentes/comun.scad` reúne las medidas comunes: grosores, redondeos, orificio y fuente.
`salida/placa_llaveros_arte23.3mf` contiene los dos llaveros en una placa de la Kobra 3 V2.
`salida/comprobaciones.txt` es el informe de las comprobaciones.

## Diseño

### 1. Pont de Sant Jordi

- Perfil del puente: tablero horizontal y cuatro pilas centrales con **tres grandes arcos parabólicos iguales**, cuya clave llega hasta el tablero. Entre el arco y el tablero hay montantes verticales. Sobre las pilas se levantan las **torres escalonadas art déco** del pretil (las que llevan las farolas). En cada extremo hay un arco menor.
- El puente se apoya en una línea de suelo continua, de modo que el relieve forma una sola pieza, sin pilas ni torres sueltas. La base es una placa maciza de 3,2 mm.
- El texto «ALCOI» va en Liberation Sans Bold, con mayúsculas de 5,6 mm y algo de espacio entre letras.
- El orificio está en un panel a la izquierda, separado por una línea vertical en relieve. El marco perimetral en relieve da un acabado sobrio, de placa o sello.
- **Referencia:** la ficha del puente en Visit Alcoy (`visitalcoy.com/puentes/puentesanjorge/`, enlazada desde `visitalcoy.com/es/puentes/`) devolvía un error 404. El listado solo confirma «se inauguró en 1931 y se alza sobre el río Riquer». Para el perfil usé el artículo «Puente de San Jorge (Alcoy)» de Wikipedia (art déco, hormigón armado, cuatro pilas centrales con arcos parabólicos, farolas) y dos fotos laterales de Wikimedia Commons («Vista lateral del pont de sant Jordi, Alcoi» y «Pont de sant Jordi d'Alcoi, vista lateral»). Las fotos solo sirvieron de referencia y no van en el repositorio.

### 2. Escudo personalizable

- Es un escudo español (de punta redonda) con anilla arriba y borde en relieve de 1,4 mm. Una faja horizontal separa la zona del apellido (arriba) del motivo (abajo).
- **Apellido** (`APELLIDO = "MOSTRA"`): mayúsculas de 5 mm en Liberation Sans Bold, con el trazo engrosado 0,15 mm para que las diagonales de la M superen los 0,8 mm. Si un apellido no cabe en 34 mm, primero se estrecha hasta el 80 % y después se reduce entero. La consola de OpenSCAD avisa si la letra baja de 3,5 mm. Va colocado por la línea base, así que las tildes y las cedillas no descolocan el texto. Lo probé con «BERENGUER» (cabe bien) y con «BERENGUER-ÇOLÀ» (salta el aviso, porque es demasiado largo).
- **Motivo de muestra (propio):** estrella de ocho puntas formada por dos cuadrados entrelazados, con un anillo y un rombo en el centro. Los trazos son de 1,2 mm (3 líneas de 0,4).
- **Para cambiarlo por el diseño de Arte23:** pon `MOTIVO_SVG = "arte23_motivo.svg"` con el SVG en `fuentes/`. El diseño se centra, se escala a 21 mm por el lado indicado en `MOTIVO_SVG_LADO` (`"alto"` o `"ancho"`) y se recorta al círculo de la zona del motivo. Las partes de menos de 0,8 mm se eliminan. El SVG debe tener formas rellenas y cerradas, no solo trazos. La importación la probé con un SVG de ejemplo.

### Común a los dos

- **Base:** 3,2 mm (16 capas). El canto superior está redondeado con radio 0,8 mm y el inferior lleva un chaflán de 0,4 mm a 45°. Las superficies son lisas, hechas con una suma de Minkowski.
- **Relieve:** 0,6 mm (3 capas), y **todo empieza en z = 3,2 mm**. Basta un solo cambio de color al empezar la capa 17.
- **Orificio:** pasante de 5 mm, con chaflán de 0,4 mm en las dos bocas.
- **Grosores mínimos:** ningún trazo del relieve baja de 0,8 mm y ninguna separación entre piezas del relieve baja de 0,6 mm.

## Impresión (Kobra 3 V2 + ACE Pro)

`placa_llaveros_arte23.3mf` lleva los dos llaveros, cada uno en dos partes (base y relieve), con los ajustes del proyecto. Salen de los perfiles oficiales de Anycubic en OrcaSlicer (`../perfiles-anycubic`):

- **Impresora y proceso:** Anycubic Kobra 3 V2 0.4 nozzle, 0.20mm Standard, con capa de 0,20 mm también en la primera.
- **Relleno:** 100 %, para que el llavero aguante el uso diario y no se doble.
- **Sin soportes ni borde.** La torre de purga está activada, detrás de los llaveros.
- **Filamentos:** el mismo orden del ACE Pro que en los proyectos anteriores (1 blanco, 2 rojo, 3 negro, 4 azul). La **base va en el 1 (blanco)** y el **relieve en el 3 (negro)**. Por eso, en toda la placa hay **un solo cambio de color**, de blanco a negro, en la capa 17. Cada capa es de un solo color.
- Elegí negro sobre blanco y no al revés porque el negro cubre bien en solo 3 capas y necesita poca purga. El blanco sobre negro deja ver un velo gris.
- Si prefieres otros colores, cambia el filamento de cada parte en el laminador. Para que siga habiendo un solo cambio, los dos llaveros de la misma placa deben compartir la pareja de colores.

**Con los STL sueltos:** el STL de cada llavero es de una sola pieza. Ábrelo en Anycubic Slicer Next y añade un cambio de filamento al empezar la capa 17 (z = 3,2 mm), con clic derecho en el deslizador de capas. Así obtienes el mismo resultado.

## Comprobaciones hechas (`salida/comprobaciones.txt`)

`generar.py` lo regenera todo con OpenSCAD y comprueba cada STL:

- Medidas exactas: 55 × 30 × 3,8 mm y 42 × 48 × 3,8 mm.
- Malla cerrada: estanca, normales coherentes, una sola pieza y sin errores en manifold3d.
- Orificio de 5 mm libre en toda la altura, con cortes cada 0,1 mm.
- Material alrededor del orificio de al menos 2,5 mm (4,1 y 2,9 mm).
- Todo el relieve entre z = 3,2 y 3,8 mm, sin ninguna otra altura.
- Trazos de al menos 0,8 mm y piezas del relieve separadas al menos 0,6 mm. Hay muescas más estrechas en los ángulos agudos de algunas letras (como la A o la M): ahí se rellena la punta y la letra se sigue leyendo.
- Sin voladizos de más de 45° ni techos sueltos, así que no hacen falta soportes.

## Pendiente

- **Laminado real, gramos y tiempo.** No he podido laminar. No encontré una versión de Anycubic Slicer Next para Linux que pudiera descargar, y no tenía permiso para instalar otro laminador en este entorno. Los gramos de la tabla salen del volumen de la malla con relleno al 100 % (PLA a 1,24 g/cm³). Al laminar habrá que sumar la torre y la purga del cambio de color. **El tiempo de impresión no está estimado.** Abre el 3MF en Anycubic Slicer Next, pulsa «Laminar» y anota los gramos y el tiempo reales.
- **Apertura del 3MF en Anycubic Slicer Next.** Usa el mismo formato que los 3MF anteriores del repositorio, pero no lo he abierto en el laminador. Comprueba que cada parte tiene su filamento y que la vista previa muestra el cambio en la capa 17. Si pregunta si cargar los ajustes del proyecto, di que sí.
- **Impresión física:** queda pendiente de tu revisión.
- **Motivo de Arte23:** a la espera del SVG.

## Regenerar

```
pip install trimesh shapely manifold3d pillow numpy scipy networkx
python3 generar.py
```

Hace falta OpenSCAD 2021.01 o posterior en el PATH. OpenSCAD incluye la fuente Liberation Sans en Windows, macOS y Linux. Si solo quieres un STL, abre el `.scad` en OpenSCAD, cambia los parámetros del principio (en el Personalizador o en el texto), pulsa F6 y exporta.

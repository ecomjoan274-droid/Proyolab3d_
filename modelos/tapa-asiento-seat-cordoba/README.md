# Tapa lateral del asiento del copiloto — Seat Córdoba 6K (ref. 191 881 478)

Copia de la tapa de plástico del lateral del asiento delantero derecho, la que tapa el mecanismo del respaldo.

- Vista previa (arriba, la cara vista; abajo, por detrás): `salida/tapa_vista.png`.
- Fotogramas del vídeo de la pieza: `referencia_delante.jpg`, `referencia_detras.jpg`, `referencia_codigo.jpg`.

## Qué pieza es

| Marca | Qué es |
|---|---|
| **191 881 478** | Recambio original de Volkswagen: **"Verkleidung Sitzgestell, rechts, ohne Loch"**, es decir, la tapa del armazón del asiento, lado **derecho**, **sin agujero**. El 191 881 477 es la izquierda, y según una tienda el 191 881 480 es la versión con agujero. Detrás del número va el color: `LX6` (negro satinado), `U71` (gris franela), `P21` (beige)… |
| **>PE<** | El material: **polietileno**. |
| **Tabla 1–12 / 94–98** | No es una referencia: es el **reloj de fecha** del molde (meses y años 1994–1998). Indica cuándo se fabricó la pieza. |

Es la misma tapa en Golf 2, Jetta 2, Scirocco 2, Corrado, Golf 1 Cabrio, Caddy, Polo y Lupo, y en Seat Ibiza y Córdoba 6K.

### Medidas oficiales

Del catálogo **Volkswagen Classic Parts** (191 881 478 U71): **210 mm de largo × 95 mm de ancho × 15 mm de alto**.

La relación ancho/largo que sale de la foto (0,449) y del vídeo (0,446) cuadra con la del catálogo (0,452): la forma es la buena.

## Cómo está hecha

| Qué | De dónde sale |
|---|---|
| Contorno, círculo de la cúpula y posición de los 3 agujeros | Foto cenital de una pieza nueva (anuncio de omecar.de), calcada con `calcar_contorno.py` y escalada a 210 mm. Está en `contorno.json`. |
| Largo 210 mm, alto total 15 mm | Catálogo Volkswagen Classic Parts. |
| Perfil de la cúpula (borde redondeado, valle y cúpula central) | Radios medidos en la misma foto. |
| Alturas: borde bajo y pared alta | Foto de canto de la pieza (canto de la muesca): la pared alta mide casi el doble que el borde bajo (90 px frente a 46 px). |
| Pivote, bloques, media luna y pestaña de detrás | Fotos de la parte de detrás con las flechas y el segundo vídeo. |

Vista previa (`salida/tapa_vista.png`), de arriba abajo: cara vista, de canto (mirando el canto de la muesca), por detrás y por detrás en tres cuartos.

### Alturas (con la pieza boca arriba, apoyada en la pared alta)

- **Pared alta**: de la muesca a la punta por el canto en diagonal, y por el extremo derecho. Llega hasta la cama: **11,5 mm** de la cama a la cara vista, con 5 mm de grueso.
- **Borde bajo**: todo lo demás (alrededor de la cúpula, el canto de arriba y el de abajo hasta la muesca). Baja solo **5,9 mm** desde la cara vista, así que se queda a 5,6 mm de la cama. Ese es el escalón que se ve de canto.
- **Cúpula**: 75,4 mm de diámetro; sobresale 3,5 mm de la cara vista (15 mm en total, como en el catálogo).

### Por detrás

- **Pivote con dientes** (clip de abeto) en el agujero de arriba que está junto a la cúpula: 6,5 mm de grueso, con tres dientes de 8,5 mm, y llega casi hasta la cama.
- **Bloque largo** de la cúpula hacia el pivote, **un bloque** a la derecha del pivote y **otro** junto al segundo agujero, con una **media luna** en relieve encima.
- **Pestaña** pegada al canto de arriba.
- Torretas en el agujero de abajo y en el segundo de arriba; cuenco de la cúpula con tetón y nervio redondo.
- Sin reloj de fecha, número ni `>PE<` (no hacen falta).

**Medidas: 210 × 94 × 15 mm.**

### Lo que aún es aproximado

Las alturas salen de proporciones en las fotos y del alto del catálogo, no de una medida con regla. Los tamaños de los bloques y del pivote están medidos en una foto tomada en ángulo. Si al probarla algo no encaja, con la medida de esa zona se corrige en `generar.py` (todo está al principio).

## Archivos (carpeta `salida/`)

| Archivo | Para qué |
|---|---|
| `tapa_asiento_191881478.3mf` | La pieza con los ajustes de impresión dentro (Kobra 3 V2, boquilla 0,4). |
| `tapa_asiento_191881478.stl` | La misma pieza, por si el 3MF no se abre bien. |

## Ajustes de impresión (ya van dentro del 3MF)

- **Impresora:** Anycubic Kobra 3 V2 0.4 nozzle, perfiles oficiales de OrcaSlicer (`../perfiles-anycubic`).
- **Proceso:** 0.20mm Standard con estos cambios:
  - cara vista hacia arriba, apoyada en la pared alta;
  - soportes en árbol solo desde la cama: sostienen el borde bajo (a 5,6 mm de la cama), la punta del pivote y la placa, que hace de techo sobre el hueco de detrás;
  - 3 perímetros, 6 capas arriba, relleno al 30 %;
  - borde (brim) de 6 mm por fuera;
  - costura atrás, en el canto de arriba.
- **Filamento:** el 3MF lleva el perfil de PLA, pero **para el coche mejor PETG o ASA**: al sol el coche pasa de 60 °C y el PLA se deforma. La original es de polietileno.

## Fuentes

- Medidas: [Volkswagen Classic Parts / Stein Gruppe — 191 881 478 U71](https://volkswagen.steingruppe.de/detail/index/sArticle/124444)
- Foto calcada: [omecar.de — Verkleidung Blende Abdeckung Sitz 191881478 LX6](https://omecar.de/shop/vw-golf-2-gt-gti-16v-g60-rallye-verkleidung-blende-abdeckung-sitz-191881478-lx6/)
- "Rechts, ohne Loch" y modelos: [oldtimer-werk.de — Cover, right front seat, no hole](https://www.oldtimer-werk.de/en/golf-1-co/interior/assembly-parts/2262/cover-right-front-seat-no-hole-black-golf-co-oe-ref.-191881478)
- Seat Córdoba / Ibiza 6K: [oemwolf.com — 191881478 P21](https://oemwolf.com/oem-parts/191881478p21.html)

## Regenerar

```
pip install trimesh shapely mapbox-earcut manifold3d matplotlib pillow scipy contourpy
python3 generar.py
```

`contorno.json` ya está hecho. Para volver a calcarlo, se descarga la foto de omecar y se pasa a `calcar_contorno.py foto.jpg`.
En `generar.py`, al principio, están el alto total, lo que sobresale la cúpula, los grosores y los diámetros de los agujeros.

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
| Alturas de canto, escalón, redondeo del canto y todo lo de detrás | Vídeo de la pieza (de canto a los 44 s, por detrás a los 10 s y de 54 a 64 s). |

Vista previa, de arriba abajo: cara vista, de canto (mirando el canto de arriba), por detrás y por detrás en tres cuartos.

### Por delante

- **Cúpula de 75,4 mm**: su borde de fuera es el propio contorno de la pieza a la izquierda y sube recto desde el faldón. Por eso, de canto, **la zona de la cúpula es más alta y hay un escalón** donde empieza el cuerpo (como en el vídeo a los 44 s).
- La cara vista **baja hacia la punta**: 10,5 mm de la cama a la cara en el lado de la cúpula y 9,5 mm en la punta; la cúpula llega a 15 mm.
- Canto de la cara vista redondeado (radio 3 mm), muesca y punta calcadas de la foto.

### Por detrás

- Placa de 2,2 mm y faldón de 1,8 mm alrededor.
- Cuenco de la cúpula con tetón en el centro y nervio redondo alrededor.
- **Pared gruesa (4,5 mm) en el canto en diagonal**, de la muesca a la punta: en el vídeo es el bloque que sobresale junto a la muesca.
- Torretas en los 3 agujeros (en tu pieza la de arriba está rota; aquí va entera).
- Nervio recto que pasa por la torreta de arriba, desde la cúpula.
- Zona en relieve junto al segundo agujero y dos marcas redondas del expulsor.
- En relieve: **reloj de fecha** (meses 1–12, años 94–98), `191 881 478` y `>PE<`, en su sitio.

**Medidas: 210 × 94 × 15 mm.**

### Lo que aún es aproximado

El vídeo no da milímetros, así que estas medidas están estimadas:
- las alturas de canto (10,5 mm en el lado de la cúpula y 9,5 mm en la punta);
- el grosor de la placa y del faldón, y el de la pared en diagonal;
- el diámetro de los agujeros;
- la posición exacta de los nervios y las marcas de detrás.

Las pestañas que sobresalen del faldón por detrás tampoco van: en el vídeo no se ve bien cuántas son ni dónde están.

Para dejarlo exacto hacen falta estas medidas de la pieza original (con regla o pie de rey):
1. con la pieza boca abajo en la mesa, la altura de la mesa a lo alto de la cúpula;
2. lo mismo en el cuerpo junto a la cúpula y en la punta;
3. el grosor de la placa (por un agujero) y del faldón;
4. el diámetro de los agujeros;
5. una foto de la parte de detrás desde arriba, plana y con una regla al lado, y otra de canto con la regla.

## Archivos (carpeta `salida/`)

| Archivo | Para qué |
|---|---|
| `tapa_asiento_191881478.3mf` | La pieza con los ajustes de impresión dentro (Kobra 3 V2, boquilla 0,4). |
| `tapa_asiento_191881478.stl` | La misma pieza, por si el 3MF no se abre bien. |

## Ajustes de impresión (ya van dentro del 3MF)

- **Impresora:** Anycubic Kobra 3 V2 0.4 nozzle, perfiles oficiales de OrcaSlicer (`../perfiles-anycubic`).
- **Proceso:** 0.20mm Standard con estos cambios:
  - cara vista hacia arriba y faldón sobre la cama;
  - soportes en árbol solo desde la cama (la placa hace de techo sobre el hueco de detrás);
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

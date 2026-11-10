# Perfil "crema" – Anycubic Kobra 3 V2 · boquilla 0.4 · PLA Elegoo

Perfiles para **Anycubic Slicer Next** pensados para el modelo
`llavero_botecito_kiroestetika_v2` (bote con rosca + tapa con logo bicolor).

| Archivo | Qué es |
|---|---|
| `crema.json` | Perfil de **proceso** (calidad) llamado `crema` |
| `crema PLA Elegoo.json` | Perfil de **filamento** para PLA Elegoo |
| `llavero_botecito_kiroestetika_v2_crema.3mf` | Tu proyecto, sin los ajustes por objeto que pisaban el perfil |

## Cómo instalarlo

1. Abre Anycubic Slicer Next y elige la impresora **Anycubic Kobra 3 V2 0.4 nozzle**.
2. **Archivo → Importar → Importar configuraciones…** y selecciona `crema.json`
   y `crema PLA Elegoo.json`.
3. Abre `llavero_botecito_kiroestetika_v2_crema.3mf`.
4. En **Proceso** elige `crema`. En **Filamento**, asigna `crema PLA Elegoo` a los
   **dos** filamentos (1 = marrón, 2 = verde del logo).
5. En **Tipo de placa** elige **Textured PEI Plate**.
6. Lamina y revisa la vista previa (mira las capas 1 a 4, que llevan el logo).

> Si la importación falla, crea el perfil a mano: parte de
> "0.12mm Standard @Anycubic Kobra 3 V2 0.4 nozzle", cambia los valores de la
> tabla de abajo y usa **Guardar como → `crema`**.

## Por qué estos valores

Medidas del modelo: bote de Ø32 × 21 mm con rosca exterior (de 14 a 20,5 mm),
tapa de Ø32 × 9,3 mm con rosca interior y logo verde de **0,6 mm**
hundido en la cara que apoya en la cama.

| Ajuste | Valor | Motivo |
|---|---|---|
| Altura de capa | **0,12 mm** | Rosca suave y buen detalle sin disparar el tiempo |
| Primera capa | **0,24 mm** | 0,24 + 3 × 0,12 = **0,60 mm**: el logo termina justo en una capa y solo hay 4 capas con cambio de color |
| Generador de perímetros | Arachne | Letras y bordes del logo más limpios |
| Perímetros | 4 | Pared y rosca resistentes |
| Capas sup./inf. | 8 / 6 | Superficies cerradas, sin transparencias |
| Relleno | 25 % gyroid | Pieza rígida para un llavero |
| Compensación pata de elefante | 0,15 mm | Cara del logo nítida y tapa que no roza |
| Pared exterior precisa | Sí | Medidas de la rosca más exactas |
| Velocidad pared exterior | 60 mm/s · acel. 2000 | Acabado exterior más fino |
| Pared interior / relleno | 120 / 180 mm/s | Velocidad donde no se ve |
| Sup. superior | 80 mm/s · acel. 2000 | Superficie superior más limpia |
| Primera capa | 40 mm/s · acel. 500 · línea 0,45 | Buena adherencia y detalle del logo |
| Costura | Alineada | Costura en una sola línea vertical |
| Evitar cruzar perímetros | Sí | Menos marcas e hilos |
| Brim / soportes / planchado | No | No hacen falta en esta pieza |
| Torre de purga | Sí, 35 mm | Obligatoria para el logo bicolor |

**Filamento `crema PLA Elegoo`:** boquilla 210 °C (primera capa 215 °C), cama 60 °C,
flujo 0,98, máx. 15 mm³/s, ventilador al 80–100 % (apagado en la primera capa) y
tiempo mínimo de capa de 10 s. El cuello roscado es pequeño y necesita tiempo para enfriar.

## ¿Placa de fábrica o smooth?

**Recomiendo la de fábrica (PEI texturizada).** Las dos piezas se imprimen con la
cara bonita hacia abajo, sobre todo la tapa con el logo. La textura da un acabado
mate uniforme, disimula las líneas de la primera capa y la unión entre colores, y
el PLA se despega solo al enfriar.

Usa la **smooth** solo si quieres la cara del logo brillante tipo espejo. En ese
caso limpia la placa con alcohol isopropílico, ten la primera capa perfectamente
calibrada (en una placa lisa se ve todo) y cambia el tipo de placa en el laminador.

## Notas

- El logo verde necesita el **ACE Pro** (o un cambio manual de filamento).
- Prueba la rosca con una primera tapa. Si queda dura, pon la **compensación XY
  de agujeros** a `0.05` en la tapa (o la **de contorno** a `-0.05` en el bote).
  Si queda bien, déjalas en 0.
- Calibra el **flujo** y el **avance de presión** (Calibración → Flujo / Pressure
  Advance) con tu rollo de PLA Elegoo para sacar el máximo.

// Protolab3D · Llavero «Escudo personalizable» para Arte23
// 42 × 48 mm · base 3,2 mm + relieve 0,6 mm · orificio pasante de 5 mm
//
// Escudo de punta redonda con borde en relieve, una faja que separa la zona
// del apellido (arriba) y el motivo central (abajo).
//
// PARA PERSONALIZAR:
//   - APELLIDO: escribe el apellido en mayúsculas. Si no cabe en ANCHO_TEXTO_MAX,
//     primero se estrecha (hasta el 80 %) y luego se reduce; nunca se sale del escudo.
//     Con más de unas 9 letras la consola avisa si la letra baja de 3,5 mm.
//   - MOTIVO_SVG: deja "" para el motivo geométrico de muestra, o pon la ruta
//     de un SVG (por ejemplo "arte23_motivo.svg", en esta misma carpeta) con el
//     diseño que facilite Arte23. Se centra, se escala a ZONA_MOTIVO mm por el
//     lado que indique MOTIVO_SVG_LADO y se recorta al círculo de la zona.
//     El SVG debe ser un dibujo relleno (formas cerradas, sin solo trazos);
//     las partes de menos de 0,8 mm se eliminan porque no se imprimirían bien.
//
// Origen en la esquina inferior izquierda; X a lo ancho, Y a lo alto.

include <comun.scad>

/* [Personalización] */
APELLIDO = "MOSTRA";
MOTIVO_SVG = "";              // "" = motivo de muestra; o ruta a un .svg
MOTIVO_SVG_LADO = "alto";     // "alto" o "ancho": lado del SVG que mide ZONA_MOTIVO

/* [Escudo] */
ANCHO = 42;
ALTO_ESCUDO = 39;           // de la punta al jefe (borde superior)
R_ESQ = 3;                  // esquinas superiores del escudo
MARCO_IN = 1.0;             // el borde en relieve empieza tras el canto redondeado
MARCO_W  = 1.4;
FAJA_Y = 27.4; FAJA_W = 1.2; // faja horizontal bajo el apellido

/* [Anilla] */
C_AGUJERO = [ANCHO / 2, 42.6];
R_ANILLA = 5.4;             // 5,4 − 2,5 = 2,9 mm de material alrededor del orificio
R_UNION = 1.5;              // redondeo del encuentro anilla-escudo
// alto total = C_AGUJERO.y + R_ANILLA = 48 mm

/* [Texto] */
TEXTO_ALTO = 5.0;           // altura de las mayúsculas (mm)
TEXTO_ESPACIADO = 1.12;
ANCHO_TEXTO_MAX = 34;       // ancho útil en la zona del apellido
TEXTO_GROSOR = 0.15;        // engorda el trazo: las diagonales de la M quedan por encima de 0,8 mm

/* [Motivo] */
C_MOTIVO = [ANCHO / 2, 15.0];
ZONA_MOTIVO = 21;           // diámetro de la zona reservada al motivo
TRAZO = 1.2;                // grueso de línea del motivo de muestra (3 líneas de 0,4)

// ---------------------------------------------------------------- 2D

module escudo() {           // escudo español: rectángulo con la punta en semicírculo
    offset(r = R_ESQ) offset(delta = -R_ESQ) union() {
        translate([0, ANCHO / 2]) square([ANCHO, ALTO_ESCUDO - ANCHO / 2]);
        intersection() {
            translate([ANCHO / 2, ANCHO / 2]) circle(d = ANCHO, $fn = 192);
            square([ANCHO, ANCHO / 2 + 0.01]);
        }
    }
}

module contorno() {
    offset(r = -R_UNION) offset(r = R_UNION) union() {
        escudo();
        translate(C_AGUJERO) circle(r = R_ANILLA);
    }
}

module borde() {
    difference() {
        offset(delta = -MARCO_IN) escudo();
        offset(delta = -(MARCO_IN + MARCO_W)) escudo();
    }
    // faja
    intersection() {
        offset(delta = -MARCO_IN - 0.01) escudo();
        translate([0, FAJA_Y]) square([ANCHO, FAJA_W]);
    }
}

// Anchura de cada letra (Liberation Sans Bold, unidades de la fuente; 1 em = 2048)
CARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZÑÇÁÉÍÓÚÀÈÒÏÜ -'·.";
AVANCE = [1479,1479,1479,1479,1366,1251,1593,1479,569,1139,1479,1251,1706,1479,1593,1366,
          1593,1479,1366,1251,1479,1366,1933,1366,1366,1251,1479,1479,1479,1366,569,1593,
          1479,1479,1366,1593,569,1479,569,682,487,682,569];
function avance(c) = let(r = search(c, CARS)) len(r) > 0 ? AVANCE[r[0]] : 1480;
function suma(v, i = 0) = i >= len(v) ? 0 : v[i] + suma(v, i + 1);
// En OpenSCAD, con size = s la mayúscula mide 0,9555·s y 1 em mide 1,3889·s
TAM = TEXTO_ALTO / 0.9555;
function ancho_natural(t) = suma([for (c = t) avance(c)]) * TEXTO_ESPACIADO * TAM * 1.3889 / 2048;
// Si el apellido no cabe: primero se estrecha hasta un 80 %; si aún no cabe, se
// reduce la letra entera (y se avisa si baja de 3,5 mm, el mínimo que se lee bien).
AJUSTE = ANCHO_TEXTO_MAX / ancho_natural(APELLIDO);
ESTRECHAR = min(1, max(0.8, AJUSTE));
REDUCIR = min(1, AJUSTE / ESTRECHAR);
if (TEXTO_ALTO * REDUCIR < 3.5)
    echo(str("AVISO: con «", APELLIDO, "» la letra queda en ", TEXTO_ALTO * REDUCIR,
             " mm; usa iniciales o un apellido más corto"));

module apellido() {
    y = (FAJA_Y + FAJA_W + ALTO_ESCUDO - MARCO_IN - MARCO_W) / 2;   // centro de las mayúsculas
    translate([ANCHO / 2, y]) offset(r = TEXTO_GROSOR) scale([ESTRECHAR * REDUCIR, REDUCIR])
        translate([0, -TEXTO_ALTO / 2])   // por la línea base: tildes y cedillas no descolocan el texto
            text(APELLIDO, size = TAM, font = FUENTE, halign = "center", valign = "baseline",
                 spacing = TEXTO_ESPACIADO);
}

// Motivo geométrico de muestra: estrella de ocho puntas de dos cuadrados
// entrelazados, con un anillo y un rombo en el centro.
module estrella(r) { for (a = [0, 45]) rotate(a) square(r * sqrt(2), center = true); }
module motivo_muestra() {
    r = ZONA_MOTIVO / 2 - 0.3;
    difference() { estrella(r); offset(delta = -TRAZO) estrella(r); }
    difference() { circle(r = 5.2); circle(r = 5.2 - TRAZO); }
    rotate(45) square(2.2 * sqrt(2), center = true);
}

module motivo() {
    translate(C_MOTIVO)
        if (MOTIVO_SVG == "") motivo_muestra();
        else sin_hilos(0.8) intersection() {
            circle(d = ZONA_MOTIVO);
            if (MOTIVO_SVG_LADO == "ancho") resize([ZONA_MOTIVO, 0], auto = true) import(MOTIVO_SVG, center = true);
            else resize([0, ZONA_MOTIVO], auto = true) import(MOTIVO_SVG, center = true);
        }
}

module dibujo_relieve() {
    borde();
    apellido();
    motivo();
}

// ---------------------------------------------------------------- 3D

module llavero() {
    difference() {
        union() {
            base_redondeada() contorno();
            relieve() dibujo_relieve();
        }
        orificio(C_AGUJERO);
    }
}

echo(str("Apellido: ", APELLIDO, " · ancho natural ", ancho_natural(APELLIDO), " mm · estrechado ", ESTRECHAR, " · tamaño ", REDUCIR));

PARTE = "todo";   // "todo", "base" o "relieve"
if (PARTE == "todo") llavero();
else if (PARTE == "base") difference() { base_redondeada() contorno(); orificio(C_AGUJERO); }
else if (PARTE == "relieve") relieve() dibujo_relieve();

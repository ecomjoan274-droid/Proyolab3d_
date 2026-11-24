// Protolab3D · Llavero «Pont de Sant Jordi · ALCOI» para Arte23
// 55 × 30 mm · base 3,2 mm + relieve 0,6 mm · orificio pasante de 5 mm
//
// Perfil del puente (Pont de Sant Jordi, Alcoi, 1931, art déco, hormigón armado):
// tablero horizontal sobre cuatro pilas centrales robustas que sostienen tres
// grandes arcos parabólicos iguales, con la clave pegada al tablero y montantes
// verticales entre arco y tablero; sobre las pilas, las torres escalonadas art
// déco que rematan el pretil (llevan las farolas); en los extremos, arcos menores.
// Todo el puente se apoya en una línea de suelo continua que une las pilas:
// el relieve del puente es una sola pieza, sin pilas ni torres sueltas.
//
// Origen en la esquina inferior izquierda; X a lo ancho, Y a lo alto.

include <comun.scad>

/* [Placa] */
ANCHO   = 55;
ALTO    = 30;
R_ESQ   = 4;      // radio de las esquinas
MARCO_IN = 1.0;   // distancia del marco al borde (deja libre el canto redondeado)
MARCO_W  = 1.2;   // ancho del marco en relieve (3 líneas de 0,4)

/* [Orificio] */
C_AGUJERO = [6.6, ALTO / 2];   // 4,1 mm de material hasta el borde (mínimo pedido: 2,5)
SEPARADOR_X = 11.0;            // línea vertical que separa la zona del orificio

/* [Texto] */
TEXTO = "ALCOI";
TEXTO_ALTO = 5.6;        // altura de las mayúsculas
TEXTO_ESPACIADO = 1.18;
TEXTO_Y = 6.2;           // centro vertical del texto

/* [Puente] */
P_X0 = 13.4;  P_X1 = 51.6;        // extremos del puente
SUELO_Y0 = 10.4; SUELO_W = 1.2;   // línea de suelo continua bajo todas las pilas
TABLERO_Y = 20.6; TABLERO_W = 1.8;
PILA_W = 1.9;                     // ancho de las 4 pilas centrales
ESTRIBO_W = 1.4;                  // muros de los extremos
TRAMO_X0 = 18.6; TRAMO_X1 = 46.4; // tramo central de los tres arcos
NERVIO = 1.1;                     // grueso de los arcos
MONTANTE = 0.9;                   // pilares verticales entre arco y tablero
BAJADA_EXT = 2.6;                 // los arcos de los extremos quedan más bajos que los centrales
// torres escalonadas sobre las pilas centrales: [ancho, alto] de cada cuerpo
TORRE = [[2.6, 1.6], [1.8, 1.6], [1.0, 1.4]];

// ---------------------------------------------------------------- 2D

module contorno() {
    translate([R_ESQ, R_ESQ]) offset(r = R_ESQ) square([ANCHO - 2 * R_ESQ, ALTO - 2 * R_ESQ]);
}

module marco() {
    difference() {
        offset(delta = -MARCO_IN) contorno();
        offset(delta = -(MARCO_IN + MARCO_W)) contorno();
    }
    // separador de la zona del orificio
    translate([SEPARADOR_X, MARCO_IN]) square([MARCO_W, ALTO - 2 * MARCO_IN]);
}

function hueco() = (TRAMO_X1 - TRAMO_X0 - 4 * PILA_W) / 3;
function pilas() = [for (i = [0 : 3]) TRAMO_X0 + i * (PILA_W + hueco())];

// Intradós parabólico: hueco bajo un arco de luz 2a con arranque en (xc ± a, y0) y clave en y0 + f
module parabola(xc, a, y0, f, n = 48) {
    polygon(concat(
        [for (i = [0 : n]) let(t = -1 + 2 * i / n) [xc + a * t, y0 + f * (1 - t * t)]],
        [[xc + a, y0 - 0.01], [xc - a, y0 - 0.01]]));
}

module torre() {
    for (i = [0 : len(TORRE) - 1])
        translate([-TORRE[i][0] / 2, sum_altos(i) - 0.01]) square([TORRE[i][0], TORRE[i][1] + 0.02]);
}
function sum_altos(i) = i == 0 ? 0 : TORRE[i - 1][1] + sum_altos(i - 1);

// Un vano: arco parabólico (nervio) entre x0 y x0 + luz, que arranca en el suelo
// y cuya clave queda "bajada" mm por debajo del tablero, con montantes verticales
// (en las posiciones t, de -1 a 1 sobre la luz) que llevan el tablero sobre el arco.
module vano(x0, luz, bajada, t_montantes) {
    y_arr = SUELO_Y0 + SUELO_W;
    a = luz / 2; xc = x0 + a;
    f = TABLERO_Y - bajada - NERVIO - y_arr;
    intersection() {
        translate([x0 - 0.01, SUELO_Y0]) square([luz + 0.02, TABLERO_Y - SUELO_Y0 + 0.01]);
        union() {
            difference() { offset(r = NERVIO) parabola(xc, a, y_arr, f); parabola(xc, a, y_arr, f); }
            for (t = t_montantes) difference() {
                translate([xc + t * a - MONTANTE / 2, y_arr]) square([MONTANTE, TABLERO_Y - y_arr + 0.01]);
                parabola(xc, a, y_arr, f);
            }
        }
    }
}

module puente() {
    // cerrar (rellena rendijas de menos de 0,7 mm) y abrir (quita hilos de menos de 0,8 mm)
    sin_hilos(0.8) offset(r = -0.35) offset(r = 0.35) union() {
        translate([P_X0, SUELO_Y0]) square([P_X1 - P_X0, SUELO_W]);              // suelo
        translate([P_X0, TABLERO_Y]) square([P_X1 - P_X0, TABLERO_W]);           // tablero
        for (x = [P_X0, P_X1 - ESTRIBO_W])                                       // estribos
            translate([x, SUELO_Y0]) square([ESTRIBO_W, TABLERO_Y - SUELO_Y0 + 0.01]);
        for (x = pilas()) translate([x, SUELO_Y0]) square([PILA_W, TABLERO_Y - SUELO_Y0 + 0.01]);
        for (i = [0 : 2]) vano(pilas()[i] + PILA_W, hueco(), 0, [-0.58, 0.58]);  // tres grandes arcos
        vano(P_X0 + ESTRIBO_W, TRAMO_X0 - P_X0 - ESTRIBO_W, BAJADA_EXT, [0]);     // arcos de los extremos
        vano(TRAMO_X1, P_X1 - ESTRIBO_W - TRAMO_X1, BAJADA_EXT, [0]);
    }
    // torres escalonadas art déco sobre las cuatro pilas centrales
    for (x = pilas()) translate([x + PILA_W / 2, TABLERO_Y + TABLERO_W]) torre();
}

module rotulo() {
    translate([(SEPARADOR_X + MARCO_W + ANCHO - MARCO_IN - MARCO_W) / 2, TEXTO_Y])
        resize([0, TEXTO_ALTO], auto = true)
            texto(TEXTO, 10, espaciado = TEXTO_ESPACIADO, grosor = 0);
}

module dibujo_relieve() {
    marco();
    puente();
    rotulo();
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

// PARTE = "todo" (STL de una pieza), "base" o "relieve" (por separado, para asignar filamento)
PARTE = "todo";
if (PARTE == "todo") llavero();
else if (PARTE == "base") difference() { base_redondeada() contorno(); orificio(C_AGUJERO); }
else if (PARTE == "relieve") relieve() dibujo_relieve();
else if (PARTE == "2d") { color("tan") contorno(); color("sienna") translate([0,0,1]) dibujo_relieve(); }

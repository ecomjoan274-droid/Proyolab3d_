// Protolab3D · Llaveros Arte23 · utilidades comunes
// OpenSCAD 2021.01 o posterior. Todas las medidas en mm.
//
// Reglas de impresión que siguen las dos piezas:
//   - base de BASE mm y relieve de RELIEVE mm; todo el relieve empieza en z = BASE,
//     así que basta un único cambio de color en esa altura (capa 17 con capas de 0,20).
//   - orificio pasante de 5 mm con al menos 2,5 mm de material alrededor.
//   - impresión plana, cara de relieve hacia arriba, sin soportes.

BASE      = 3.2;   // grosor de la base (16 capas de 0,20)
RELIEVE   = 0.6;   // altura del relieve (3 capas de 0,20)
R_CANTO   = 0.8;   // radio del redondeo del canto superior de la base
CHAFLAN   = 0.4;   // chaflán a 45° del canto inferior (evita la "pata de elefante")
D_AGUJERO = 5.0;   // diámetro del orificio pasante
CH_AGUJERO = 0.4;  // chaflán a 45° en las dos bocas del orificio
FUENTE    = "Liberation Sans:style=Bold"; // viene con OpenSCAD en Windows, macOS y Linux

$fn = 96;

// Base extruida a partir de un contorno 2D (children(0)), con el canto
// superior redondeado (cuarto de círculo de radio r) y el inferior con un
// chaflán de ch a 45° (sin voladizo: se imprime sin soportes).
// Se hace con la suma de Minkowski de un prisma (el contorno encogido r) y una
// pieza de revolución con ese perfil: las superficies quedan lisas, sin escalones.
module base_redondeada(h = BASE, r = R_CANTO, ch = CHAFLAN) {
    minkowski() {
        linear_extrude(h - ch - r) offset(delta = -r) children(0);
        canto(r, ch);
    }
}
module canto(r = R_CANTO, ch = CHAFLAN, n = 10) {
    rotate_extrude($fn = 48)
        polygon(concat([[0, 0], [r - ch, 0], [r, ch]],
                       [for (i = [1 : n]) let(a = 90 * i / n) [r * cos(a), ch + r * sin(a)]]));
}

// Relieve: extruye el dibujo 2D (children(0)) desde z = BASE hasta BASE + RELIEVE.
module relieve() {
    translate([0, 0, BASE - 0.001]) linear_extrude(RELIEVE + 0.001) children(0);
}

// Orificio pasante con chaflán en las dos bocas (sirve para restar con difference()).
module orificio(c = [0, 0], d = D_AGUJERO, h = BASE + RELIEVE) {
    translate([c[0], c[1], 0]) {
        translate([0, 0, -1]) cylinder(d = d, h = h + 2);
        translate([0, 0, -0.001]) cylinder(d1 = d + 2 * CH_AGUJERO, d2 = d, h = CH_AGUJERO);
        translate([0, 0, BASE - CH_AGUJERO + 0.001]) cylinder(d1 = d, d2 = d + 2 * CH_AGUJERO, h = CH_AGUJERO);
    }
}

// Quita al dibujo 2D las partes más finas que "w" (no se podrían imprimir con boquilla de 0,4).
module sin_hilos(w = 0.8) { offset(r = w / 2) offset(r = -w / 2) children(); }

// Texto centrado con letra gruesa. "grosor" engorda el trazo (mm) para que salga limpio.
module texto(t, alto, espaciado = 1.0, grosor = 0.1, fuente = FUENTE) {
    offset(r = grosor)
        text(t, size = alto, font = fuente, halign = "center", valign = "center", spacing = espaciado);
}

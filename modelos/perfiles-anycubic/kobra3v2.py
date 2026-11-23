"""Ajustes de proyecto para la Anycubic Kobra 3 V2 con boquilla de 0,4 mm y ACE Pro.

Parte de los perfiles oficiales de OrcaSlicer (base de Anycubic Slicer Next),
descargados en esta carpeta desde
https://github.com/SoftFever/OrcaSlicer/tree/main/resources/profiles/Anycubic

  impresora  Anycubic Kobra 3 V2 0.4 nozzle
  proceso    0.20mm Standard @Anycubic Kobra 3 V2 0.4 nozzle
  filamento  Anycubic PLA @Anycubic Kobra 3 V2 0.4 nozzle

Cada perfil se aplana con los que hereda y se juntan en el
Metadata/project_settings.config de un 3MF, que es donde el laminador guarda
la impresora, el proceso y los filamentos de un proyecto.
"""
import json
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
IMPRESORA = "Anycubic Kobra 3 V2 0.4 nozzle"
PROCESO = "0.20mm Standard @Anycubic Kobra 3 V2 0.4 nozzle"
FILAMENTO = "Anycubic PLA @Anycubic Kobra 3 V2 0.4 nozzle"

# Claves que describen el perfil y no son ajustes
_META = {"type", "name", "inherits", "from", "setting_id", "instantiation", "filament_id",
         "compatible_printers", "compatible_printers_condition", "compatible_prints",
         "compatible_prints_condition", "description"}


def _perfil(tipo, nombre):
    """Perfil aplanado: el padre primero y encima lo que cambia cada hijo."""
    cadena = []
    while nombre:
        with open(os.path.join(AQUI, f"{tipo}__{nombre}.json"), encoding="utf-8") as f:
            d = json.load(f)
        cadena.append(d)
        nombre = d.get("inherits")
    plano = {}
    for d in reversed(cadena):
        plano.update({k: v for k, v in d.items() if k not in _META})
    return plano, cadena[0]


def _purga(colores):
    """Volumen de purga (mm³) al pasar de un color a otro: lo claro tras lo oscuro necesita más."""
    def luz(c):
        r, g, b = (int(c[i:i + 2], 16) for i in (1, 3, 5))
        return (0.299 * r + 0.587 * g + 0.114 * b) / 255
    m = []
    for de in colores:
        for a in colores:
            if de == a:
                m.append("0")
            else:
                m.append(str(int(round(180 + 520 * max(0.0, luz(a) - luz(de)) + 120 * abs(luz(a) - luz(de))))))
    return m


def ajustes_proyecto(colores, proceso=None, torre=(200.0, 185.0)):
    """colores: '#RRGGBB' de cada filamento, en el orden del ACE Pro.
    proceso: cambios sobre el perfil de proceso. torre: posición de la torre de purga (mm)."""
    impresora, _ = _perfil("machine", IMPRESORA)
    proc, _ = _perfil("process", PROCESO)
    fil, fil_sistema = _perfil("filament", FILAMENTO)
    cambios = dict(proceso or {})
    proc.update(cambios)

    n = len(colores)
    cfg = {}
    cfg.update(impresora)
    cfg.update(proc)
    for k, v in fil.items():  # los ajustes de filamento van como lista, uno por filamento
        cfg[k] = (v * n) if isinstance(v, list) and len(v) == 1 else v
    cfg.update({
        "name": "project_settings",
        "from": "project",
        "version": "2.0.0.0",
        "printer_settings_id": IMPRESORA,
        "print_settings_id": PROCESO,
        "filament_settings_id": [FILAMENTO] * n,
        "filament_ids": [fil_sistema.get("filament_id", "")] * n,
        "filament_colour": list(colores),
        "inherits": "",
        "inherits_group": [PROCESO] + [FILAMENTO] * n + [IMPRESORA],
        "different_settings_to_system": [";".join(sorted(cambios))] + [""] * n + [""],
        "curr_bed_type": "Textured PEI Plate",
        "flush_multiplier": "1",
        "flush_volumes_matrix": _purga(colores),
        "flush_volumes_vector": ["140"] * (2 * n),
        "wipe_tower_x": [f"{torre[0]:g}"],
        "wipe_tower_y": [f"{torre[1]:g}"],
    })
    return cfg

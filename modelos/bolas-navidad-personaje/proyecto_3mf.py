"""Escribe un proyecto 3MF que Anycubic Slicer Next (basado en OrcaSlicer) abre
con cada pieza ya asignada a su filamento.

El formato sigue lo que escribe y lee el propio laminador
(src/libslic3r/Format/bbs_3mf.cpp): un modelo principal con objetos compuestos,
las mallas en 3D/Objects/*.model y los filamentos en Metadata/model_settings.config.
No se guarda impresora ni perfil: el laminador conserva los que tengas elegidos.
"""
import uuid
import zipfile
from xml.sax.saxutils import quoteattr

APLICACION = "BambuStudio-2.0.0"  # etiqueta con la que el laminador reconoce el proyecto
NS_CORE = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
NS_PROD = "http://schemas.microsoft.com/3dmanufacturing/production/2015/06"
NS_BBL = "http://schemas.bambulab.com/package/2021"
REL_MODELO = "http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"
IDENTIDAD = "1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"

CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
 <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
 <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
 <Default Extension="png" ContentType="image/png"/>
 <Default Extension="gcode" ContentType="text/x.gcode"/>
</Types>
"""


def _uuid(*claves):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "protolab3d/" + "/".join(str(c) for c in claves)))


def _cabecera(principal):
    s = '<?xml version="1.0" encoding="UTF-8"?>\n'
    s += (f'<model unit="millimeter" xml:lang="en-US" xmlns="{NS_CORE}" xmlns:BambuStudio="{NS_BBL}" '
          f'xmlns:p="{NS_PROD}" requiredextensions="p">\n')
    if principal:
        s += f' <metadata name="Application">{APLICACION}</metadata>\n'
    s += ' <metadata name="BambuStudio:3mfVersion">1</metadata>\n'
    return s


def _malla_xml(malla):
    lineas = ["   <mesh>\n    <vertices>\n"]
    for x, y, z in malla.vertices:
        lineas.append(f'     <vertex x="{x:.5f}" y="{y:.5f}" z="{z:.5f}"/>\n')
    lineas.append("    </vertices>\n    <triangles>\n")
    for a, b, c in malla.faces:
        lineas.append(f'     <triangle v1="{a}" v2="{b}" v3="{c}"/>\n')
    lineas.append("    </triangles>\n   </mesh>\n")
    return "".join(lineas)


def escribir_3mf(ruta, objetos):
    """objetos: lista de dicts con
         nombre:   nombre del objeto
         posicion: (x, y) del centro sobre la cama, en mm
         piezas:   lista de (nombre_pieza, malla_trimesh, numero_de_filamento)
    """
    rels_raiz = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                 '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
                 f' <Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="{REL_MODELO}"/>\n'
                 '</Relationships>')

    principal = _cabecera(True) + " <resources>\n"
    construccion = f' <build p:UUID="{_uuid(ruta, "build")}">\n'
    ajustes = '<?xml version="1.0" encoding="UTF-8"?>\n<config>\n'
    rels_modelo = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                   '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n')
    submodelos = {}

    siguiente_id = 1
    for n, obj in enumerate(objetos, start=1):
        ruta_sub = f"3D/Objects/objeto_{n}.model"
        sub = _cabecera(False) + " <resources>\n"
        ids = []
        for nombre_pieza, malla, _ in obj["piezas"]:
            m = malla.copy()
            m.merge_vertices()
            if m.volume < 0:
                m.invert()
            sub += f'  <object id="{siguiente_id}" p:UUID="{_uuid(ruta, n, siguiente_id)}" type="model">\n'
            sub += _malla_xml(m)
            sub += "  </object>\n"
            ids.append(siguiente_id)
            siguiente_id += 1
        sub += " </resources>\n <build/>\n</model>\n"
        submodelos[ruta_sub] = sub

        id_objeto = siguiente_id
        siguiente_id += 1
        principal += f'  <object id="{id_objeto}" p:UUID="{_uuid(ruta, n, "objeto")}" type="model">\n   <components>\n'
        for i in ids:
            principal += (f'    <component p:path="/{ruta_sub}" objectid="{i}" p:UUID="{_uuid(ruta, n, i, "comp")}" '
                          f'transform="1 0 0 0 1 0 0 0 1 0 0 0"/>\n')
        principal += "   </components>\n  </object>\n"

        x, y = obj["posicion"]
        construccion += (f'  <item objectid="{id_objeto}" p:UUID="{_uuid(ruta, n, "item")}" '
                         f'transform="1 0 0 0 1 0 0 0 1 {x:g} {y:g} 0" printable="1"/>\n')

        ajustes += f'  <object id="{id_objeto}">\n'
        ajustes += f'    <metadata key="name" value={quoteattr(obj["nombre"])}/>\n'
        ajustes += '    <metadata key="extruder" value="1"/>\n'
        for i, (nombre_pieza, _, filamento) in zip(ids, obj["piezas"]):
            ajustes += f'    <part id="{i}" subtype="normal_part">\n'
            ajustes += f'      <metadata key="name" value={quoteattr(nombre_pieza)}/>\n'
            ajustes += f'      <metadata key="matrix" value="{IDENTIDAD}"/>\n'
            ajustes += f'      <metadata key="extruder" value="{filamento}"/>\n'
            ajustes += "    </part>\n"
        ajustes += "  </object>\n"

        rels_modelo += f' <Relationship Target="/{ruta_sub}" Id="rel-{n}" Type="{REL_MODELO}"/>\n'

    principal += " </resources>\n" + construccion + " </build>\n</model>\n"
    ajustes += "</config>\n"
    rels_modelo += "</Relationships>"

    with zipfile.ZipFile(ruta, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", CONTENT_TYPES)
        z.writestr("_rels/.rels", rels_raiz)
        z.writestr("3D/3dmodel.model", principal)
        z.writestr("3D/_rels/3dmodel.model.rels", rels_modelo)
        for nombre, contenido in submodelos.items():
            z.writestr(nombre, contenido)
        z.writestr("Metadata/model_settings.config", ajustes)

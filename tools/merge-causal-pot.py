#!/usr/bin/env python3
"""Une la Red Causal 3N (datos/red-causal-3n.xlsx) con la Red POT Kennedy
(datos/red-pot-kennedy-visor.xlsx) en datos/red-causal-3n-ampliada.xlsx.

- Los nodos que estan en las dos redes se fusionan (queda el de la red causal):
  humedales El Burro, La Vaca y Techo, Av. Ciudad de Cali y Corabastos.
- Capas y tipos de relacion del POT se agregan con el prefijo "POT · ".
- Las aristas del POT se reasignan a los nodos fusionados; se omiten duplicadas y autoaristas.

Uso:  python tools/merge-causal-pot.py
      python tools/build-red.py datos/red-causal-3n-ampliada.xlsx red-causal-3n.html
"""
import openpyxl

CAUSAL = 'datos/red-causal-3n.xlsx'
POT = 'datos/red-pot-kennedy-visor.xlsx'
OUT = 'datos/red-causal-3n-ampliada.xlsx'

SAME = {  # nodo POT -> nodo causal equivalente
    'NOD-EEP01': 'N2-HEB',
    'NOD-EEP02': 'N2-HVA',
    'NOD-EEP03': 'N2-HTE',
    'NOD-MOV02': 'N2-AVC',
    'NOD-ECO01': 'N3-COR',
}
PREFIX = 'POT · '


def data_rows(ws):
    return [list(r) for r in ws.iter_rows(min_row=2, values_only=True) if r and r[0]]


def main():
    wb = openpyxl.load_workbook(CAUSAL)
    pot = openpyxl.load_workbook(POT, data_only=True)

    capas, tipos = wb['CAPAS'], wb['INTERACCIONES']
    n_capas = len(data_rows(capas))
    for i, r in enumerate(data_rows(pot['CAPAS'])):
        capas.append(['C%d' % (n_capas + i + 1), PREFIX + r[1], r[2], r[3], r[4], r[5]])
    n_tipos = len(data_rows(tipos))
    for i, r in enumerate(data_rows(pot['INTERACCIONES'])):
        tipos.append(['T%02d' % (n_tipos + i + 1), PREFIX + r[1], r[2], r[3], r[4]])

    nodos = wb['NODOS']
    added_nodes = 0
    for r in data_rows(pot['NODOS']):
        if r[0] in SAME:
            continue
        r = (r + [None] * 18)[:18]
        r[2] = PREFIX + r[2]
        nodos.append(r)
        added_nodes += 1

    aristas = wb['ARISTAS']
    seen = set()
    for r in data_rows(aristas):
        seen.add(tuple(sorted((r[1], r[2]))))
    added_edges = skipped = 0
    for r in data_rows(pot['ARISTAS']):
        a, b = SAME.get(r[1], r[1]), SAME.get(r[2], r[2])
        key = tuple(sorted((a, b)))
        if a == b or key in seen:
            skipped += 1
            continue
        seen.add(key)
        r = (r + [None] * 12)[:12]
        r[0], r[1], r[2], r[3] = 'POT-' + str(r[0]), a, b, PREFIX + r[3]
        aristas.append(r)
        added_edges += 1

    red = wb['RED']
    for row in red.iter_rows(min_row=2):
        if row[0].value == 'titulo':
            row[1].value = 'Red Causal de Problemas — Kennedy (3 Niveles + POT)'
        elif row[0].value == 'marca':
            row[1].value = 'RED CAUSAL · 3 NIVELES + POT'
        elif row[0].value == 'capa_clave':
            row[1].value = 'Estructura ecologica'

    consolidar(wb)
    if 'CONTROL' in wb.sheetnames:
        del wb['CONTROL']
    wb.save(OUT)
    print('OK: +%d nodos, +%d aristas (omitidas %d duplicadas/autoaristas), 4 capas y 4 tipos -> %s'
          % (added_nodes, added_edges, skipped, OUT))


# --- 4 convenciones de capa y 4 tipos de relacion (paleta de marca) ---------------------------
CAPAS4 = [
    ['C1', 'Estructura ecologica', 'Humedales, rondas, fauna, flora, agua, residuos y presiones ambientales', '#8A3FFC', 'fa-leaf', 'ECOLOGIA'],
    ['C2', 'Movilidad y logistica', 'Corredores de carga, vias, transporte publico, tractomulas e invasion de calzadas', '#DBF343', 'fa-route', 'MOVILIDAD'],
    ['C3', 'Economia, usos y barrios', 'Corabastos, economia popular, comercio, usos del suelo, vivienda y barrios', '#F2F2F2', 'fa-city', 'ECONOMIA'],
    ['C4', 'Planeacion, actores e indicadores', 'Actuaciones del POT, normas, entidades, comunidad organizada e indicadores', '#B7ABDB', 'fa-scale-balanced', 'PLANEACION'],
]
TIPOS4 = [
    ['R1', 'Causa y presion', 'Un nodo produce, agrava, presiona o fragmenta a otro.', '#DBF343', 'fa-arrow-up'],
    ['R2', 'Sostiene y conecta', 'Un nodo sostiene, articula o encadena a otro (ecologica, funcional o economicamente).', '#8A3FFC', 'fa-hand-holding-heart'],
    ['R3', 'Mide y gestiona', 'Un indicador lo mide, o una entidad o actor lo gestiona y regula.', '#B7ABDB', 'fa-scale-balanced'],
    ['R4', 'Comparten territorio', 'Se manifiesta en el mismo lugar o los nodos estan a menos de 600 m.', '#6E6680', 'fa-location-dot'],
]
# capa original -> convencion (por nombre de capa); algunos nodos se ajustan uno a uno
CAPA_MAP = {
    'NIVEL 2 · Efectos ecologicos y metabolicos': 'C1',
    'NIVEL 2 · Efectos comunitarios y economia popular': 'C3',
    'NIVEL 3 · Causa estructural': 'C3',
    'INDICADORES · Diez medidores': 'C4',
    PREFIX + 'Estructura ecológica': 'C1',
    PREFIX + 'Aspectos poco atendidos': 'C1',
    PREFIX + 'Movilidad e infraestructura': 'C2',
    PREFIX + 'Actividad económica': 'C3',
    PREFIX + 'Usos del suelo (POT)': 'C3',
    PREFIX + 'Actuaciones Estratégicas (AE)': 'C4',
    PREFIX + 'Condicionantes normativos': 'C4',
    PREFIX + 'Actores clave': 'C4',
}
NODO_MAP = {
    'N1-MPAZ': 'C3', 'N1-PBON': 'C3', 'N1-EAMP': 'C3', 'N1-RES': 'C1', 'N1-INV': 'C2', 'N1-TRAC': 'C2',
    'N2-AVC': 'C2', 'N2-KR80': 'C2', 'N3-FRA': 'C4', 'NOD-ECO05': 'C2', 'NOD-EEP06': 'C1',
}
TIPO_MAP = {
    'Causa directa (asciende de nivel)': 'R1', 'Presiona / agrava': 'R1', 'Fragmenta': 'R1',
    'Mide a': 'R3', 'Sostiene / alimenta': 'R2', 'Se manifiesta en': 'R4',
    PREFIX + 'Articulación funcional': 'R2', PREFIX + 'Presión ecológica': 'R1',
    PREFIX + 'Fragmentación y barrera': 'R1', PREFIX + 'Encadenamiento económico y plusvalía': 'R2',
    PREFIX + 'Presión socioeconómica y desplazamiento': 'R1', PREFIX + 'Soporte ecosistémico y cuidado': 'R2',
    PREFIX + 'Gestión e intervención institucional': 'R3', PREFIX + 'Gobernanza y participación': 'R3',
    PREFIX + 'Comparten territorio (menos de 600 m)': 'R4', PREFIX + 'Comparten entidad responsable': 'R3',
}


def reset_sheet(ws, rows_):
    ws.delete_rows(2, ws.max_row)
    for r in rows_:
        ws.append(r)


def consolidar(wb):
    capa_name = {c[0]: c[1] for c in CAPAS4}
    tipo_name = {t[0]: t[1] for t in TIPOS4}
    old_icon = {r[1]: r[4] for r in data_rows(wb['CAPAS'])}
    for row in wb['NODOS'].iter_rows(min_row=2):
        if not row[0].value:
            continue
        old = row[2].value
        code = NODO_MAP.get(row[0].value) or CAPA_MAP.get(old)
        if not code:
            raise SystemExit('Capa sin convencion: %s (%s)' % (old, row[0].value))
        if not row[17].value:          # conserva el icono de su capa original
            row[17].value = old_icon.get(old)
        row[2].value = capa_name[code]
    for row in wb['ARISTAS'].iter_rows(min_row=2):
        if not row[0].value:
            continue
        old = row[3].value
        code = TIPO_MAP.get(old)
        if not code:
            raise SystemExit('Tipo sin convencion: %s (%s)' % (old, row[0].value))
        orig = old.replace(PREFIX, '')
        row[4].value = orig + (': ' + row[4].value if row[4].value else '')   # el tipo original queda en el detalle
        row[3].value = tipo_name[code]
    reset_sheet(wb['CAPAS'], CAPAS4)
    reset_sheet(wb['INTERACCIONES'], TIPOS4)


if __name__ == '__main__':
    main()

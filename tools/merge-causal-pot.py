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

    if 'CONTROL' in wb.sheetnames:
        del wb['CONTROL']
    wb.save(OUT)
    print('OK: +%d nodos, +%d aristas (omitidas %d duplicadas/autoaristas) -> %s'
          % (added_nodes, added_edges, skipped, OUT))


if __name__ == '__main__':
    main()

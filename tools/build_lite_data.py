"""Genera versiones compactas de las capas del territorio para index.html.
No modifica los JSON originales (los usan otros modulos).
  assets/lite/buildings.json     -> todos los edificios (desktop), identico visualmente
  assets/lite/buildings_m.json   -> 1 de cada 4 edificios, sin vertice de cierre (celular)
  assets/lite/trees.json         -> arboles SIGAU agrupados por nombre
Formato edificios: lista plana [h*10, n, dx, dy, dx, dy, ...] con coordenadas *10 en delta
(el delta continua de un edificio al siguiente)."""
import json, os
os.makedirs('assets/lite', exist_ok=True)
b = json.load(open('assets/kennedy_buildings.json'))
def enc(stride, mobile):
    flat = []; px = py = 0
    for i, e in enumerate(b):
        if i % stride: continue
        pts = e.get('pts') or []
        if mobile:
            if len(pts) < 3: continue
            if len(pts) > 3 and pts[0] == pts[-1]: pts = pts[:-1]
        h = e.get('height') or e.get('h') or 12.0
        flat += [round(h * 10), len(pts)]
        for x, y in pts:
            X, Y = round(x * 10), round(y * 10)
            flat += [X - px, Y - py]; px, py = X, Y
    return flat
for name, st, mob in [('buildings.json', 1, False), ('buildings_m.json', 4, True)]:
    json.dump(enc(st, mob), open('assets/lite/' + name, 'w'), separators=(',', ':'))
t = json.load(open('assets/kennedy_trees_real.json'))
t = t if isinstance(t, list) else t.get('trees', [])
names = []; nidx = {}; flat = []; px = py = 0
for tr in t:
    x, y, h, name = tr[0], tr[1], tr[2], tr[3] if len(tr) > 3 else None
    if not name: continue
    if name not in nidx: nidx[name] = len(names); names.append(name)
    X, Y = round(x * 10), round(y * 10)
    flat += [nidx[name], X - px, Y - py, round((h or 0) * 10)]; px, py = X, Y
json.dump({'n': names, 'd': flat}, open('assets/lite/trees.json', 'w'), separators=(',', ':'), ensure_ascii=False)

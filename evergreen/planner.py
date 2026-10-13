"""Small, dependency-free route and inventory planner. Demo data is illustrative."""
import csv
import heapq
import math
from pathlib import Path

ROOT = Path(__file__).parent


def load_data(directory=ROOT / 'data'):
    def read(name):
        with (Path(directory) / f'{name}.csv').open(encoding='utf-8-sig', newline='') as f:
            return list(csv.DictReader(f))
    buildings, rooms, links, inventory = [read(n) for n in ('buildings', 'rooms', 'links', 'inventory')]
    def unique(rows, key):
        ids = [r[key] for r in rows]
        if len(ids) != len(set(ids)) or any(not x for x in ids):
            raise ValueError(f'Identifiants {key} vides ou en double')
    unique(buildings, 'id'); unique(rooms, 'id'); unique(links, 'id')
    bids = {b['id'] for b in buildings}; rids = {r['id'] for r in rooms}
    for b in buildings:
        for k in ('x', 'y'):
            b[k] = float(b[k])
            if not math.isfinite(b[k]): raise ValueError('Coordonnée invalide')
        if not b['target_model']: raise ValueError('Modèle cible manquant')
    for r in rooms:
        if r['building'] not in bids: raise ValueError('Bâtiment inconnu')
        r['floor'] = int(r['floor']); r['capacity'] = int(r['capacity']); r['corridor_m'] = float(r['corridor_m'])
        if r['capacity'] < 0 or not math.isfinite(r['corridor_m']) or r['corridor_m'] < 0: raise ValueError('Salle invalide')
    for e in links:
        e['meters'] = float(e['meters']); e['fixed_seconds'] = float(e['fixed_seconds'])
        if e['kind'] not in ('walk', 'elevator', 'stairs'): raise ValueError('Type de liaison inconnu')
        if e['accessible'] not in ('0', '1') or e['enabled'] not in ('0', '1'): raise ValueError('Utiliser 0 ou 1 pour accessibilité/disponibilité')
        if any(not math.isfinite(e[k]) or e[k] < 0 for k in ('meters', 'fixed_seconds')): raise ValueError('Coût de liaison invalide')
    seen = set(); counts = {r: 0 for r in rids}
    for i in inventory:
        if i['room'] not in rids or not i['model']: raise ValueError('Inventaire invalide')
        pair = (i['room'], i['model'])
        if pair in seen: raise ValueError('Ligne salle/modèle en double')
        seen.add(pair); i['quantity'] = int(i['quantity'])
        if i['quantity'] < 0: raise ValueError('Quantité négative')
        counts[i['room']] += i['quantity']
    for r in rooms:
        if counts[r['id']] > r['capacity']: raise ValueError(f"Capacité dépassée : {r['id']}")
    # Landing IDs are explicit; classroom digits are never used to infer floors.
    nodes = rids | {f"{r['building']}:F{r['floor']}" for r in rooms} | {f'{b}:F0' for b in bids}
    for e in links:
        if e['source'] not in nodes or e['target'] not in nodes: raise ValueError(f"Nœud inconnu : {e['id']}")
    return dict(buildings=buildings, rooms=rooms, links=links, inventory=inventory)


def graph(data, accessible=True, speed=0.8, wait=1.0):
    if not 0.1 <= speed <= 3 or not 0 <= wait <= 5: raise ValueError('Paramètres de déplacement invalides')
    g = {}
    def add(a, b, meters, seconds, kind, label):
        edge = dict(source=a, target=b, meters=meters, seconds=seconds, kind=kind, label=label)
        g.setdefault(a, []).append(edge)
        g.setdefault(b, []).append({**edge, 'source': b, 'target': a})
    for r in data['rooms']:
        add(r['id'], f"{r['building']}:F{r['floor']}", r['corridor_m'], r['corridor_m']/speed, 'walk', 'Couloir')
    for e in data['links']:
        if e['enabled'] != '1' or (accessible and e['accessible'] != '1'): continue
        seconds = e['meters']/speed + e['fixed_seconds'] * (wait if e['kind'] == 'elevator' else 1)
        add(e['source'], e['target'], e['meters'], seconds, e['kind'], e['label'])
    return g


def route(g, source, target, metric='seconds'):
    if metric not in ('seconds', 'meters'): raise ValueError('Critère inconnu')
    if source not in g or target not in g: raise ValueError('Salle inconnue')
    heap = [(0, source)]; dist = {source: 0}; prev = {}
    while heap:
        cost, u = heapq.heappop(heap)
        if cost != dist[u]: continue
        if u == target: break
        for e in g[u]:
            v = e['target']; value = cost + e[metric]
            if value < dist.get(v, math.inf):
                dist[v] = value; prev[v] = e; heapq.heappush(heap, (value, v))
    if target not in dist: return None
    steps = []; v = target
    while v != source:
        e = prev[v]; steps.append(e); v = e['source']
    steps.reverse()
    return dict(source=source, target=target, steps=steps, meters=sum(e['meters'] for e in steps), seconds=sum(e['seconds'] for e in steps))


def allocate(supply, demand, costs):
    """Integral minimum-cost maximum flow, including residual reassignment."""
    n = 2 + len(supply) + len(demand); sink = n-1; adj = [[] for _ in range(n)]
    def edge(u, v, cap, cost):
        a = [v, len(adj[v]), cap, cost]; b = [u, len(adj[u]), 0, -cost]
        adj[u].append(a); adj[v].append(b)
        return a
    for i, (_, qty) in enumerate(supply): edge(0, i+1, qty, 0)
    for j, (_, qty) in enumerate(demand): edge(1+len(supply)+j, sink, qty, 0)
    refs = []
    for i, (s, qty) in enumerate(supply):
        for j, (t, _) in enumerate(demand):
            if (s, t) in costs:
                e = edge(i+1, 1+len(supply)+j, qty, costs[s, t]); refs.append((s, t, qty, e))
    while True:
        dist = [math.inf]*n; dist[0] = 0; prev = [None]*n
        for _ in range(n-1):
            changed = False
            for u in range(n):
                if dist[u] == math.inf: continue
                for k, e in enumerate(adj[u]):
                    if e[2] > 0 and dist[u]+e[3] < dist[e[0]]-1e-9:
                        dist[e[0]] = dist[u]+e[3]; prev[e[0]] = (u, k); changed = True
            if not changed: break
        if prev[sink] is None: break
        qty = math.inf; v = sink
        while v:
            u, k = prev[v]; qty = min(qty, adj[u][k][2]); v = u
        v = sink
        while v:
            u, k = prev[v]; e = adj[u][k]; e[2] -= qty; adj[v][e[1]][2] += qty; v = u
    return [(s, t, qty-e[2]) for s, t, qty, e in refs if qty-e[2] > 0]


def plan(data, g, metric='seconds', cart=2, handling=120):
    if metric not in ('seconds', 'meters') or cart < 1 or not math.isfinite(handling) or handling < 0: raise ValueError('Paramètres invalides')
    targets = {b['id']: b['target_model'] for b in data['buildings']}
    models = sorted({i['model'] for i in data['inventory']} | set(targets.values()))
    assignments = []; moves = []; warnings = []; retained = 0
    for model in models:
        supply = [(i['room'], i['quantity']) for i in data['inventory'] if i['model'] == model and i['quantity']]
        demand = [(r['id'], r['capacity']) for r in data['rooms'] if targets[r['building']] == model and r['capacity']]
        paths = {}; costs = {}
        for s, _ in supply:
            for t, _ in demand:
                p = route(g, s, t, metric)
                if p is not None: paths[s, t] = p; costs[s, t] = p[metric]
        assigned = allocate(supply, demand, costs)
        for s, t, qty in assigned:
            assignments.append(dict(model=model, source=s, target=t, quantity=qty))
            if s == t: retained += qty; continue
            p = paths[s, t]; trips = math.ceil(qty/cart)
            # Each batch has an outward loaded leg and a return leg. Handling is per PC.
            moves.append(dict(model=model, source=s, target=t, quantity=qty, trips=trips, route=p,
                              estimated_seconds=2*trips*p['seconds'] + qty*handling))
        used = sum(q for _, _, q in assigned)
        if used < sum(q for _, q in supply): warnings.append(f'{model} : {sum(q for _,q in supply)-used} PC non affecté(s), à conserver dans leur salle ou à prévoir en stockage temporaire.')
        if used < sum(q for _, q in demand): warnings.append(f'{model} : {sum(q for _,q in demand)-used} emplacement(s) cible non rempli(s), stock insuffisant ou trajet indisponible.')
    return dict(assignments=assignments, moves=moves, warnings=warnings, retained=retained,
                moved=sum(m['quantity'] for m in moves), estimated_seconds=sum(m['estimated_seconds'] for m in moves))

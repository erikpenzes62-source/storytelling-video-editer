"""Wort-Zeitstempel -> Untertitel-Chunks (Korrekturen, Aufteilung, Keywords).

Aufruf:  python3 tools/captions.py words.json fixes.json chunks.json [max_words] [max_chars]

fixes.json (optional, darf {} sein):
  {"fix": {"12": "High Ticket", "13": null}, "keys": ["business", "skill"]}
  - fix:  Wort-Index -> neuer Text (null = Wort löschen und an das vorige anhängen)
  - keys: Wörter, die farbig hervorgehoben werden (max. eine Gruppe pro Chunk)
"""
import json, re, sys

def _n(s): return re.sub(r'[^\w€%„“]', '', s.lower())

def build(words, fix, keys, max_words=4, max_chars=20):
    toks = []
    for i, x in enumerate(words):
        t = x['w'].strip()
        if i in fix:
            if fix[i] is None:
                if toks: toks[-1]['e'] = x['e']
                continue
            t = fix[i]
        toks.append({'i': i, 't': t, 's': x['s'], 'e': x['e']})
    keys = set(_n(k) for k in keys)
    chunks, cur = [], []
    for j, t in enumerate(toks):
        cur.append(t)
        nxt = toks[j + 1] if j + 1 < len(toks) else None
        chars = sum(len(x['t']) + 1 for x in cur)
        end_punct = bool(re.search(r'[.,!?…:]$', t['t']))
        gap = (nxt['s'] - t['e']) if nxt else 9
        if (nxt is None or len(cur) >= max_words or chars >= max_chars or gap > 0.45
                or (end_punct and len(cur) >= 2) or (end_punct and t['t'][-1] in '.!?:')):
            chunks.append(cur); cur = []
    if cur: chunks.append(cur)
    merged = []
    for c in chunks:   # Ein-Wort-Reste an den vorigen Chunk hängen
        if merged and len(c) == 1 and sum(len(x['t']) + 1 for x in merged[-1] + c) <= 30 and c[0]['s'] - merged[-1][-1]['e'] < 0.5:
            merged[-1] = merged[-1] + c
        else:
            merged.append(c)
    for c in merged:   # max. eine Keyword-Gruppe pro Chunk
        for x in c: x['k'] = False
        hit = [n for n, x in enumerate(c) if _n(x['t']) in keys]
        if hit:
            a = b = hit[0]
            while b + 1 < len(c) and _n(c[b + 1]['t']) in keys and b + 1 - a < 2: b += 1
            for n in range(a, b + 1): c[n]['k'] = True
    return merged

if __name__ == '__main__':
    words = json.load(open(sys.argv[1]))
    fx = json.load(open(sys.argv[2])) if len(sys.argv) > 2 and sys.argv[2] != '-' else {}
    fix = {int(k): v for k, v in fx.get('fix', {}).items()}
    mw = int(sys.argv[4]) if len(sys.argv) > 4 else 4
    mc = int(sys.argv[5]) if len(sys.argv) > 5 else 20
    ch = build(words, fix, fx.get('keys', []), mw, mc)
    json.dump(ch, open(sys.argv[3], 'w'), ensure_ascii=False, indent=0)
    for c in ch:
        print(f"{c[0]['s']:7.2f}  " + ' '.join(('[' + x['t'] + ']') if x['k'] else x['t'] for x in c))

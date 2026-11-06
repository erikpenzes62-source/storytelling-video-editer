"""Schnittliste (edl in project.json) prüfen und in cut.json umwandeln.

edl-Format:  [[startzeit_im_video, clip_id, einstiegspunkt_im_clip], ...]
  z. B. [0, 72, 2.0] = ab Sekunde 0 läuft Clip 72, ab dessen Sekunde 2.0
Optional 4. Wert: Zeitlupenfaktor (0.5 = halbe Geschwindigkeit).

Aufruf:  python3 tools/cutlist.py projects/NAME
"""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

p = C.load(sys.argv[1])
info = json.load(open(os.path.join(C.data_dir(), 'clipinfo.json')))
br = json.load(open(os.path.join(C.data_dir(), 'bright.json')))
byid = {v['id']: (k, v) for k, v in info.items()}
ban = set(p.get('ban_clips', []))
e = p['edl']; TE = p['dur']; out = []; ok = True; line = []
for j, row in enumerate(e):
    t0, cid, inp = row[0], row[1], row[2]; sp = row[3] if len(row) > 3 else 1.0
    t1 = e[j + 1][0] if j + 1 < len(e) else TE
    if cid not in byid:
        print(f'FEHLER: Clip-ID {cid} (bei {t0}s) gibt es nicht in clipinfo.json'); ok = False; continue
    k, v = byid[cid]
    if cid in ban: print(f'WARNUNG: Clip {cid} ({k}) steht auf der Sperrliste')
    if v['w'] > v['h']: print(f'WARNUNG: Clip {cid} ist Querformat – wird beschnitten')
    n = round(t1 * C.FPS) - round(t0 * C.FPS)
    need = inp + (t1 - t0) * sp
    if need > v['dur'] - 0.05:
        print(f'FEHLER: Clip {cid} bei {t0}s ist zu kurz: braucht bis {need:.2f}s, hat nur {v["dur"]}s'); ok = False
    if t1 - t0 < 0.6: print(f'HINWEIS: sehr kurzer Schnitt bei {t0}s ({t1 - t0:.2f}s)')
    s = br.get(str(cid), {})
    b = s.get(str(min(5, int(6 * (inp + (t1 - t0) / 2) / max(v['dur'], 0.1)))), 0)
    line.append(f'{t0:.0f}s:#{cid}(hell {b:.0f})')
    out.append({'id': cid, 'file': k, 'in': inp, 'n': n, 'hlg': v['transfer'] == 'arib-std-b67', 'sp': sp})
ids = [r[1] for r in e]; dup = sorted({i for i in ids if ids.count(i) > 1})
if dup: print('HINWEIS: Clips doppelt verwendet:', dup)
print('Helligkeitsverlauf:', ' '.join(line))
tot = sum(c['n'] for c in out)
print(f'{len(out)} Schnitte, {tot} Frames = {tot / C.FPS:.2f}s (Soll {TE}s)')
if not ok: raise SystemExit('Schnittliste hat Fehler – bitte edl in project.json korrigieren.')
json.dump(out, open(C.path(p, 'cut.json'), 'w'), ensure_ascii=False, indent=0)
print('-> cut.json geschrieben')

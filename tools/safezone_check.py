"""Prüft VOR dem Rendern, ob Untertitel/Einblendungen in der TikTok-Safe-Zone bleiben.

Gesperrt (1080x1920): oben y<220, unten y>1545, Ränder x<45 / x>1035,
rechte Spalte x>900 für y 970-1545 (Profilbild, Likes, Kommentare, Teilen).
Aufruf:  python3 tools/safezone_check.py projects/NAME   -> zeigt Verstöße + safezone.jpg (Testbilder jeder Einblendung)
"""
import sys, json, os
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
import overlay as O

p = C.load(sys.argv[1]); W, H = C.W, C.H
caps = O.Captions(C.path(p, 'chunks.json'), p['style'])
objs = []
for ins in p.get('inserts', []):
    d = dict(ins); k = d.pop('kind'); objs.append((k, ins, getattr(O, k)(**d)))
hide = [tuple(x) for x in p.get('hide_caps', [])]; bad = []; t = 0.0
while t < p['dur']:
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    act = [k for k, ins, o in objs if o.on(t)]
    for k, ins, o in objs: o.draw(im, t)
    if not any(a <= t < b for a, b in hide): caps.draw(im, t)
    a = im.split()[3].point(lambda v: 255 if v > 90 else 0); bb = a.getbbox()
    if bb:
        x0, y0, x1, y1 = bb; probs = []
        if y0 < 220: probs.append('oben')
        if y1 > 1545: probs.append('unten')
        if x0 < 45 or x1 > 1035: probs.append('Rand')
        if a.crop((900, 970, 1080, 1545)).getbbox(): probs.append('rechte Spalte')
        if probs: bad.append((round(t, 2), act, probs))
    t += 0.1
shots = []
for k, ins, o in objs:
    tt = min(ins['t1'] - 0.05, max([ins['t0'] + 0.6] + [v for kk, v in ins.items() if kk in ('t_end', 'strike', 'punch') and isinstance(v, (int, float))]) + 0.35)
    bg = Image.new('RGBA', (W, H), (70, 80, 90, 255)); o.draw(bg, tt)
    if not any(a <= tt < b for a, b in hide): caps.draw(bg, tt)
    d = ImageDraw.Draw(bg); d.rectangle([45, 220, 1035, 1545], outline=(255, 0, 0, 255), width=4)
    d.rectangle([900, 970, 1035, 1545], outline=(255, 0, 0, 255), width=4)
    shots.append(bg.convert('RGB').resize((270, 480)))
if shots:
    S = Image.new('RGB', (270 * len(shots), 480)); [S.paste(s, (i * 270, 0)) for i, s in enumerate(shots)]
    S.save(C.path(p, 'safezone.jpg'), quality=80)
print('Safe-Zone-Verstöße:', len(bad))
for x in bad[:20]: print('  ', x)
if bad: print('-> Einblendung kleiner machen (size), y-Position ändern oder Untertitel währenddessen ausblenden (hide_caps).')

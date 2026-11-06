"""Untertitel + Einblendungen auf das Basisvideo rendern (60 fps), Frames [k0, k1).

Aufruf:  python3 tools/render.py projects/NAME k0 k1 ausgabe.mp4
Normalerweise nicht direkt aufrufen, sondern:  bash tools/render_all.sh projects/NAME
"""
import sys, json, subprocess, os
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
import overlay as O

p = C.load(sys.argv[1]); k0, k1 = int(sys.argv[2]), int(sys.argv[3]); out = sys.argv[4]
W, H, FPS = C.W, C.H, C.FPS
caps = O.Captions(C.path(p, 'chunks.json'), p['style'])
objs = []
for ins in p.get('inserts', []):
    ins = dict(ins); kind = ins.pop('kind'); objs.append(getattr(O, kind)(**ins))
hook = O.Hook(**p.get('hook', {'end': 0.1, 'impacts': [], 'cuts': [], 'zoom': 0.0}))
hide = [tuple(x) for x in p.get('hide_caps', [])]
reader = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', f'{k0 / FPS:.6f}', '-i', C.path(p, 'base.mp4'),
    '-vf', f'scale={W}:{H}', *C.passthrough_flag(), '-f', 'rawvideo', '-pix_fmt', 'rgba', '-'], stdout=subprocess.PIPE)
writer = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{W}x{H}', '-r', str(FPS),
    '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', '-threads', '1', out + '.tmp.mp4'],
    stdin=subprocess.PIPE)
last = None
for k in range(k0, k1):
    buf = reader.stdout.read(W * H * 4)
    if len(buf) < W * H * 4:
        buf = last
        if buf is None: break
    last = buf; t = k / FPS
    im = Image.frombuffer('RGBA', (W, H), buf, 'raw', 'RGBA', 0, 1).copy()
    im = hook.frame(im, t)
    for o in objs: o.draw(im, t)
    if not any(a <= t < b for a, b in hide): caps.draw(im, t)
    writer.stdin.write(im.tobytes())
writer.stdin.close(); writer.wait(); reader.kill()
os.replace(out + '.tmp.mp4', out); print('ok', out)

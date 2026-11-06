"""Alle Schnitte aus cut.json als 1080x1920 / 60 fps-Segmente schneiden.

Aufruf:  python3 tools/cut_segments.py projects/NAME [teil anzahl_teile]
  Ohne Teil-Angabe: alles nacheinander. Zum Beschleunigen 3x parallel starten:
    python3 tools/cut_segments.py P 0 3 & python3 tools/cut_segments.py P 1 3 & python3 tools/cut_segments.py P 2 3 & wait
Schon fertige Segmente werden übersprungen -> nach einem Abbruch einfach neu starten.
iPhone-HDR (HLG) wird automatisch auf normales SDR umgerechnet.
"""
import json, subprocess, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

p = C.load(sys.argv[1]); src = C.clips_dir()
part, nparts = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (0, 1)
cl = json.load(open(C.path(p, 'cut.json'))); sd = C.path(p, 'segs'); os.makedirs(sd, exist_ok=True)
TM = "zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=mobius:desat=0:param=0.35,zscale=t=bt709:m=bt709:r=tv,"
common = ['-an', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', '-threads', '1',
          '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709']
for k, c in enumerate(cl):
    if k % nparts != part: continue
    o = os.path.join(sd, f's{k:03d}.mp4')
    if os.path.exists(o) and os.path.getsize(o) > 1000: continue
    vf = f"scale={C.W}:{C.H}:force_original_aspect_ratio=increase:flags=bicubic,crop={C.W}:{C.H},"
    if c.get('hlg'): vf += TM
    if c.get('sp', 1.0) != 1.0: vf += f"setpts=PTS/{c['sp']},"
    vf += f"fps={C.FPS},setsar=1,format=yuv420p"
    dur_src = c['n'] / C.FPS * c.get('sp', 1.0) + 0.15
    cmd = ['ffmpeg', '-v', 'error', '-y', '-ss', str(c['in']), '-t', f'{dur_src:.3f}', '-i', os.path.join(src, c['file']),
           '-vf', vf, '-frames:v', str(c['n']), *common, o + '.tmp.mp4']
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode == 0:
        os.replace(o + '.tmp.mp4', o); print('ok', k, c['file'], flush=True)
    else:
        print('FEHLER', k, c['file'], r.stderr[-400:], flush=True)

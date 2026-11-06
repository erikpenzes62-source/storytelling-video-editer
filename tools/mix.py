"""Ton: Stimme + Soundeffekte mischen und für TikTok mastern (ca. -14 LUFS, True Peak <= -1 dBTP).

cues in project.json:  [[zeitpunkt_s, "soundname", lautstärke_dB], ...]
  soundname = Dateiname ohne .wav im Ordner sounds/ (bzw. SFX_DIR)
Aufruf:  python3 tools/mix.py projects/NAME
"""
import json, subprocess, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

p = C.load(sys.argv[1]); D = p['dur']
ins = ['-ss', str(p.get('voice_ss', 0)), '-t', str(D), '-i', C.path(p, p['voice'])]; fl = []
for j, (tc, n, db) in enumerate(p.get('cues', [])):
    f = os.path.join(C.sfx_dir(), n + '.wav')
    if not os.path.exists(f): raise SystemExit(f'FEHLER: Sound fehlt: {f}  (bash tools/render_sounds.sh ausführen?)')
    ins += ['-i', f]; ms = int(tc * 1000)
    fl.append(f'[{j+1}:a]aformat=sample_rates=48000:channel_layouts=stereo,adelay={ms}|{ms},volume={db}dB,apad[s{j}]')
N = len(p.get('cues', [])) + 1
voice_gain = p.get('voice_gain', 1.0)
mix = f'[0:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={voice_gain}[v];' + ''.join(x + ';' for x in fl) + \
      '[v]' + ''.join(f'[s{j}]' for j in range(N - 1)) + \
      f'amix=inputs={N}:duration=first:dropout_transition=0,volume={N},atrim=0:{D},' \
      'aresample=192000,alimiter=limit=0.70:level=false,aresample=48000,' \
      'loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.84:level=false,aresample=48000[a]'
subprocess.run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', mix, '-map', '[a]', '-c:a', 'aac', '-b:a', '192k',
                C.path(p, 'audio_mix.m4a')], check=True)
r = subprocess.run(['ffmpeg', '-nostats', '-i', C.path(p, 'audio_mix.m4a'), '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                   capture_output=True, text=True).stderr
I = [l for l in r.splitlines() if ' I:' in l][-1:]; P = [l for l in r.splitlines() if 'Peak:' in l][-1:]
print('-> audio_mix.m4a  |', (I + P), '(Ziel: I ca. -14 LUFS, Peak unter -1)')

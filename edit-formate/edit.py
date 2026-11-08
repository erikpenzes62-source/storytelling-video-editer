#!/usr/bin/env python3
"""Edit-Formate: Grundvideo (Gespräch) + Musik-Drop + Beat-Edit aus Clips.

Aufruf:   python3 edit-formate/edit.py projekte/NAME/edit.json
Ergebnis: das MP4, das in "out" steht (Standard: <Projektordner>/<name>.mp4)

Alle Pfade in der JSON sind relativ zum Ordner der JSON-Datei (oder absolut).
Aufbau der JSON: siehe edit-formate/docs/EDIT_JSON.md
"""
import json, os, subprocess, sys, shutil
import numpy as np

try:
    import soundfile as sf, pyloudnorm as pyln
    import scipy.signal as ss
    from PIL import ImageFont
except ImportError as e:
    sys.exit(f"FEHLER: Python-Paket fehlt ({e.name}). Erst  source .venv/bin/activate  und  pip install -r requirements.txt")

FPS, SR, VW, VH = 30, 48000, 1080, 608          # Video 16:9 (1080x608) mittig in 1080x1920
TOP = 656                                         # y-Position des Videos im 9:16-Bild
HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.abspath(os.path.join(HERE, '..', 'tools', 'fonts'))

GRADE = {   # Look des Edit-Teils (Gespräch bleibt natürlich)
    'cine':  "eq=contrast=1.14:brightness=-0.045:saturation=0.82,colorbalance=rs=-0.06:bs=0.07:rh=0.07:gh=0.02:bh=-0.06",
    'chaos': "eq=contrast=1.10:saturation=1.18",
    'vivid': "eq=contrast=1.06:saturation=1.15",
    'doku':  "eq=contrast=1.03",
}

# ---------------------------------------------------------------- Hilfen
def run(cmd, what):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.returncode:
        print(r.stderr[-2500:])
        sys.exit(f"FEHLER bei: {what}  (siehe Meldung oben, Lösungen in edit-formate/TROUBLESHOOTING.md)")
    return r.stdout

def fr(t): return round(t * FPS) / FPS

def probe(path):
    if not os.path.exists(path):
        sys.exit(f"FEHLER: Datei nicht gefunden: {path}")
    out = run(f'ffprobe -v error -show_entries stream=index,codec_type,codec_name,width,height,color_transfer -of json "{path}"', f'ffprobe {path}')
    st = json.loads(out)['streams']
    v = next((s for s in st if s['codec_type'] == 'video'), None)
    a = [s for s in st if s['codec_type'] == 'audio' and s.get('codec_name') in ('aac', 'pcm_s16le', 'pcm_s24le', 'alac', 'mp3', 'opus')]
    return v, (a[0]['index'] if a else None)

_cache = {}
def pre_filters(path, crop_y=0.06):
    """HDR (iPhone HLG/PQ) -> SDR, Hochformat-Clips -> 16:9-Ausschnitt."""
    if path not in _cache:
        v, _ = probe(path); _cache[path] = v
    v = _cache[path]; f = []
    tr = v.get('color_transfer', '')
    if tr in ('arib-std-b67', 'smpte2084'):
        f.append(f"zscale=tin={tr}:min=bt2020nc:pin=bt2020:t=linear:npl=203,format=gbrpf32le,"
                 "zscale=p=bt709,tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p")
    if v['height'] > v['width']:
        f.append(f"crop=iw:iw*9/16:0:ih*{crop_y}")
    return f

def load_audio(path):
    _, idx = probe(path)
    if idx is None: sys.exit(f"FEHLER: keine Tonspur in {path}")
    tmp = os.path.join(WORK, f'aud_{abs(hash(path))}.wav')
    if not os.path.exists(tmp):
        run(f'ffmpeg -v error -y -i "{path}" -map 0:{idx} -ac 1 -ar {SR} "{tmp}"', f'Ton lesen {path}')
    return sf.read(tmp)[0].astype(np.float64)

def fade(a, ms=8):
    k = min(int(ms / 1000 * SR), len(a) // 2)
    if k > 0:
        r = np.linspace(0, 1, k); a = a.copy(); a[:k] *= r; a[-k:] *= r[::-1]
    return a

# ---------------------------------------------------------------- Untertitel-Stile
CY = r'\c&H00F0E000&'          # Cyan  (ASS-Farben sind &HBBGGRR&)
YE = r'\c&H0000E5FF&'          # Gelb
WH = r'\c&H00FFFFFF&'
POP = r'\fscx118\fscy118\t(0,80,\fscx100\fscy100)'
SUBSTYLES = {
    # 1A Ferrari-Block: 2 Zeilen eng übereinander, gleich breit gezogen, oben links, leicht 3D
    '1A': dict(font='Archivo Black', file='ArchivoBlack-Regular.ttf', mode='block', key=CY),
    # 1C Ferrari-Einzelwort: ein Wort groß oben links, leicht 3D
    '1C': dict(style="Archivo Black,76,&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,0,0,0,0,86,100,-1,0,1,0,3,7,0,0,0,1",
               pos=rf'\an7\pos(48,{TOP+40})\fry-12\frx3', mode='single', key=CY),
    # 2 Klassik: fett, Großbuchstaben, Wort für Wort aufbauend, gelbe Keywords, unten
    '2':  dict(style="Poppins,58,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,1,0,1,4,2,2,40,40,0,1",
               pos=rf'\an2\pos(540,{TOP+VH-66})', mode='accum', key=YE),
    # 5 Rot Anton: ein Wort in der Mitte
    '5':  dict(style="Anton,86,&H002020E8,&H002020E8,&H00100000,&H64000000,0,0,0,0,100,100,1,0,1,3,0,5,0,0,0,1",
               pos=rf'\an5\pos(540,{TOP+VH//2})', mode='single', key=''),
    # 8 Bebas groß mit Schatten, Keywords gelb
    '8':  dict(style="Bebas Neue,120,&H00FFFFFF,&H00FFFFFF,&H00000000,&HA0000000,0,0,0,0,100,100,2,0,1,0,6,5,0,0,0,1",
               pos=rf'\an5\pos(540,{TOP+330})', mode='accum2', key=YE),
    # 9 Zwei Zeilen klein/GROSS: Satz klein oben, aktuelles Wort groß darunter
    '9':  dict(style="Archivo Black,46,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,3,0,2,0,0,0,1",
               pos=rf'\an2\pos(540,{TOP+VH-48})', mode='twoline', key=YE),
}

def ts(t): return f"0:{int(t // 60):02d}:{t % 60:05.2f}"

def build_subs(cfg, talk, T0, path):
    st = SUBSTYLES[cfg.get('sub_style', '2')]
    def o_of(ti, s_): return talk[ti]['o'] + (s_ - talk[ti]['s'])
    styles = "Style: S," + st.get('style', "Archivo Black,60,&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,0,0,0,0,100,100,0,0,1,0,2,7,0,0,0,1")
    ev = []
    for ti, words, end in cfg['subs']:
        cend = min(o_of(ti, end), talk[ti]['o'] + talk[ti]['d'] - 0.01, T0 - 0.04)
        for j, (w, s_, key) in enumerate(words):
            a = o_of(ti, s_); b = o_of(ti, words[j + 1][1]) if j + 1 < len(words) else cend
            if b <= a + 0.02: continue
            m = st['mode']; k = st['key']
            if m == 'single':
                txt = '{' + st['pos'] + POP + (k if key else '') + '}' + w
                ev.append((a, b, txt))
            elif m in ('accum', 'accum2'):
                parts = []
                for q, (w2, _, k2) in enumerate(words[:j + 1]):
                    p = ('{' + k + '}' if k2 and k else '') + w2 + ('{' + WH + '}' if k2 and k else '')
                    if q == j: p = '{' + POP + '}' + p + r'{\fscx100\fscy100}'
                    parts.append(p)
                ev.append((a, b, '{' + st['pos'] + '}' + ' '.join(parts)))
            elif m == 'twoline':
                small = ' '.join(x[0] for x in words[:j])
                big = ('{' + k + '}' if key else '') + w
                txt = '{' + st['pos'] + '}' + (r'{\fs40}' + small + r'\N' if small else '') + r'{\fs86' + POP + '}' + big
                ev.append((a, b, txt))
            elif m == 'block':
                # 1A: bisher gesprochene Wörter des Chunks auf max. 2 Zeilen, jede Zeile auf gleiche Breite
                cur = words[:j + 1]
                lines = [cur] if len(cur) <= 2 else [cur[:len(cur) // 2], cur[len(cur) // 2:]]
                font = ImageFont.truetype(os.path.join(FONTS, st['file']), 60)
                y = TOP + 30; target = 300
                for ln in lines:
                    text = ' '.join(x[0] for x in ln)
                    wpx = font.getlength(text) * 0.84 - (len(text) - 1)
                    fs = 60 * target / max(wpx, 1); fs = min(fs, 120)
                    keyed = any(x[2] for x in ln)
                    ev.append((a, b, rf'{{\an7\pos(46,{y:.0f})\fs{fs:.0f}\fscx84\fsp-1\fry-10\frx3{k if keyed else ""}}}{text}'))
                    y += fs * 0.80
    head = ["[Script Info]", "ScriptType: v4.00+", "PlayResX: 1080", "PlayResY: 1920", "WrapStyle: 2", "",
            "[V4+ Styles]",
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
            styles, "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    body = [f"Dialogue: 0,{ts(a)},{ts(b)},S,,0,0,0,,{t}" for a, b, t in ev]
    open(path, 'w', encoding='utf-8').write("\n".join(head + body) + "\n")

# ---------------------------------------------------------------- Hauptablauf
def main(jpath):
    global WORK
    cfg = json.load(open(jpath, encoding='utf-8'))
    root = os.path.dirname(os.path.abspath(jpath))
    name = cfg.get('name', os.path.splitext(os.path.basename(jpath))[0])
    WORK = os.path.join(root, f'_work_{name}'); os.makedirs(WORK, exist_ok=True)
    base = os.path.join(root, cfg['base']) if not os.path.isabs(cfg['base']) else cfg['base']
    clips_dir = os.path.join(root, cfg.get('clips_dir', '.'))
    def clip(p): return p if os.path.isabs(p) else os.path.join(clips_dir, p)
    sound = cfg['sound'] if os.path.isabs(cfg['sound']) else os.path.join(root, cfg['sound'])
    for s in cfg['shots']:
        if s[0] != 'BASE' and not os.path.exists(clip(s[0])):
            sys.exit(f"FEHLER: Clip nicht gefunden: {clip(s[0])}")

    # Gespräch
    talk = []; t = 0.0
    for seg in cfg['talk']:
        s, e = seg[0], seg[1]; z = seg[2] if len(seg) > 2 else 1.0; ae = seg[3] if len(seg) > 3 else None
        d = fr(e - s); talk.append(dict(s=s, d=d, z=z, ae=ae, o=t)); t += d
    T0 = t; P_ = cfg['beat']; hb = P_ / 2
    EL = sum(b - a for a, b in cfg['music']); TOTAL = fr(T0 + EL)
    shots = []; acc = 0.0
    for c, s, nb, sp, fx in cfg['shots']:
        a = fr(T0 + acc * P_)
        if nb == 'rest': b = TOTAL
        else: acc += nb; b = fr(T0 + acc * P_)
        shots.append(dict(c=c, s=s, sp=sp, fx=fx, o=a, d=round(b - a, 4)))
    if shots[-1]['o'] >= TOTAL - 0.2:
        sys.exit(f"FEHLER: Shots ({acc} Beats = {acc*P_:.2f}s) sind länger als die Musik ({EL:.2f}s). Beats kürzen oder 'music' verlängern.")
    print(f"Gespräch {T0:.2f}s | Edit {EL:.2f}s | gesamt {TOTAL:.2f}s | {len(shots)} Shots")

    parts = []; style = cfg.get('style', 'chaos')
    # --- Gesprächs-Teile
    for i, x in enumerate(talk):
        out = os.path.join(WORK, f't{i}.mp4'); parts.append(out); z = x['z']; n = round(x['d'] * FPS)
        f = pre_filters(base) + [f"fps={FPS}", "scale=2160:1216", f"crop={int(2160/z)//2*2}:{int(1216/z)//2*2}:(iw-ow)/2:(ih-oh)/2*0.6",
                                 f"scale={VW}:{VH}:flags=lanczos", "setsar=1"]
        if i == len(talk) - 1 and cfg.get('fog'):
            f += [f"drawbox=c=white@0.25:t=fill:enable='eq(n,{n-3})'", f"drawbox=c=white@0.55:t=fill:enable='eq(n,{n-2})'",
                  f"drawbox=c=white@0.85:t=fill:enable='eq(n,{n-1})'", f"avgblur=sizeX=8:sizeY=8:enable='gte(n,{n-2})'"]
        f.append("format=yuv420p")
        print(f"  Gespräch {i+1}/{len(talk)}")
        run(f'ffmpeg -v error -y -ss {x["s"]} -i "{base}" -t {x["d"]+0.2} -an -vf "{",".join(f)}" -frames:v {n} -c:v libx264 -preset veryfast -crf 15 -r {FPS} "{out}"', f'Gesprächsteil {i+1}')

    # --- Edit-Shots
    for i, x in enumerate(shots):
        out = os.path.join(WORK, f'e{i}.mp4'); parts.append(out)
        d = x['d']; fx = x['fx']; n = max(1, round(d * FPS))
        src = base if x['c'] == 'BASE' else clip(x['c'])
        f = pre_filters(src)
        if x['sp'] != 1: f.append(f"setpts={1/x['sp']}*(PTS-STARTPTS)")
        f += [f"fps={FPS}", "scale=2160:1216"]
        z = "1"
        if 'zout' in fx: z += f"+0.13*(1-on/{n})"
        if 'zin' in fx: z += f"+0.10*on/{n}"
        if 'zb_in' in fx: z += "+0.40*max(0,1-on/3)"
        if 'zb_out' in fx: z += f"+0.45*pow(max(0,(on-({n}-4))/4),1.6)"
        if 'steps' in fx: z += f"+0.09*floor(on/{max(2, round(hb*FPS))})"
        if 'punch' in fx: z += "+0.14"
        if 'pulse' in fx: z += f"+if(lt(mod(on/{FPS},{P_}),{hb}),0.16,0.07)*exp(-mod(on/{FPS},{hb})*11)"
        f.append(f"zoompan=z='{z}':d=1:x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':s={VW}x{VH}:fps={FPS}")
        f += ["setsar=1", GRADE.get(style, GRADE['chaos'])]
        if 'pulse' in fx: f.append(f"eq=brightness='if(lt(mod(t,{P_}),{hb}),0.16,0.07)*exp(-mod(t,{hb})*13)':contrast=1.04:eval=frame")
        if 'whip_in' in fx:  f += ["avgblur=sizeX=55:sizeY=1:enable='lt(n,2)'", "avgblur=sizeX=20:sizeY=1:enable='eq(n,2)'"]
        if 'whip_out' in fx: f += [f"avgblur=sizeX=20:sizeY=1:enable='eq(n,{n-3})'", f"avgblur=sizeX=55:sizeY=1:enable='gte(n,{n-2})'"]
        if 'zb_in' in fx:  f += ["avgblur=sizeX=14:sizeY=14:enable='lt(n,1)'", "avgblur=sizeX=7:sizeY=7:enable='eq(n,1)'"]
        if 'zb_out' in fx: f.append(f"avgblur=sizeX=10:sizeY=10:enable='gte(n,{n-2})'")
        if 'fog_in' in fx:
            f += ["drawbox=c=white@0.9:t=fill:enable='eq(n,0)'", "drawbox=c=white@0.65:t=fill:enable='eq(n,1)'",
                  "drawbox=c=white@0.4:t=fill:enable='eq(n,2)'", "drawbox=c=white@0.18:t=fill:enable='eq(n,3)'",
                  "avgblur=sizeX=10:sizeY=10:enable='lt(n,3)'"]
        if 'dip_in' in fx:  f += ["drawbox=c=white@0.75:t=fill:enable='eq(n,0)'", "drawbox=c=white@0.35:t=fill:enable='eq(n,1)'"]
        if 'dip_out' in fx: f += [f"drawbox=c=white@0.35:t=fill:enable='eq(n,{n-2})'", f"drawbox=c=white@0.75:t=fill:enable='eq(n,{n-1})'"]
        if 'flash' in fx:  f += ["drawbox=c=white@1:t=fill:enable='eq(n,0)'", "drawbox=c=white@0.45:t=fill:enable='eq(n,1)'"]
        if 'flash1' in fx: f.append("drawbox=c=white@1:t=fill:enable='eq(n,0)'")
        if 'overexp' in fx: f.append("eq=brightness=0.3:contrast=0.85:enable='lt(n,2)'")
        f.append("format=yuv420p")
        print(f"  Shot {i+1}/{len(shots)}  {os.path.basename(src)} ab {x['s']}s  {d:.2f}s  {' '.join(fx)}")
        run(f'ffmpeg -v error -y -ss {x["s"]} -t {d*x["sp"]+0.3} -i "{src}" -an -vf "{",".join(f)}" -frames:v {n} -c:v libx264 -preset veryfast -crf 15 -r {FPS} "{out}"', f'Shot {i+1} ({src})')

    lst = os.path.join(WORK, 'list.txt')
    open(lst, 'w').write(''.join(f"file '{p}'\n" for p in parts))
    run(f'ffmpeg -v error -y -f concat -safe 0 -i "{lst}" -c copy "{WORK}/video169.mp4"', 'Teile zusammenfügen')

    # --- Ton
    print("  Ton mischen")
    meter = pyln.Meter(SR); N = int(TOTAL * SR) + SR
    main_a = load_audio(base); snd = load_audio(sound)
    voice = np.zeros(N); music = np.zeros(N)
    for x in talk:
        end = x['ae'] if x['ae'] else x['s'] + x['d']
        seg = fade(main_a[int(x['s'] * SR):int(end * SR)]); o = int(x['o'] * SR); voice[o:o + len(seg)] += seg
    gv = 10 ** ((-16 - meter.integrated_loudness(voice[:int(T0 * SR)])) / 20); voice *= gv
    for x in shots:
        if 'keepaudio' in x['fx']:
            seg = fade(main_a[int(x['s'] * SR):int((x['s'] + x['d']) * SR)], 30) * gv * 0.35
            o = int(x['o'] * SR); voice[o:o + len(seg)] += seg
    ed = np.concatenate([fade(snd[int(a * SR):int(b * SR)], 6) for a, b in cfg['music']])
    L = int((TOTAL - T0) * SR); ed = np.pad(ed, (0, max(0, L - len(ed))))[:L]
    ed[-int(0.02 * SR):] *= np.linspace(1, 0, int(0.02 * SR))
    ed *= 10 ** ((cfg.get('edit_lufs', -9) - meter.integrated_loudness(ed)) / 20)
    music[int(T0 * SR):int(T0 * SR) + L] += ed
    bed = cfg.get('bed')
    if bed:
        bs = cfg['music'][0][0] - T0 if bed.get('start', 'auto') == 'auto' else bed['start']
        if bs < 0: sys.exit("FEHLER: Musik vor dem Drop reicht nicht für das ganze Gespräch. 'bed.start' setzen oder Sound mit längerem Anfang nehmen.")
        b = snd[int(bs * SR):int((bs + T0) * SR)].copy()
        if bed.get('lowpass'):
            b_, a_ = ss.butter(2, bed['lowpass'] / (SR / 2), 'low'); b = ss.lfilter(b_, a_, b)
        env = np.full(len(b), 10 ** ((bed.get('lufs', -28) - meter.integrated_loudness(b)) / 20))
        env[:int(0.3 * SR)] *= np.linspace(0, 1, int(0.3 * SR))
        cut = bed.get('cut')
        if bed.get('cut_before_drop') is not None: cut = T0 - bed['cut_before_drop']
        if cut is not None:
            c = int(cut * SR)
            env[c:] = 0; env[max(0, c - int(0.06 * SR)):c] *= np.linspace(1, 0, min(c, int(0.06 * SR)))
        music[:len(b)] += b * env
    mix = (voice + music)[:int(TOTAL * SR)]
    sf.write(os.path.join(WORK, 'audio.wav'), np.stack([mix, mix], 1).astype('float32'), SR, subtype='FLOAT')

    # --- Untertitel + Endmontage
    print("  Untertitel + fertiges Video")
    build_subs(cfg, talk, T0, os.path.join(WORK, 'subs.ass'))
    out = cfg.get('out', f'{name}.mp4'); out = out if os.path.isabs(out) else os.path.join(root, out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    sub = os.path.join(WORK, 'subs.ass').replace(':', r'\:').replace("'", r"\'")
    fonts = FONTS.replace(':', r'\:')
    run(f'ffmpeg -v error -y -i "{WORK}/video169.mp4" -i "{WORK}/audio.wav" '
        f'-filter_complex "[0:v]pad=1080:1920:0:{TOP}:black,subtitles=\'{sub}\':fontsdir=\'{fonts}\'[v]" '
        f'-map "[v]" -map 1:a -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p '
        f'-af alimiter=limit=0.93:attack=3:release=60:level=false -c:a aac -b:a 192k -t {TOTAL} -movflags +faststart "{out}"', 'Endmontage')
    sheet = os.path.splitext(out)[0] + '_check.jpg'
    run(f'ffmpeg -v error -y -i "{out}" -vf "fps=4,crop=1080:{VH}:0:{TOP},scale=180:-1,tile=10x{int(TOTAL*4/10)+1}" -frames:v 1 "{sheet}"', 'Kontaktbogen')
    print(f"FERTIG: {out}\nKontaktbogen: {sheet}")
    if not cfg.get('keep_work'): shutil.rmtree(WORK, ignore_errors=True)

if __name__ == '__main__':
    if len(sys.argv) != 2: sys.exit("Aufruf: python3 edit-formate/edit.py projekte/NAME/edit.json")
    main(sys.argv[1])

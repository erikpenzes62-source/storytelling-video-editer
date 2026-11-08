#!/usr/bin/env python3
"""Untertitel für edit.json automatisch aus dem Grundvideo bauen (Whisper).

Aufruf:  python3 edit-formate/untertitel.py projekte/NAME/edit.json [max_wörter] [keyword ...]
Beispiel: python3 edit-formate/untertitel.py projekte/nein/edit.json 3 nein wirklich

- Transkribiert das Grundvideo ("base") einmal und speichert words.json im Projektordner
  (beim zweiten Aufruf wird words.json wiederverwendet – zum Neu-Transkribieren löschen).
- Nimmt nur Wörter, die in den "talk"-Abschnitten liegen.
- Chunks mit höchstens max_wörter Wörtern (Standard 3), Umbruch nach Satzzeichen.
- Zahlen und angegebene Keywords werden markiert (farbig).
- Schreibt "subs" in die edit.json. Falsch erkannte Wörter danach dort von Hand korrigieren.
"""
import sys, json, re, os, subprocess, tempfile

jpath = sys.argv[1]
maxw = int(sys.argv[2]) if len(sys.argv) > 2 else 3
keys = [k.lower() for k in sys.argv[3:]]
cfg = json.load(open(jpath, encoding='utf-8'))
root = os.path.dirname(os.path.abspath(jpath))
base = cfg['base'] if os.path.isabs(cfg['base']) else os.path.join(root, cfg['base'])
wpath = os.path.join(root, 'words.json')

if not os.path.exists(wpath):
    # richtige Tonspur finden (iPhone-.mov hat oft zuerst eine Spur, die ffmpeg nicht lesen kann)
    st = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=index,codec_type,codec_name', '-of', 'json', base],
                                   capture_output=True, text=True).stdout)['streams']
    aud = [s['index'] for s in st if s['codec_type'] == 'audio' and s.get('codec_name') in ('aac', 'pcm_s16le', 'pcm_s24le', 'alac', 'mp3', 'opus')]
    if not aud: sys.exit(f"FEHLER: keine lesbare Tonspur in {base}")
    wav = os.path.join(tempfile.mkdtemp(), 'a.wav')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', base, '-map', f'0:{aud[0]}', '-ac', '1', '-ar', '16000', wav], check=True)
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        sys.exit("FEHLER: faster-whisper fehlt:  source .venv/bin/activate  und  pip install -r requirements.txt")
    print("Transkribiere (beim ersten Mal lädt Whisper das Modell, das dauert) …")
    model = WhisperModel(os.environ.get('WHISPER_MODEL', 'medium'), device='cpu', compute_type='int8')
    import soundfile as sf
    audio = sf.read(wav, dtype='float32')[0]            # als Array übergeben (umgeht PyAV-Versionsprobleme)
    segs, _ = model.transcribe(audio, language='de', word_timestamps=True, beam_size=5)
    words = [{'w': w.word.strip(), 's': round(w.start, 2), 'e': round(w.end, 2)} for s in segs for w in (s.words or []) if w.word.strip()]
    json.dump(words, open(wpath, 'w', encoding='utf-8'), ensure_ascii=False)
words = json.load(open(wpath, encoding='utf-8'))

subs = []
for ti, seg in enumerate(cfg['talk']):
    s, e = seg[0], seg[1]
    chunk = []
    def flush():
        if chunk:
            subs.append([ti, [[w['w'].upper(), round(max(w['s'], s), 2),
                               1 if (re.search(r'\d', w['w']) or w['w'].lower().strip('.,!?') in keys) else 0] for w in chunk],
                         round(min(chunk[-1]['e'] + 0.3, e), 2)])
            chunk.clear()
    for w in [w for w in words if s - 0.05 <= w['s'] < e]:
        chunk.append(w)
        if len(chunk) >= maxw or w['w'][-1:] in '.,!?': flush()
    flush()
for a, b in zip(subs, subs[1:]):
    if a[0] == b[0]: a[2] = min(a[2], b[1][0][1])
cfg['subs'] = subs
json.dump(cfg, open(jpath, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print("Alle Wörter im Grundvideo:", ' '.join(f"{w['w']}@{w['s']}" for w in words))
print()
for ti, ws, end in subs:
    print(f"[{ws[0][1]:6.2f}] " + ' '.join(('*' + w + '*') if k else w for w, _, k in ws))
print(f"\n{len(subs)} Untertitel in {jpath} geschrieben (*Wort* = farbig).")

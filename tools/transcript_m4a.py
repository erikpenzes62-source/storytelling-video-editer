"""Transkript mit Wort-Zeitstempeln aus einem iPhone-Sprachmemo (.m4a) lesen.

iOS speichert das Transkript im Atom 'tsrp' der Datei. Hat die Datei keins
(ältere iPhones, Bildschirmaufnahmen, andere Apps): tools/transcribe_whisper.py nehmen.
Aufruf:  python3 tools/transcript_m4a.py voice.m4a words.json
"""
import json, sys

def words(path):
    b = open(path, 'rb').read(); i = b.find(b'tsrp')
    if i < 0: raise SystemExit('FEHLER: kein eingebautes Transkript in dieser Datei -> tools/transcribe_whisper.py verwenden')
    s = b[i + 4:]; j = s.find(b'{'); depth = 0; end = None
    for k, ch in enumerate(s[j:]):
        if ch == 123: depth += 1
        elif ch == 125:
            depth -= 1
            if depth == 0: end = j + k + 1; break
    a = json.loads(s[j:end])['attributedString']
    runs = a['runs']; tab = a['attributeTable']; out = []
    for t, idx in zip(runs[0::2], runs[1::2]):
        tr = tab[idx].get('timeRange')
        if not t.strip() or tr is None: continue
        out.append({'w': t.strip(), 's': round(tr[0], 2), 'e': round(tr[0] + tr[1], 2)})
    return out

if __name__ == '__main__':
    w = words(sys.argv[1]); json.dump(w, open(sys.argv[2], 'w'), ensure_ascii=False)
    print(len(w), 'Wörter:', ' '.join(f"{i}:{x['w']}" for i, x in enumerate(w)))

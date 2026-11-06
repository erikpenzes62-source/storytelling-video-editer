"""Transkript mit Wort-Zeitstempeln für Audios OHNE eingebautes Transkript
(z. B. Bildschirmaufnahmen der Sprachmemo-App als .mp4).

Aufruf:  python3 tools/transcribe_whisper.py audio.mp4 words.json [modell]
Modell: medium (Standard, gut für Deutsch) oder small (schneller, weniger RAM).
Braucht:  pip install faster-whisper   (lädt das Modell beim ersten Mal herunter)
"""
import sys, json, subprocess, tempfile, os
from faster_whisper import WhisperModel

src, out = sys.argv[1], sys.argv[2]
model_name = sys.argv[3] if len(sys.argv) > 3 else 'medium'
wav = os.path.join(tempfile.mkdtemp(), 'a.wav')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-vn', '-ac', '1', '-ar', '16000', wav], check=True)
model = WhisperModel(model_name, device='cpu', compute_type='int8')
segs, _ = model.transcribe(wav, language='de', word_timestamps=True, vad_filter=True, beam_size=5)
words = []
for s in segs:
    for w in s.words or []:
        if w.word.strip():
            words.append({'w': w.word.strip(), 's': round(w.start, 2), 'e': round(w.end, 2)})
json.dump(words, open(out, 'w'), ensure_ascii=False)
print(len(words), 'Wörter:', ' '.join(f"{i}:{w['w']}" for i, w in enumerate(words)))

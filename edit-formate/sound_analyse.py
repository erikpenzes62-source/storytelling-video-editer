#!/usr/bin/env python3
"""Sound analysieren: Tempo, Beats, Drop-Kandidaten und eingebaute Pausen.

Aufruf:  python3 edit-formate/sound_analyse.py sound.wav   (auch .mp3/.m4a/.mp4 – Bildschirmaufnahme geht)
Ausgabe: Werte im Terminal + Bild  <sound>_analyse.png  (Wellenform, Spektrum, Beats)

Was du davon brauchst (für edit.json):
  beat   = "Beat-Abstand"            (Sekunden pro Beat)
  music  = [[DROP, ENDE]]            (DROP = ein Drop-Kandidat, ENDE = ein Beat oder eine Pause danach)
"""
import sys, os, subprocess, tempfile
import numpy as np
try:
    import librosa
except ImportError:
    sys.exit("FEHLER: librosa fehlt. Einmalig:  pip install librosa matplotlib")

src = sys.argv[1]
wav = os.path.join(tempfile.mkdtemp(), 'a.wav')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-vn', '-ac', '1', '-ar', '22050', wav], check=True)
y, sr = librosa.load(wav, sr=22050)
dur = len(y) / sr
tempo, beats = librosa.beat.beat_track(y=y, sr=sr, units='time')
P = float(np.median(np.diff(beats))) if len(beats) > 2 else 0
print(f"Länge {dur:.2f}s | Tempo ca. {float(np.atleast_1d(tempo)[0]):.0f} BPM | Beat-Abstand {P:.3f}s")
print("Beats:", ' '.join(f'{b:.2f}' for b in beats))

# Bass-Sprünge = Drop-Kandidaten
hop = 512
S = np.abs(librosa.stft(y, n_fft=2048, hop_length=hop)); f = librosa.fft_frequencies(sr=sr, n_fft=2048)
t = np.arange(S.shape[1]) * hop / sr
bass = 20 * np.log10(S[(f > 30) & (f < 150)].sum(0) + 1e-9)
win = int(0.5 * sr / hop)
cand = []
for i in range(max(win, int(1.0 * sr / hop)), len(bass) - win):
    if bass[i - win:i].mean() < -80: continue          # Stille am Anfang/Ende ignorieren
    jump = bass[i:i + win].mean() - bass[i - win:i].mean()
    cand.append((jump, t[i]))
cand.sort(reverse=True); picked = []
for j, tt in cand:
    if all(abs(tt - p) > 2 for _, p in picked): picked.append((j, tt))
    if len(picked) == 5: break
print("\nDrop-Kandidaten (Bass springt hoch, beste zuerst):")
for j, tt in sorted(picked, key=lambda x: -x[0]):
    nb = beats[np.argmin(abs(beats - tt))] if len(beats) else tt
    print(f"  {tt:6.2f}s  (+{j:4.1f} dB, nächster Beat {nb:.2f}s)")

# eingebaute Pausen im Song (gut für "Sound kurz weg" vor dem Drop)
rms = librosa.feature.rms(y=y, hop_length=hop)[0]; db = 20 * np.log10(rms + 1e-9); ref = np.percentile(db, 75)
quiet = db < ref - 18; gaps = []; start = None
for i, q in enumerate(quiet):
    tt = i * hop / sr
    if q and start is None: start = tt
    if not q and start is not None:
        if tt - start >= 0.2: gaps.append((start, tt))
        start = None
print("\nEingebaute Pausen (Song wird kurz still):", ', '.join(f'{a:.2f}–{b:.2f}s' for a, b in gaps) or 'keine')
print("\nLautstärke pro 0,5 s (dB):", ' '.join(f'{i*0.5:.1f}:{db[int(i*0.5*sr/hop):int((i+1)*0.5*sr/hop)].mean():.0f}' for i in range(int(dur * 2))))

try:
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt, librosa.display
    fig, ax = plt.subplots(2, 1, figsize=(18, 6), sharex=True)
    ax[0].plot(np.arange(len(y)) / sr, y, lw=.3)
    for b in beats: ax[0].axvline(b, color='orange', lw=.4)
    for _, tt in picked: ax[0].axvline(tt, color='red', lw=1.5)
    librosa.display.specshow(librosa.amplitude_to_db(S, ref=np.max), sr=sr, hop_length=hop, x_axis='time', y_axis='log', ax=ax[1])
    ax[1].set_xticks(np.arange(0, dur, 1))
    out = os.path.splitext(src)[0] + '_analyse.png'; plt.tight_layout(); plt.savefig(out, dpi=70)
    print(f"\nBild: {out}  (orange = Beats, rot = Drop-Kandidaten)")
except ImportError:
    print("\n(Für das Bild: pip install matplotlib)")

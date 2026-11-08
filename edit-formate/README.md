# Edit-Formate

Kurze Videos, die auf Musik geschnitten sind:

1. **Grundvideo:** ein Gespräch oder Moment mit einer Pointe, z. B. „12.000 € an einem Tag“ oder „Nein.“. Darunter läuft leise Musik.
2. **Kurze Stille:** Kurz vor dem Drop geht die Musik raus.
3. **Drop:** Ab hier läuft ein Edit aus deinen Clips, im Takt geschnitten, mit Übergängen und Effekten.

Am Ende steht ein **9:16-Video (1080 × 1920)**. Das Bild ist 16:9 in der Mitte, mit Untertiteln im Gesprächsteil.

```
Grundvideo (Gespräch, Musik leise drunter) ─► Pointe ─► 0,3 s Stille ─► DROP ─► Clips im Beat ─► Hero-Shot ─► Ende
```

> **Wenn etwas nicht funktioniert:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
> **Alle Felder der edit.json:** [docs/EDIT_JSON.md](docs/EDIT_JSON.md)
> **Was gut ankommt und was nicht:** [docs/EDIT_STIL.md](docs/EDIT_STIL.md)

---

## 1. Einrichten (einmalig)

Die Einrichtung ist dieselbe wie für das Storytelling-System, siehe [Haupt-README](../README.md#1-einrichten-einmalig):

```bash
brew install ffmpeg python git
git clone https://github.com/erikpenzes62-source/storytelling-video-editer.git
cd storytelling-video-editer
bash setup.sh
```

**Vor jeder Sitzung:**

```bash
cd storytelling-video-editer
source .venv/bin/activate
```

## 2. Ein Edit machen

### Schritt 1: Projektordner anlegen

```bash
mkdir -p projects/nein/{grundvideo,clips,sound}
```

- `grundvideo/` – das Gesprächsvideo (z. B. `IMG_5564.mov`)
- `clips/` – das Material für das Edit (iPhone-Videos gehen direkt, auch HDR und Hochformat)
- `sound/` – der Song (`.wav`, `.mp3`, `.m4a` oder eine Bildschirmaufnahme `.mp4`)

Ein passendes Beispiel aus `edit-formate/beispiele/` als Vorlage kopieren:

```bash
cp edit-formate/beispiele/nein_chaotisch.json projects/nein/edit.json
```

### Schritt 2: Sound analysieren

```bash
python3 edit-formate/sound_analyse.py projects/nein/sound/song.mp3
```

Ausgabe: Beat-Abstand, **Drop-Kandidaten** und eingebaute Pausen, dazu ein Bild `song_analyse.png`.
In die `edit.json` trägst du ein:

- `"sound"`: Pfad zum Song
- `"beat"`: den Beat-Abstand (z. B. `0.597`)
- `"music"`: `[[DROP, ENDE]]`, also wo im Song das Edit startet und endet (z. B. `[[13.42, 19.12]]`)

### Schritt 3: Gespräch festlegen

In `"talk"` steht, welche Stücke vom Grundvideo genommen werden: `[start, ende]` in Sekunden.

- **Erzählt das Grundvideo die Geschichte selbst** (kurz, ein Moment): **ein** Stück, nur am Ende kürzen, z. B. `[[0, 6.4]]`.
- **Langes Gespräch** (z. B. das 12.000-€-Video): mehrere Stücke, Pausen raus. Optional ein 3. Wert (Zoom, z. B. `1.08`) gegen sichtbare Sprünge und ein 4. Wert, ab wann der Ton im letzten Stück still sein soll.

Das letzte Stück endet direkt nach der **Pointe**, danach kommt der Drop.

### Schritt 4: Untertitel automatisch erstellen

```bash
python3 edit-formate/untertitel.py projects/nein/edit.json 4 nein wirklich
```

- Whisper schreibt mit, was im Grundvideo gesagt wird (das erste Mal dauert länger), und trägt die Untertitel in die `edit.json` ein.
- `4` steht für höchstens 4 Wörter pro Untertitel (eine Phrase). Angezeigt werden die Wörter einzeln oder zu zweit nacheinander (`"sub_speed": "words"`, Standard). `nein wirklich` sind die Keywords, die farbig werden. Zahlen werden automatisch farbig.
- Falsch erkannte Wörter korrigierst du danach direkt in der `edit.json` unter `"subs"`.
- Den Stil wählst du mit `"sub_style"`: `1A`, `1C`, `2`, `5`, `8` oder `9` (Bilder und Beschreibung in [docs/EDIT_STIL.md](docs/EDIT_STIL.md)).

### Schritt 5: Shots festlegen

In `"shots"` steht pro Zeile: `[Clip, Start im Clip (s), Länge in Beats, Tempo, [Effekte]]`

```json
["IMG_4265.mov", 0.3, 1.5, 1, ["pulse"]]
```

- Die **Länge** zählt in Beats: `1` = ein Beat, `0.5` = halber Beat. Beim letzten Shot steht `"rest"`, der läuft bis zum Ende der Musik.
- **Tempo:** `1` = normal, `0.5` = halb so schnell (Zeitlupe), `0.25` = viertel (nur bei 60/120-fps-Clips schön).
- **Clip** `"BASE"` = ein Stück aus dem Grundvideo selbst, z. B. der Geldwurf direkt nach der Pointe.
- Alle Effekte stehen in [docs/EDIT_JSON.md](docs/EDIT_JSON.md#effekte).

### Schritt 6: Rendern

```bash
python3 edit-formate/edit.py projects/nein/edit.json
```

Das dauert etwa 1–2 Minuten. Am Ende entstehen:

- `projects/nein/fertig/…mp4`: das fertige Video
- `projects/nein/fertig/…_check.jpg`: ein Kontaktbogen (4 Bilder pro Sekunde) zum schnellen Prüfen

Anschauen, in der `edit.json` etwas ändern und denselben Befehl nochmal starten.

---

## Dateien

| Datei | Zweck |
|---|---|
| `edit.py` | Die Engine: Gespräch + Musik + Shots + Effekte + Untertitel → MP4 |
| `sound_analyse.py` | Beats, Drop-Kandidaten, Pausen im Song finden |
| `untertitel.py` | Whisper-Transkript → Untertitel in der edit.json |
| `beispiele/*.json` | Fertige Vorlagen: Cinematic (12.000 €), Chaotisch („Nein.“), Cinematic mit 1C-Untertiteln (Spaßgutscheine) |
| `docs/EDIT_JSON.md` | Alle Felder und Effekte |
| `docs/EDIT_STIL.md` | Stilregeln und Untertitel-Stile |
| `TROUBLESHOOTING.md` | Fehler und Lösungen |

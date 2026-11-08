# Storytelling-Video-Editor

Das System schneidet aus einem Voiceover und einem Ordner mit eigenen Clips fertige **TikTok-Storytelling-Videos**. Jedes Video hat:

- Format 1080 × 1920, 60 fps
- Wort-für-Wort-Untertitel mit hervorgehobenen Keywords
- emotionale Einblendungen, z. B. ein Kontostand, der hochzählt, grüne Haken oder ein „Scam“-Stempel
- Soundeffekte (earshot) und Ton auf TikTok-Lautstärke (−14 LUFS)

Musik ist bewusst **nicht** drin, die kommt in TikTok dazu.

```
Voiceover ─► Transkript ─► Untertitel ─┐
Clips ─► Clip-Datenbank ─► Schnittliste ┼─► Clips schneiden ─► Effekte rendern ─► Ton mischen ─► final.mp4
            Einblendungen + Sounds ─────┘
```

> **Wenn etwas nicht funktioniert:** Schau zuerst in **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)**, dort steht jeder bekannte Fehler mit Lösung.

> **Neu: Edit-Formate.** Gespräch + Musik-Drop + Beat-Edit aus Clips (9:16). Anleitung: **[edit-formate/README.md](edit-formate/README.md)**, Fehler: **[edit-formate/TROUBLESHOOTING.md](edit-formate/TROUBLESHOOTING.md)**

---

## 1. Einrichten (einmalig)

Voraussetzung ist ein Mac (oder Linux) mit **ffmpeg** und **Python 3**. Auf dem Mac installierst du beides mit [Homebrew](https://brew.sh):

```bash
brew install ffmpeg python git
```

Dann das Repo holen und einrichten:

```bash
git clone https://github.com/erikpenzes62-source/storytelling-video-editer.git
cd storytelling-video-editer
bash setup.sh
```

`setup.sh` macht vier Dinge:

- legt eine eigene Python-Umgebung an (`.venv`)
- installiert Pillow, numpy und faster-whisper
- holt **earshot** für die Soundeffekte
- rendert die 25 Standard-Sounds nach `sounds/`

**Vor jeder Sitzung** im Terminal:

```bash
cd storytelling-video-editer
source .venv/bin/activate
export CLIPS_DIR="$HOME/Downloads/Neuer Ordner"   # Ordner mit den eigenen Clips
```

## 2. Clips einlesen (einmalig, und jedes Mal, wenn neue Clips dazukommen)

```bash
python3 tools/clip_info.py "$CLIPS_DIR" data/clipinfo.json data/bright.json
```

Jeder Clip bekommt dabei eine **feste ID** (0, 1, 2 …). Mit dieser ID wird der Clip in der Schnittliste verwendet. Das Skript speichert außerdem Länge, Format, HDR und Helligkeit (0 = schwarz, 255 = weiß). Bereits eingelesene Clips überspringt es.

Tipp: Eine Übersicht mit einem Bild pro Clip macht die Auswahl leichter:

```bash
mkdir -p data/thumbs && for f in "$CLIPS_DIR"/*.{MOV,MP4,mov,mp4}; do ffmpeg -v error -y -ss 1 -i "$f" -frames:v 1 -vf scale=180:-1 "data/thumbs/$(basename "$f").jpg"; done
```

## 3. Ein Video machen

Für jedes Video gibt es einen Ordner unter `projects/`. Am einfachsten kopierst du das Beispiel:

```bash
cp -r examples/demo projects/video15
cp "/Pfad/zur/Audio.m4a" projects/video15/voice.m4a
```

### Schritt 1: Transkript mit Wort-Zeitstempeln

- **iPhone-Sprachmemo (.m4a):** Das Transkript steckt schon in der Datei.
  ```bash
  python3 tools/transcript_m4a.py projects/video15/voice.m4a projects/video15/words.json
  ```
- **Bildschirmaufnahme oder andere Audio (.mp4, .mp3 …):** Hier erstellt Whisper das Transkript. Das dauert ein paar Minuten.
  ```bash
  python3 tools/transcribe_whisper.py projects/video15/voice.mp4 projects/video15/words.json
  ```

Das Skript gibt alle Wörter mit Nummer aus, z. B. `12:Hig 13:Ticket`. Diese Nummern brauchst du für Korrekturen im nächsten Schritt.

### Schritt 2: Untertitel

Trage in `fixes.json` die Korrekturen und die Keywords ein:

```json
{
  "fix":  {"12": "High Ticket", "13": null},
  "keys": ["business", "skill", "high ticket"]
}
```

- `"12": "High Ticket"` ersetzt Wort 12 durch diesen Text.
- `"13": null` löscht Wort 13, die Zeit wird an das vorige Wort angehängt.
- `keys` sind die Wörter, die farbig hervorgehoben werden. Pro Untertitel wird höchstens eine Gruppe markiert.

```bash
python3 tools/captions.py projects/video15/words.json projects/video15/fixes.json projects/video15/chunks.json 3 17
```

`3 17` bedeutet: höchstens 3 Wörter und 17 Zeichen pro Untertitel. Die Ausgabe zeigt alle Untertitel mit Startzeit. Mit diesen Zeiten planst du Schnitte und Effekte.

### Schritt 3: `project.json` ausfüllen

Hier legst du fest, welcher Clip wann läuft, welche Effekte kommen und welche Sounds. Die komplette Erklärung steht in **[docs/PROJECT_JSON.md](docs/PROJECT_JSON.md)**, alle Effekte in **[docs/EFFEKTE.md](docs/EFFEKTE.md)**. Die Stilregeln (was gut ankommt und was nicht) stehen in **[docs/STIL.md](docs/STIL.md)**.

### Schritt 4: Alles rendern

```bash
bash run_all.sh projects/video15
```

Das Skript läuft diese Schritte nacheinander ab:

1. **Schnittliste prüfen:** Ist jeder Clip lang genug? Wie verläuft die Helligkeit?
2. **Safe Zone prüfen:** Ragt etwas unter die TikTok-Buttons? Ein Testbild landet in `safezone.jpg`.
3. **Clips schneiden:** 1080 × 1920, 60 fps; iPhone-HDR wird automatisch auf normal umgerechnet.
4. **Basisvideo** zusammenfügen.
5. **Effekte und Untertitel** rendern, in 10-Sekunden-Stücken.
6. **Ton** mischen und mastern, danach das **fertige Video** `projects/video15/final.mp4` plus Kontaktbogen `check.jpg`.

Bricht etwas ab (z. B. weil der Mac einschläft), **startest du einfach denselben Befehl noch einmal**. Was schon fertig ist, wird übersprungen.

Ungefähre Dauer auf einem MacBook für ein 100-Sekunden-Video: Schneiden 10–20 min (4K-HDR-Clips sind langsam), Rendern 10–15 min.

### Schritt 5: Prüfen und hochladen

- `check.jpg` anschauen: Passt die Helligkeit? Sind die Untertitel lesbar? Sitzen die Einblendungen?
- `final.mp4` ganz anschauen, mit Ton.
- Per AirDrop aufs iPhone schicken und in TikTok unter „Mehr Optionen“ **„Hochladen in hoher Qualität“** einschalten.

---

## Ordner

| Ordner/Datei | Inhalt |
|---|---|
| `setup.sh` | Einmalige Einrichtung |
| `run_all.sh` | Kompletter Ablauf für ein Projekt |
| `tools/` | Alle Skripte (siehe unten) |
| `tools/overlay.py` | Die Effekt-Engine: alle Einblendungen und Untertitel-Stile |
| `tools/fonts/` | Schriften (Google Fonts, Open Font License) |
| `examples/demo/` | Beispielprojekt zum Kopieren |
| `docs/` | Stilregeln, Effekte, project.json-Referenz |
| `edit-formate/` | Zweites System: Edit-Formate (Gespräch + Drop + Beat-Edit), eigene Anleitung |
| `data/` | Clip-Datenbank (wird angelegt, nicht im Repo) |
| `sounds/` | Soundeffekte (werden angelegt, nicht im Repo) |
| `projects/` | Eure Videos (nicht im Repo) |

| Skript | Zweck |
|---|---|
| `tools/clip_info.py` | Clips einlesen: ID, Länge, HDR, Helligkeit |
| `tools/transcript_m4a.py` | Transkript aus iPhone-Sprachmemo lesen |
| `tools/transcribe_whisper.py` | Transkript per Whisper erstellen |
| `tools/captions.py` | Untertitel-Chunks und Keywords bauen |
| `tools/cutlist.py` | Schnittliste prüfen, `cut.json` schreiben |
| `tools/safezone_check.py` | TikTok-Safe-Zone prüfen, `safezone.jpg` erstellen |
| `tools/cut_segments.py` | Clips schneiden (fortsetzbar, parallel möglich) |
| `tools/make_base.sh` | Segmente zu `base.mp4` zusammenfügen |
| `tools/render_all.sh` / `render.py` | Effekte und Untertitel rendern |
| `tools/mix.py` | Stimme und Sounds mischen, auf −14 LUFS mastern |
| `tools/finish.sh` | Fertiges Video und Kontaktbogen erstellen |
| `tools/render_sounds.sh` | earshot-Sounds rendern |
| `tools/extract_sound.sh` | Originalton aus einem Clip als Sound speichern (z. B. das Kaching) |

Soundeffekte: [earshot](https://github.com/Leonxlnx/earshot) von Leon Lin (MIT-Lizenz).

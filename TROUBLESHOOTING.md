# Wenn etwas nicht funktioniert

Lies die **letzte Zeile mit `FEHLER`**, die das Terminal ausgibt, und such sie hier. Fast alle Schritte lassen sich gefahrlos wiederholen. Was schon fertig ist, wird übersprungen.

## Schnellcheck: Läuft alles?

```bash
cd storytelling-video-editer
source .venv/bin/activate          # (.venv) muss vorne im Terminal stehen
echo $CLIPS_DIR                    # muss den Clip-Ordner zeigen
ffmpeg -version | head -1          # ffmpeg vorhanden?
python3 -c "import PIL, numpy; print('Python ok')"
ls sounds | wc -l                  # sollte 25 oder mehr sein
```

---

## Einrichtung

| Problem | Lösung |
|---|---|
| `command not found: brew` | Homebrew installieren: https://brew.sh (den Befehl von der Seite ins Terminal kopieren), danach das Terminal neu öffnen |
| `FEHLER: ffmpeg fehlt` | `brew install ffmpeg` |
| `WARNUNG: ffmpeg ohne zscale` | `brew reinstall ffmpeg`. Ohne zscale sehen iPhone-HDR-Clips grau und flau aus oder brechen ab |
| `pip install` schlägt fehl | Zuerst `source .venv/bin/activate`, dann `pip install -r requirements.txt` erneut. Bei `externally-managed-environment`: Die venv ist nicht aktiv |
| `git clone … earshot` schlägt fehl | Internetverbindung prüfen. Notfalls `rm -rf .earshot` und `bash setup.sh` erneut |
| `earshot nicht installiert` | `source .venv/bin/activate`, dann `pip install --no-deps -e .earshot` und `bash tools/render_sounds.sh` |
| `ModuleNotFoundError: No module named 'PIL'` (oder numpy, faster_whisper) | Die venv ist nicht aktiv, also `source .venv/bin/activate` ausführen |

## Clips und Transkript

| Problem | Lösung |
|---|---|
| `FEHLER: CLIPS_DIR ist nicht gesetzt` | `export CLIPS_DIR="$HOME/Downloads/Neuer Ordner"`. Muss in jedem neuen Terminalfenster neu gesetzt werden |
| `No such file or directory` beim Clip | Wurde der Clip verschoben oder umbenannt? Datei zurücklegen oder `clip_info.py` neu laufen lassen und die ID in der `edl` anpassen |
| `ÜBERSPRUNGEN (nicht lesbar)` | Datei kaputt oder liegt nur in iCloud bzw. Google Drive („nur online“). Im Finder einmal öffnen bzw. herunterladen |
| `transcript_m4a.py` stürzt ab (`KeyError` / `json`) | Die Datei hat kein eingebautes Transkript (nur Sprachmemos von neueren iPhones haben eins). Dann `transcribe_whisper.py` nehmen |
| Whisper ist sehr langsam oder der Mac hängt | Kleineres Modell: `python3 tools/transcribe_whisper.py audio.mp4 words.json small` |
| Whisper erkennt Wörter falsch („Hig Ticket“) | In `fixes.json` korrigieren, siehe README Schritt 2 |
| Whisper erfindet am Ende Sätze, die nie gesagt wurden | Diese Wörter in `fixes.json` auf `null` setzen |

## Schnittliste (`cutlist.py`)

| Meldung | Lösung |
|---|---|
| `Clip X bei Ys ist zu kurz` | Den Einstiegspunkt (3. Wert) kleiner machen, den Schnitt früher enden lassen oder einen anderen Clip nehmen |
| `Clip-ID X gibt es nicht` | Tippfehler, oder `clip_info.py` nach dem Hinzufügen neuer Clips nicht ausgeführt |
| `Frames = … (Soll …)` weicht ab | Der letzte Schnitt läuft bis `dur`. Wenn `dur` falsch ist, in `project.json` korrigieren |
| `Expecting ',' delimiter` / `JSONDecodeError` | Fehler in der `project.json`: fehlendes Komma, Komma nach dem letzten Element, `true`/`false` klein schreiben. Prüfen mit `python3 -m json.tool projects/NAME/project.json` |

## Safe Zone (`safezone_check.py`)

| Meldung | Lösung |
|---|---|
| `oben` / `unten` | `y` der Einblendung Richtung 0.45–0.50 setzen |
| `rechte Spalte` / `Rand` | Text kürzer, `size` kleiner (z. B. 150 → 110), oder Untertitel per `hide_caps` ausblenden, wenn sie die Ursache sind |
| Untertitel ragen rechts rein | In `captions.py` weniger Zeichen pro Untertitel (z. B. `3 15` statt `3 17`) |

## Clips schneiden (`cut_segments.py`)

| Problem | Lösung |
|---|---|
| `FEHLER … zscale` / `No such filter: 'zscale'` | ffmpeg ohne zscale, `brew reinstall ffmpeg` |
| `FEHLER … Invalid data` | Der Clip ist beschädigt. Anderen Clip in der `edl` verwenden |
| Abbruch mittendrin (Mac eingeschlafen, Terminal zu) | Einfach `bash run_all.sh projects/NAME` erneut starten. Fertige Segmente werden übersprungen |
| Sehr langsam | 4K-HDR-Clips sind langsam (1–3 s pro Sekunde Video). Den Mac am Netzteil lassen und Ruhezustand verhindern: `caffeinate -i bash run_all.sh projects/NAME` |
| Clip sieht grau/flau oder zu dunkel aus | Es ist ein HDR-Clip, aber `hlg` wurde nicht erkannt. `clip_info.py` neu laufen lassen (dafür den Eintrag aus `data/clipinfo.json` löschen) |

## Basisvideo (`make_base.sh`)

| Meldung | Lösung |
|---|---|
| `erst X von Y Segmenten fertig` | Beim Schneiden ist etwas fehlgeschlagen. Die Ausgabe nach `FEHLER` durchsuchen und `run_all.sh` erneut starten |
| `Frameanzahl stimmt nicht` | `rm -r projects/NAME/segs` und neu starten |

## Effekte rendern (`render_all.sh`)

| Problem | Lösung |
|---|---|
| `TypeError: __init__() got an unexpected keyword argument` | Falscher Feldname bei einer Einblendung. Mit [docs/EFFEKTE.md](docs/EFFEKTE.md) vergleichen |
| `AttributeError: module 'overlay' has no attribute 'XYZ'` | `kind` falsch geschrieben (Groß- und Kleinschreibung beachten: `BigTitle`, nicht `Bigtitle`) |
| `KeyError: 'S20'` | Diesen Untertitel-Stil gibt es nicht, also S1–S19 nehmen |
| `OSError: cannot open resource` | Schrift fehlt. Liegt `tools/fonts/` vollständig vor? Notfalls das Repo neu klonen |
| `fertig: 5 von 8 Stücken` | Einzelne Stücke sind abgestürzt. Die Fehlermeldung darüber lesen und `render_all.sh` erneut starten |
| Mac wird sehr heiß oder langsam | `PARALLEL=2 bash tools/render_all.sh projects/NAME` |
| Änderung an Effekten ist nicht zu sehen | Alte Stücke werden übersprungen. Vorher `rm -r projects/NAME/pieces` |

## Ton (`mix.py`)

| Problem | Lösung |
|---|---|
| `FEHLER: Sound fehlt: …/xyz.wav` | Name in `cues` falsch, oder `bash tools/render_sounds.sh` noch nicht ausgeführt. `ls sounds` zeigt alle Namen |
| Stimme zu leise oder zu laut gegenüber den Effekten | Die dB-Werte in `cues` ändern: −3 = laut, −10 = dezent, −16 = kaum hörbar |
| Ton insgesamt zu leise | Die Ausgabe zeigt `I:` und sollte bei ca. −14 LUFS liegen. Wenn nicht, `"voice_gain": 1.5` in `project.json` setzen |
| Ton und Bild laufen auseinander | `voice_ss` prüfen (Stille am Anfang der Audio). Die Untertitel-Zeiten müssen zur Audio ab `voice_ss` passen |
| Kaching kommt zu früh oder zu spät | Zeitpunkt in `cues` in 0,1-s-Schritten verschieben, nur `mix.py` + `finish.sh` erneut ausführen |

## Fertiges Video

| Problem | Lösung |
|---|---|
| Video lässt sich nicht abspielen | `finish.sh` erneut ausführen. Prüfen mit `ffprobe projects/NAME/final.mp4` |
| Länge stimmt nicht | `dur` in `project.json` prüfen |
| In TikTok unscharf | Beim Hochladen „Hochladen in hoher Qualität“ einschalten. Per AirDrop übertragen, nicht über WhatsApp (das komprimiert) |
| Untertitel in TikTok verdeckt | `safezone_check.py` laufen lassen, siehe oben |

## Speicherplatz

Ein Projekt braucht 1–2 GB (Segmente + Stücke). Wenn das Video fertig ist:

```bash
rm -r projects/NAME/segs projects/NAME/pieces projects/NAME/base.mp4
```

`final.mp4` und `project.json` bleiben erhalten. Mit `project.json` lässt sich das Video jederzeit neu bauen.

## Immer noch kaputt?

1. Den Befehl erneut ausführen und die **komplette Ausgabe** kopieren.
2. Dazu die `project.json` des Projekts.
3. Beides an Claude oder an Erik schicken.

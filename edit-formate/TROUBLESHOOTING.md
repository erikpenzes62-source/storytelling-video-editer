# Edit-Formate – wenn etwas nicht funktioniert

Lies die **Zeile mit `FEHLER`** ganz unten im Terminal und such sie hier. Darüber steht meist die genaue ffmpeg-Meldung.
Du kannst `edit.py` jederzeit neu starten, es baut alles neu.

## Schnellcheck

```bash
cd storytelling-video-editer
source .venv/bin/activate                       # (.venv) muss vorne im Terminal stehen
ffmpeg -hide_banner -filters | grep zscale      # muss eine Zeile ausgeben (für iPhone-HDR)
python3 -c "import librosa, soundfile, pyloudnorm, PIL; print('ok')"
ls tools/fonts                                  # ArchivoBlack, BebasNeue, Anton, Montserrat, Poppins …
python3 -m json.tool projects/NAME/edit.json > /dev/null && echo "JSON ok"
```

## Einrichtung

| Problem | Lösung |
|---|---|
| `FEHLER: Python-Paket fehlt (…)` / `ModuleNotFoundError` | `source .venv/bin/activate`, dann `pip install -r requirements.txt` |
| `FEHLER: librosa fehlt` | `pip install librosa matplotlib` (bei aktiver .venv) |
| `zscale` fehlt / HDR-Clips sehen grau, flau oder viel zu hell aus | `brew reinstall ffmpeg` (die Homebrew-Version hat zscale) |
| `command not found: ffmpeg` | `brew install ffmpeg` |

## edit.json

| Meldung | Lösung |
|---|---|
| `JSONDecodeError` / `Expecting ',' delimiter` | Tippfehler in der edit.json: Komma fehlt, Komma nach dem letzten Element, `true`/`false`/`null` klein schreiben. Prüfen mit `python3 -m json.tool projects/NAME/edit.json` |
| `FEHLER: Datei nicht gefunden: …` | Pfad stimmt nicht. Pfade sind relativ zum Ordner der edit.json. Groß-/Kleinschreibung prüfen (`IMG_1.MOV` ≠ `IMG_1.mov`) |
| `FEHLER: Clip nicht gefunden: …` | Clip liegt nicht in `clips_dir` oder heißt anders |
| `FEHLER: Shots (…) sind länger als die Musik` | Summe der Beats bei `shots` ist größer als die Musik. Beats kürzen oder in `music` das Ende später setzen. Der letzte Shot sollte `"rest"` sein |
| `FEHLER: Musik vor dem Drop reicht nicht` | Das Gespräch ist länger als der Song vor dem Drop. In `bed` eine feste `start`-Zahl setzen (z. B. `0`) oder einen späteren Drop nehmen |
| `KeyError: 'X'` bei `sub_style` | Nur `1A`, `1C`, `2`, `5`, `8`, `9` gibt es |
| `KeyError: 'subs'` | Zuerst `python3 edit-formate/untertitel.py projects/NAME/edit.json` ausführen |

## Beim Rendern

| Problem | Lösung |
|---|---|
| `FEHLER bei: Shot N (…)` | Meist ist der Start im Clip zu spät, der Clip ist zu kurz für die Länge. Startzeit kleiner machen oder bei Zeitlupe (`0.25`) einen längeren Clip nehmen. Die ffmpeg-Meldung darüber zeigt die Details |
| Shot ist schwarz oder eingefroren | Wie oben: Start + Länge × Tempo ist länger als der Clip. Clip-Länge prüfen mit `ffprobe -v error -show_entries format=duration -of csv=p=0 clip.mov` |
| `Error opening input` / `moov atom not found` | Datei kaputt oder liegt nur in iCloud bzw. Google Drive („nur online“). Im Finder einmal öffnen bzw. herunterladen |
| `FEHLER: keine Tonspur` / `keine lesbare Tonspur` | Das Grundvideo oder der Sound hat keinen Ton, oder nur eine Spur, die ffmpeg nicht kennt. Mit Quicktime als `.mov`/`.mp4` neu exportieren |
| Untertitel in falscher Schrift | Schrift fehlt in `tools/fonts`. Repo neu holen (`git pull`) |
| `FEHLER bei: Endmontage` mit `subtitles` | Der Pfad hat Sonderzeichen. Projektordner ohne Leerzeichen und Umlaute benennen (`projects/nein`, nicht `projects/Nein Edit ä`) |
| Sehr langsam | 4K-HDR-Clips sind langsam. Normal sind 1–3 Minuten pro Edit auf einem MacBook |

## Ergebnis gefällt nicht

| Problem | Lösung |
|---|---|
| Edit kommt nicht genau auf den Drop | `sound_analyse.py` nochmal laufen lassen und im Bild prüfen, wo die rote Linie (Drop) liegt. Den Wert bei `music` auf 0,01 s genau eintragen |
| Schnitte nicht im Takt | `beat` stimmt nicht. Der Wert aus `sound_analyse.py` (Beat-Abstand) kommt in `beat`. Wenn das Tempo doppelt oder halb erkannt wurde, den Wert ×2 oder ÷2 nehmen |
| Musik unter dem Gespräch zu laut | `bed.lufs` kleiner machen (−28 → −30) |
| Man hört den Drop nicht deutlich | `bed.cut` oder `bed.cut_before_drop: 0.4` setzen, damit vorher kurz Stille ist |
| Untertitel über Gesichtern | Anderen `sub_style` nehmen (`1A`/`1C` oben links, `2`/`9` unten, `5`/`8` Mitte) |
| Falsch erkannte Wörter | In der edit.json unter `subs` direkt korrigieren. Zum Neu-Transkribieren `words.json` im Projektordner löschen und `untertitel.py` neu starten. Mit `WHISPER_MODEL=small` geht es schneller, ist aber ungenauer |
| Ein Sprung im Gespräch fällt auf | Beim Stück nach dem Sprung einen Zoom eintragen: `[start, ende, 1.08]` |

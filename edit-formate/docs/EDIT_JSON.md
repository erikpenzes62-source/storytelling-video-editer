# edit.json – alle Felder

Pfade sind relativ zum Ordner der `edit.json` (oder absolut).

| Feld | Beispiel | Bedeutung |
|---|---|---|
| `name` | `"Nein_Chaotisch"` | Name, auch für den Arbeitsordner `_work_NAME` |
| `out` | `"fertig/Edit_Nein.mp4"` | Ausgabedatei |
| `base` | `"grundvideo/IMG_5564.mov"` | Das Grundvideo (Gespräch) |
| `clips_dir` | `"clips"` | Ordner mit dem Edit-Material |
| `sound` | `"sound/song.mp3"` | Der Song |
| `talk` | `[[0, 6.4]]` | Stücke vom Grundvideo: `[start, ende, zoom?, ton_ende?]` |
| `subs` | (von `untertitel.py`) | Untertitel: `[stück, [[WORT, zeit, farbig], …], ende]` |
| `sub_style` | `"1C"` | Untertitel-Stil: `1A`, `1C`, `2`, `5`, `8`, `9` |
| `sub_speed` | `"slow"` | `slow` (Standard) = ganze Phrase auf einmal, mind. ~1 s sichtbar, gut lesbar. `fast` = Wort für Wort |
| `style` | `"cine"` | Look im Edit-Teil: `cine`, `chaos`, `vivid`, `doku` |
| `fog` | `true` | Weißer Nebel-Übergang vom Gespräch ins Edit (für Cinematic) |
| `music` | `[[13.42, 19.12]]` | Song-Stück für das Edit: `[[drop, ende]]` (mehrere Stücke möglich, werden aneinandergehängt) |
| `beat` | `0.597` | Sekunden pro Beat (aus `sound_analyse.py`) |
| `edit_lufs` | `-9` | Lautstärke des Edit-Teils (−9 = laut, so wie in den Musterlösungen) |
| `bed` | siehe unten | Hintergrundmusik unter dem Gespräch |
| `shots` | siehe unten | Die Clips im Edit |
| `keep_work` | `true` | Arbeitsordner behalten (nur zur Fehlersuche) |

## bed – Musik unter dem Gespräch

```json
"bed": {"start": "auto", "lufs": -28, "lowpass": 5000, "cut": 5.70}
```

- `start`: `"auto"` heißt, die Musik läuft so, dass sie genau am Drop ankommt, also der Teil des Songs **vor** dem Drop. Ist das Gespräch länger als dieser Teil, wird der Song-Anfang davor automatisch wiederholt. Alternativ eine Sekundenzahl im Song.
- `lufs`: Lautstärke. **−28 ist der Standard**, damit man das Reden gut versteht. Lauter wäre −24, leiser −30.
- `lowpass`: macht die Musik etwas dumpfer (5000 = leicht, 1500 = stark). `null` heißt aus.
- `cut`: ab welcher Sekunde (im fertigen Video) die Musik rausgeht, z. B. genau bei der Pointe. `null` heißt, sie läuft durch (gut, wenn der Song vor dem Drop selbst eine Pause hat).
- `cut_before_drop`: Alternative zu `cut`, z. B. `0.3` = Musik geht 0,3 s vor dem Drop raus.

## shots – die Clips

```json
["IMG_4265.mov", 0.3, 1.5, 1, ["zb_in", "pulse"]]
```

`[Clip, Start im Clip in s, Länge in Beats oder "rest", Tempo, [Effekte]]`

- Clip `"BASE"` = Stück aus dem Grundvideo
- Tempo `0.5` / `0.25` = Zeitlupe

## Effekte

Alle Effekte sind sauber, ohne Wackeln. Mehrere pro Shot sind möglich.

| Effekt | Was passiert | Typisch für |
|---|---|---|
| `zout` | langsam rauszoomen über den ganzen Shot | Cinematic |
| `zin` | langsam reinzoomen | Cinematic, Hero-Shot am Ende |
| `punch` | fest 14 % reingezoomt | Chaotisch |
| `steps` | Zoom springt pro halbem Beat eine Stufe größer | Chaotisch, Geld-Shots |
| `pulse` | Zoom + Aufhellen auf jedem Beat, federt zurück | Geldwurf |
| `zb_in` | Zoom-Blur-Übergang **in** den Shot | Chaotisch |
| `zb_out` | Zoom-Blur am **Ende** des Shots (mit `zb_in` beim nächsten = Zoom-Übergang) | Chaotisch |
| `whip_out` + `whip_in` | Wisch-Übergang (seitliche Unschärfe) | alle |
| `dip_out` + `dip_in` | kurzes Aufblenden in Weiß zwischen zwei Shots | Cinematic |
| `fog_in` | Nebel-Weiß rein (erster Shot nach dem Drop, mit `"fog": true`) | Cinematic |
| `flash` | weißer Flash auf dem Schnitt (2 Frames) | Drop, Chaotisch |
| `flash1` | einzelner weißer Flash-Frame | Chaotisch |
| `overexp` | kurz überbelichtet am Anfang | letzter Shot |
| `keepaudio` | Originalton leise mitlaufen lassen (nur bei `"BASE"`) | Jubel nach der Pointe |

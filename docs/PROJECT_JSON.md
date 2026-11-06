# `project.json`: Aufbau

Jedes Video hat eine `project.json` in seinem Projektordner. Alle Zeiten sind **Sekunden im fertigen Video**.

```json
{
  "voice": "voice.m4a",
  "voice_ss": 0.0,
  "dur": 78.6,
  "style": "S17",
  "hook": {"end": 1.8, "impacts": [1.35], "cuts": [], "zoom": 0.0},
  "edl": [[0.0, 72, 2.0], [2.2, 84, 0.5], [4.26, 52, 2.0]],
  "inserts": [ {"kind": "SlotNumber", "t0": 0.0, "t1": 4.2, "text": "2.595 €", "lock0": 0.9, "y": 0.50} ],
  "hide_caps": [[0.0, 4.26]],
  "cues": [[1.35, "cut_hit_punch", -3]],
  "ban_clips": [12, 16]
}
```

| Feld | Bedeutung |
|---|---|
| `voice` | Audiodatei im Projektordner |
| `voice_ss` | Ab welcher Sekunde der Audio das Video beginnt (Stille am Anfang wegschneiden) |
| `dur` | Länge des Videos in Sekunden (≈ Ende des letzten Worts + 0,5 s) |
| `style` | Untertitel-Stil, siehe [EFFEKTE.md](EFFEKTE.md#untertitel-stile). Pro Video einen anderen nehmen |
| `hook` | Kamerabewegung am Anfang: `end` = bis wann, `zoom` = Push-in (0.04 = 4 %), `impacts` = Zeitpunkte mit Blitz und Wackler |
| `edl` | **Schnittliste**: `[startzeit, clip_id, einstieg_im_clip]`, optional `[…, 0.5]` als 4. Wert für Zeitlupe. Jeder Eintrag läuft bis zum Start des nächsten |
| `inserts` | Einblendungen, siehe [EFFEKTE.md](EFFEKTE.md) |
| `hide_caps` | Zeitbereiche ohne Untertitel, z. B. während einer großen Zahl (ein Fokuspunkt) |
| `cues` | Soundeffekte: `[zeitpunkt, "soundname", lautstärke_dB]`. `soundname` = Datei in `sounds/` ohne `.wav`. Typisch −3 (laut) bis −16 dB (leise) |
| `ban_clips` | Clip-IDs, die nicht verwendet werden sollen (gibt eine Warnung) |
| `voice_gain` | Optional: Lautstärke der Stimme vor dem Mastern (Standard 1.0) |

## Schnittliste planen

- Pro Satz oder Satzteil ein Schnitt, also etwa alle **2–3 Sekunden**. Geschnitten wird **an Satzgrenzen**, nimm dafür die Zeiten aus der `captions.py`-Ausgabe.
- Der Clip muss **zum Gesagten passen** (Auto bei „Lambo“, Laptop bei „Business“, Gym bei „Disziplin“).
- **Helligkeit fließend**: `cutlist.py` zeigt den Verlauf. Dunkel → hell steigern, nie hart hin und her springen.
- `cutlist.py` meldet, wenn ein Clip zu kurz ist. Dann den Einstiegspunkt früher setzen oder einen anderen Clip nehmen.

## Typischer Ablauf bei Änderungen

| Du änderst … | Danach neu ausführen |
|---|---|
| Untertitel (`fixes.json`) | `captions.py`, dann `rm -r pieces` und `render_all.sh` + `finish.sh` |
| Einblendungen (`inserts`, `hide_caps`, `style`, `hook`) | `rm -r pieces`, dann `render_all.sh` + `finish.sh` |
| Sounds (`cues`) | nur `mix.py` + `finish.sh` |
| Schnitte (`edl`) | `rm -r segs pieces`, dann `run_all.sh` |

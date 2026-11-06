# Effekte und Untertitel-Stile

Alle Einblendungen kommen in `project.json` → `"inserts": [...]`. Jede hat `kind`, `t0` (Start) und `t1` (Ende) in Sekunden. `y` ist die Höhe als Anteil des Bildes (0.50 = Mitte). Farben werden als `[R, G, B]` angegeben: Grün `[34,197,94]`, Rot `[239,68,68]`, Weiß `[255,255,255]`.

**Empfohlene Position:** `y` 0.45–0.50, also direkt über den Untertiteln (die stehen bei 0.68). So gibt es einen einzigen Blickpunkt.

## Die bewährten Effekte (Dopamin-Kick)

### BalanceCard: Kontostand zählt hoch
```json
{"kind": "BalanceCard", "t0": 3.3, "t1": 11.0, "v0": 184, "v1": 1840, "t_count": 6.9, "t_end": 8.9,
 "label0": "KONTOSTAND", "label1": "3 WOCHEN SPÄTER", "badge": "×10", "y": 0.50}
```
Zeigt `v0`, zählt ab `t_count` bis `t_end` auf `v1` und wird dann grün. Das Badge springt rein, `"badge": ""` blendet es aus.
Sounds: `pro_typing_run_soft` beim Zählen (−11), `cut_hit_punch` (−3) + `shimmer_m2` (−15) bei `t_end`.

### SlotNumber: Zahl rattert wie ein Spielautomat
```json
{"kind": "SlotNumber", "t0": 0.0, "t1": 4.2, "text": "2.595 €", "lock0": 0.9, "lock_dt": 0.15, "y": 0.50, "size": 150, "col_end": [34,197,94]}
```
Die Ziffern rasten ab `lock0` nacheinander ein. Ideal als Hook in den ersten Sekunden, dabei die Untertitel per `hide_caps` ausblenden.

### BigTitle: große Zahl oder Aussage
```json
{"kind": "BigTitle", "t0": 47.5, "t1": 50.5, "text": "30–40.000 €", "sub": "JEDEN MONAT", "y": 0.50, "size": 110, "col": [34,197,94], "punch": 47.6}
```
`punch` = Zeitpunkt für einen kurzen Größen-Schlag. Rot mit „0,00 €“ funktioniert gut bei „nichts verdient“.

### Checklist: Haken und Kreuze
```json
{"kind": "Checklist", "t0": 40.8, "t1": 44.9, "items": [["Produkt", 41.04, false], ["Startkapital", 41.76, false], ["Handy", 43.08, true]], "y": 0.45}
```
Jede Zeile erscheint zu ihrer Zeit: `false` = rotes ✗, `true` = grünes ✓. Sounds: `pro_pop_in_round` (−5) je Zeile, `toggle_on` + `mallet_up4` beim Haken.

### Chips: Aufzählung, die durchgestrichen wird
```json
{"kind": "Chips", "t0": 28.0, "t1": 34.0, "items": [["Dropshipping", 28.26], ["Trading", 29.1]], "strike": 32.28,
 "label": "HIGH TICKET SALES", "label_col": [34,197,94], "y": 0.50}
```
Sounds: `pro_pop_in_round` je Chip, `whoosh_fast_tight` beim Durchstreichen.

### Stamp: Stempel knallt drauf
```json
{"kind": "Stamp", "t0": 35.5, "t1": 36.65, "text": "SCAM", "y": 0.50}
```
Sound: `cut_hit_punch` (−3) + `pro_sub_drop_quick` (−10).

### CommentCard: Kommentar-Kärtchen
```json
{"kind": "CommentCard", "t0": 37.7, "t1": 40.9, "items": [["Ich, früher", "Fake.", 37.92], ["Ich, früher", "Alles gekauft.", 38.64]], "y": 0.45}
```
Sound: `notify_m2` (−9) je Kommentar. Keine echten Namen verwenden.

### WordPop: ein großes Wort nach dem anderen
```json
{"kind": "WordPop", "t0": 30.3, "t1": 34.6, "words": [["KRYPTO", 30.42], ["TRADING", 31.26], ["DROPSHIPPING", 32.16]], "y": 0.50, "size": 110}
```
Sound: `tap_glass` (−8) je Wort.

### BarCompare: Vorher/Nachher-Balken
```json
{"kind": "BarCompare", "t0": 4.5, "t1": 8.4, "l0": "VOR 1 JAHR", "v0txt": "< 1.873 €", "t_a": 7.4, "l1": "HEUTE", "v1txt": "18.732 €", "t_b": 4.6, "y": 0.47}
```

## Weitere Effekte (sparsam einsetzen)

| kind | Wofür | Wichtige Felder |
|---|---|---|
| `StrikeTitle` | Großer Titel, der durchgestrichen wird (Anti-Hook) | `text`, `strike` |
| `StackTitle` | Zeilen stapeln sich (MARKETING / VERTRIEB) | `lines` |
| `DigitalAlarm` | Digitaluhr 05:59 → 06:00 | `flip`, `s0`, `s1` |
| `AnalogClock` | Wecker tickt auf 6:00 und klingelt | `ring` |
| `SpinClock` | Uhr rast („die Zeit läuft weg“) | – |
| `Payday` | Kalender „15.“ + Gehalt läuft leer | `chips`, `day` |
| `DayCard` | Kalenderblatt mit Umsatz, der hochzählt | `day`, `label`, `v1`, `t_count`, `t_end` |
| `PauseFreeze` | Pause-Symbol, Bild wird grau („Warte mal“) | `label` |
| `FakeSwipe` | Bild wird weggewischt und springt zurück | `amt` |
| `SplitLabels` | FRÜHER / HEUTE bei geteiltem Bild | `top`, `bottom` |
| `VideoCounter` | „VIDEO #1 … #100“ | `steps` |
| `LockScreen`, `GridReveal`, `EuroBurst`, `StationBoard` | Vorhanden, kamen aber **nicht gut an**, nicht verwenden |
| `VHS`, `FilmLabel`, `Sticker` | **Nicht verwenden** (Retro-Look und Emoji wirken billig) |

Die genaue Funktionsweise steht im Code: `tools/overlay.py`, eine Klasse pro Effekt.

## Untertitel-Stile

In `project.json` → `"style"`. **Pro Video wechseln**, nie zweimal hintereinander denselben.

| Stil | Schrift | Keyword-Farbe | Animation |
|---|---|---|---|
| S1 | Anton 50, Großbuchstaben | Gelb | Wort gleitet hoch |
| S2 | Poppins 38, Großbuchstaben | Grün | Karaoke-Kasten |
| S3 | Montserrat Black 40 | Orange | Bounce |
| S4 | Barlow Condensed 46 | Rot | Dunkler Balken |
| S5 | Barlow Condensed 46 | Blau | Pill |
| S6 | Poppins 40 | Gelb | Textmarker (lief viral) |
| S7 | Montserrat 40 | Mintgrün | Fade |
| S8 | Montserrat Black Italic | Weiß invertiert | Invertiert |
| S9 | Barlow 48 | Orange | Zoom |
| S10 | Poppins 38 | Pink | Schreibmaschine |
| S11 | Barlow 50 | Hellblau | Glow |
| S12 | Montserrat 34, Großbuchstaben | Rot | Keyword auf rotem Kasten |
| S13 | Montserrat 34 | Pink | schlicht |
| S14 | Poppins 34 | Blau | schlicht |
| S15 | Poppins 36 | Limette | dunkle Pill |
| S16 | Montserrat 34 | Gelb | schlicht |
| S17 | Montserrat 34, Großbuchstaben | Blau | Keyword auf blauem Kasten |
| S18 | Poppins 34 | Orange | schlicht |
| S19 | Barlow 44, Großbuchstaben | Grün | schlicht |

## Sounds

Nach `setup.sh` liegen diese Sounds in `sounds/`: `whoosh_fast_crisp`, `whoosh_fast_tight`, `whoosh_big_thump`, `pro_whoosh_big_swell`, `cut_hit_punch`, `pro_impact_short`, `impact_punch`, `pro_sub_drop_quick`, `riser_build`, `pro_riser_roll`, `shutter_dslr`, `shutter_quick`, `pro_pop_in_round`, `ui_pop_blip`, `pro_notify_ding_2045`, `notify_m2`, `shimmer_m2`, `pro_typing_run_soft`, `tap_glass`, `pro_tap_finger`, `swipe_flick`, `toggle_on`, `mallet_up4`, `pro_zip_up`, `click_snap`.

Weitere 227 Sounds findest du mit `earshot sfx list`.

**Kaching:** Das Original-„Kaching“ eines Digistore-Banners aus einem eigenen Clip speichern:
```bash
bash tools/extract_sound.sh "$CLIPS_DIR/IMG_1234.MP4" 0.0 2.0 kaching1
```
Dann in `cues` als `[zeitpunkt, "kaching1", 2]` verwenden. Der Zeitpunkt muss genau zum Banner im Clip passen.

# Stilregeln für Edit-Formate

Diese Regeln kommen aus Eriks Feedback zu vielen Testversionen. Sie gelten für jedes Edit.

## Aufbau

- **Erst den Inhalt des Grundvideos verstehen.** Erzählt das Grundvideo die Geschichte selbst (kurz, ein Moment), wird **nicht** zwischendurch geschnitten. Höchstens am Ende minimal kürzen. Nur lange Gespräche (wie beim 12.000-€-Video) werden gekürzt, sodass die Pausen rausfallen.
- **Das Grundvideo endet direkt nach der Pointe**, dem Satz mit Aura („12.000 € an einem Tag“, „Nein.“). Danach kommt sofort der Drop.
- **Unter dem Grundvideo läuft Hintergrundmusik** (für die Aufmerksamkeit), aber leise (`bed.lufs` −28), damit man das Reden gut versteht.
- **Kurz vor dem Drop ist die Musik weg** (0,3–0,7 s Stille), dann setzt der Drop ein. Das Edit muss **genau auf dem Beat-Drop** starten.
- **Das Edit zeigt, was gesagt wurde.** Geht es um Geld oder Verdienst, kommen Dashboard, Benachrichtigungen, Geld, Lifestyle. Nicht jeder Clip muss rein.
- **Am Ende ein Hero-Shot**, der etwas länger stehen bleibt (Cinematic 2 s+, Chaotisch ca. 1 s), dann harter Schluss.
- **Immer zwei Varianten** pro Grundvideo, mit verschiedenen Edit-Formaten und Untertitel-Stilen.

## Sound

- Der Sound muss zur **Stimmung der Clips** passen. Clips zum Angeben oder Feiern brauchen einen fröhlichen oder hypen Sound, **keinen düsteren** Rap und keinen dunklen Sound.
- Der Edit-Teil ist laut (`edit_lufs` −9), ungefähr 8–10 dB lauter als das Gespräch.

## Effekte

- **Kein Wackeln / Shake.** Nur saubere Effekte.
- **Keine dunkle Vignette** (das Einkreisen am Rand).
- **Kein Schwarz-Weiß.**
- **Übergänge benutzen:** Wisch, Zoom-Blur, Weiß-Blende, Nebel.
- **Nicht zu schnell schneiden:** meistens 1 Beat pro Clip, halbe Beats nur ab und zu.

## Edit-Formate (zum Abwechseln)

| Format | `style` | Merkmale |
|---|---|---|
| **Cinematic** | `cine` | Nebel-Weiß beim Drop, jeder Shot zoomt langsam rein oder raus, Teal-Orange-Look, Zeitlupe, 1–2 Beats pro Shot, Hero-Shot am Ende |
| **Chaotisch** | `chaos` | Flash-Frames, Zoom-Blur, Punch-ins, Stufen-Zoom, Zoom mit Aufhellen (`pulse`) beim Geldwurf, 0,5–1 Beat pro Shot |
| **Beat-Cut** | `vivid` | 1 Shot pro Beat, Wisch-Übergänge, Drop auf einem Moment aus dem Grundvideo (z. B. Geldwurf mit `"BASE"` + `keepaudio`) |

## Untertitel-Stile (Eriks Favoriten)

| `sub_style` | Aussehen | passt zu |
|---|---|---|
| `1A` | **Ferrari-Block:** Wörter oben links, max. 2 Zeilen eng übereinander, jede Zeile gleich breit gezogen, leicht 3D, Keywords Cyan | ruhige, längere Sätze, freie Fläche oben links |
| `1C` | **Ferrari-Einzelwort:** ein Wort groß oben links, leicht 3D, Keywords Cyan | schnelles Reden, kurze Grundvideos |
| `2` | **Klassik:** fett, Großbuchstaben, Wort für Wort aufbauend, unten, Keywords gelb | immer passend |
| `5` | **Rot (Anton):** ein Wort in der Mitte | Chaotisch |
| `8` | **Bebas groß** mit Schatten, Keywords gelb | Cinematic |
| `9` | **Zwei Zeilen:** Satz klein, aktuelles Wort groß darunter | Zahlen-Momente |

Nicht gewünscht: Karaoke grün, weiß auf schwarzer Box, Doku klein gelb, schlicht weiß, kursiver Balken.

**Damit es clean aussieht:** Text nur dort, wo im Bild nichts los ist (nicht über Gesichtern), höchstens 2 Zeilen, nur **eine** Akzentfarbe pro Video.

# Stilregeln

Diese Regeln stammen aus Eriks Feedback und den Videos, die gut performt haben. Wer neue Videos schneidet, hält sich daran.

## Was viral ging (der Standard-Stil)

- **Schnitt alle 2–3 Sekunden** mit Clips, die zum Satz passen.
- **Wenige, starke, emotionale Einblendungen** mit kleinem Dopamin-Kick. Beispiele: Ein Kontostand zählt hoch und wird grün mit „×10“-Badge, grüne Haken, Begriffe werden durchgestrichen, ein rotes „0,00 €“ bei „nichts verdient“, das Original-Kaching beim Verkauf.
- **Starker Hook in den ersten 1–3 Sekunden**, meist eine große Zahl. Die Hook-Art von Video zu Video variieren.
- Jedes Video **ähnlich, aber nie gleich**: andere Clips, ein anderer Untertitel-Stil, andere Effekte. Immer nur **kleine Änderungen**, nie alles auf einmal umwerfen.

## Regeln für Einblendungen

1. **Safe Zone (1080 × 1920):** Nichts gehört in diese Bereiche:
   - oben y < 220 (Statusleiste, „Folge ich / Für dich“)
   - unten y > 1545 (Beschreibung, Name, Musik)
   - rechts x > 900 für y 970–1545 (Profilbild, Likes, Kommentare, Teilen)
   - an die Ränder

   `safezone_check.py` prüft das automatisch.
2. **Ergänzen statt wiederholen:** Die Einblendung unterstreicht das Gesagte visuell, mit einer Zahl, einem Haken oder einem Symbol. Kein Fließtext.
3. **Nur Stichpunkte:** höchstens 1–3 Wörter pro Element.
4. **Ein Fokuspunkt:** Nie gleichzeitig oben, in der Mitte und unten etwas zeigen. Die Einblendung steht direkt über den Untertiteln (y 0.45–0.50), oder die Untertitel werden währenddessen ausgeblendet.

## Untertitel

- **Klein**, denn auf dem Handy wirkt alles größer: 34–50 px je nach Schrift, höchstens 520 px breit, bei **68 % der Bildhöhe**.
- 1–4 Wörter pro Untertitel, getrennt an Satzgrenzen.
- Höchstens ein farbiges Keyword (oder ein Paar) pro Untertitel.
- Weiße Schrift nie auf weißem Hintergrund, also keine hellen Handy-Screens hinter den Untertiteln.
- Clips meiden, deren eingebrannter Text dort sitzt, wo die Untertitel stehen.

## Sound

- **Keine Musik**, die kommt in TikTok dazu.
- Soundeffekte nur an **großen Momenten**, nicht auf jeden Schnitt (das wirkt billig).
- **Kamera-Auslöser** (`shutter_dslr`) beim Wechsel ins „alte Leben“.
- **Original-Kaching** aus dem Clip, wenn ein Digistore-„Neuer Verkauf“-Banner reinkommt.
- Lautstärke wird automatisch auf **−14 LUFS** gemastert, True Peak ≤ −1 dBTP.

## Clips

- **Nur Hochformat**, nie mit Querformat mischen.
- **Helligkeit fließend:** Einstieg dunkel oder nachts → heller; negative Passagen dunkler, Erfolg hell, am Ende Sonnenuntergang. Nie hart hin und her springen und Clips nie künstlich abdunkeln.
- **Alte Clips** (früheres Ich) nur dort, wo die Audio über das frühere Leben spricht, dann 2–3 kurze Clips am Stück mit Auslöser-Sound. Danach sofort zurück zu Clips aus dem neuen Leben.
- **Nichts mit Feiern** (Club, Drinks, Zigarre): Die Persona ist ein disziplinierter Businessman.
- Redet die Audio am Anfang direkt den Zuschauer an, die Person kurz selbst zeigen und dann erst in einen Effekt wechseln.

## Nicht verwenden

- VHS- oder Camcorder-Look, Schwarz-Weiß-Filmlook, Filmstreifen
- Emoji-Sticker
- Viele neue Effekte auf einmal (Sperrbildschirm + Raster + €-Regen + Abfahrtstafel in einem Video kam schlecht an)
- Zahlen einblenden, die einer im Clip sichtbaren Zahl widersprechen

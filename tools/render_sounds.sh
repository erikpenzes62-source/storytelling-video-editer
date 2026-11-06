#!/usr/bin/env bash
# Rendert die Soundeffekte mit earshot (https://github.com/Leonxlnx/earshot, MIT-Lizenz) nach sounds/.
# Aufruf:  bash tools/render_sounds.sh      (einmalig nach setup.sh)
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; OUT="${SFX_DIR:-$ROOT/sounds}"; mkdir -p "$OUT"
command -v earshot >/dev/null || { echo "FEHLER: earshot nicht installiert – erst bash setup.sh ausführen (und venv aktivieren: source .venv/bin/activate)"; exit 1; }
for s in whoosh_fast/crisp whoosh_fast/tight whoosh_big/thump pro_whoosh_big/swell cut_hit/punch pro_impact/short impact/punch \
         pro_sub_drop/quick riser/build pro_riser/roll shutter/dslr shutter/quick pro_pop_in/round ui_pop/blip pro_notify/ding_2045 \
         notify/m2 shimmer/m2 pro_typing_run/soft tap/glass pro_tap/finger swipe/flick toggle/on mallet/up4 pro_zip/up click/snap; do
  f="$OUT/$(echo $s | tr / _).wav"
  [ -f "$f" ] || earshot sfx render "$s" --sr 48000 -o "$f" >/dev/null && echo "ok $f"
done
echo "Weitere Sounds: earshot sfx list  (252 Stück) – rendern mit: earshot sfx render ID --sr 48000 -o sounds/NAME.wav"

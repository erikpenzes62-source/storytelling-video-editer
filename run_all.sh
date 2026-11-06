#!/usr/bin/env bash
# Kompletter Ablauf für ein Projekt, sobald project.json + chunks.json stehen.
# Aufruf:  bash run_all.sh projects/NAME
# Jeder Schritt ist fortsetzbar: bricht etwas ab, einfach dasselbe Kommando nochmal starten.
set -e
P="$1"; T="$(cd "$(dirname "$0")" && pwd)/tools"
[ -f "$P/project.json" ] || { echo "FEHLER: $P/project.json fehlt"; exit 1; }
[ -f "$P/chunks.json" ] || { echo "FEHLER: $P/chunks.json fehlt (Schritt 2: tools/captions.py)"; exit 1; }
echo "== 1/6 Schnittliste prüfen";  python3 "$T/cutlist.py" "$P"
echo "== 2/6 Safe Zone prüfen";     python3 "$T/safezone_check.py" "$P"
echo "== 3/6 Clips schneiden"
python3 "$T/cut_segments.py" "$P" 0 3 & python3 "$T/cut_segments.py" "$P" 1 3 & python3 "$T/cut_segments.py" "$P" 2 3 & wait
echo "== 4/6 Basisvideo";           bash "$T/make_base.sh" "$P"
echo "== 5/6 Effekte + Untertitel"; bash "$T/render_all.sh" "$P"
echo "== 6/6 Ton + fertiges Video"; python3 "$T/mix.py" "$P"; bash "$T/finish.sh" "$P"

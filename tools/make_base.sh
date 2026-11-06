#!/usr/bin/env bash
# Segmente zu einem Basisvideo (ohne Ton, ohne Effekte) zusammenfügen und Frameanzahl prüfen.
# Aufruf:  bash tools/make_base.sh projects/NAME
set -e
P="$(cd "$1" && pwd)"
n=$(python3 -c "import json;print(len(json.load(open('$P/cut.json'))))")
have=$(ls "$P/segs" 2>/dev/null | grep -v '\.tmp\.mp4$' | grep -c '\.mp4$' || true)
if [ "$have" -lt "$n" ]; then echo "FEHLER: erst $have von $n Segmenten fertig – cut_segments.py nochmal starten"; exit 1; fi
ls "$P"/segs/s*.mp4 | grep -v '\.tmp\.mp4$' | sort | sed "s|^|file '|;s|$|'|" > "$P/segs.txt"
ffmpeg -v error -y -f concat -safe 0 -i "$P/segs.txt" -c copy "$P/base.mp4"
got=$(ffprobe -v error -count_packets -select_streams v -show_entries stream=nb_read_packets -of csv=p=0 "$P/base.mp4")
want=$(python3 -c "import json;print(sum(c['n'] for c in json.load(open('$P/cut.json'))))")
echo "base.mp4: $got Frames (Soll $want)"
[ "$got" = "$want" ] || echo "WARNUNG: Frameanzahl stimmt nicht – Segmente löschen und neu schneiden"

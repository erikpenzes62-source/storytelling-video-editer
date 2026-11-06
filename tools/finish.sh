#!/usr/bin/env bash
# Stücke + Ton zum fertigen Video zusammenfügen, prüfen und Kontaktbogen erstellen.
# Aufruf:  bash tools/finish.sh projects/NAME  -> projects/NAME/final.mp4 + check.jpg
set -e
P="$(cd "$1" && pwd)"; NAME=$(basename "$P")
ls "$P"/pieces/*.mp4 | grep -v '\.tmp\.mp4$' | sort | sed "s|^|file '|;s|$|'|" > "$P/pieces.txt"
ffmpeg -v error -y -f concat -safe 0 -i "$P/pieces.txt" -i "$P/audio_mix.m4a" -map 0:v -map 1:a -c copy -shortest -movflags +faststart "$P/final.mp4"
d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$P/final.mp4")
fps=$(ffprobe -v error -select_streams v -show_entries stream=r_frame_rate -of csv=p=0 "$P/final.mp4")
want=$(python3 -c "import json;print(json.load(open('$P/project.json'))['dur'])")
echo "final.mp4: ${d}s (Soll ${want}s), fps ${fps}, $(du -h "$P/final.mp4" | cut -f1)"
ffmpeg -v error -y -i "$P/final.mp4" -vf "fps=16/$d,scale=180:320,tile=8x2" -frames:v 1 "$P/check.jpg"
echo "Kontaktbogen: $P/check.jpg  (16 Bilder über das ganze Video – Helligkeit, Untertitel, Einblendungen prüfen)"

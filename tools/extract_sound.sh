#!/usr/bin/env bash
# Originalton aus einem Clip als Sound speichern (z. B. das Digistore-"Kaching").
# Aufruf:  bash tools/extract_sound.sh "/Pfad/Clip.MP4" START_SEKUNDE LÄNGE NAME
# Beispiel: bash tools/extract_sound.sh "$CLIPS_DIR/IMG_1234.MP4" 0.0 2.0 kaching1   -> sounds/kaching1.wav
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; OUT="${SFX_DIR:-$ROOT/sounds}"; mkdir -p "$OUT"
ffmpeg -v error -y -ss "$2" -t "$3" -i "$1" -vn -ac 2 -ar 48000 -af "afade=t=out:st=$(python3 -c "print(max(0,$3-0.4))"):d=0.4" "$OUT/$4.wav" && echo "-> $OUT/$4.wav"

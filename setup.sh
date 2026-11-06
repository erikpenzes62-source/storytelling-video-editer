#!/usr/bin/env bash
# Einmalige Einrichtung (macOS oder Linux). Aufruf im Repo-Ordner:  bash setup.sh
set -e
cd "$(dirname "$0")"
command -v ffmpeg >/dev/null || { echo "FEHLER: ffmpeg fehlt. macOS: brew install ffmpeg  |  Linux: sudo apt install ffmpeg"; exit 1; }
command -v python3 >/dev/null || { echo "FEHLER: python3 fehlt. macOS: brew install python  |  Linux: sudo apt install python3 python3-venv"; exit 1; }
ffmpeg -hide_banner -filters 2>/dev/null | grep -q zscale || echo "WARNUNG: ffmpeg ohne zscale – iPhone-HDR-Clips können nicht umgerechnet werden (brew install ffmpeg liefert zscale mit)."
python3 -m venv .venv
source .venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt
[ -d .earshot ] || git clone --depth 1 https://github.com/Leonxlnx/earshot .earshot
pip install -q --no-deps -e .earshot     # nur die Sound-Erzeugung, ohne die großen KI-Pakete
mkdir -p data sounds projects
bash tools/render_sounds.sh
echo
echo "Fertig. Vor jeder Sitzung:  source .venv/bin/activate  und  export CLIPS_DIR=\"/Pfad/zu/den/Clips\""

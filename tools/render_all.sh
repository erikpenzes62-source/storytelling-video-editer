#!/usr/bin/env bash
# Rendert das ganze Video in 600-Frame-Stücken (je 10 s), mehrere parallel.
# Fertige Stücke werden übersprungen -> nach Abbruch einfach neu starten.
# Aufruf:  bash tools/render_all.sh projects/NAME   (PARALLEL=3 = Anzahl gleichzeitiger Prozesse)
P="$(cd "$1" && pwd)"; T="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$P/pieces"; rm -f "$P"/pieces/*.tmp.mp4
n=$(python3 -c "import json;c=json.load(open('$P/project.json'));print(int(round(c['dur']*60)))")
jobs=()
for k0 in $(seq 0 600 $((n-1))); do
  k1=$((k0+600)); [ $k1 -gt $n ] && k1=$n
  f="$P/pieces/$(printf %05d $k0).mp4"; [ -f "$f" ] || jobs+=("$k0:$k1")
done
echo "noch zu rendern: ${#jobs[@]} Stücke"
i=0
for j in "${jobs[@]}"; do
  k0=${j%%:*}; k1=${j##*:}
  python3 "$T/render.py" "$P" $k0 $k1 "$P/pieces/$(printf %05d $k0).mp4" &
  i=$((i+1)); if [ $((i % ${PARALLEL:-3})) -eq 0 ]; then wait; fi
done
wait
have=$(ls "$P/pieces" | grep -v '\.tmp\.mp4$' | grep -c '\.mp4$'); want=$(( (n + 599) / 600 ))
echo "fertig: $have von $want Stücken"

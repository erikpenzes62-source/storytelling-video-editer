"""Clip-Datenbank: Länge, Format, HDR (HLG) und Helligkeit jedes Clips.

Aufruf:  python3 tools/clip_info.py "/Pfad/zu/den/Clips" clipinfo.json bright.json
Danach haben alle Clips eine feste ID (in der Schnittliste verwendet).
Helligkeit: 6 Messpunkte pro Clip (0 = schwarz, 255 = weiß).
Bereits analysierte Clips werden übersprungen (neue Clips einfach dazulegen und neu starten).
"""
import sys, json, os, subprocess
src, info_p, br_p = sys.argv[1], sys.argv[2], sys.argv[3]
info = json.load(open(info_p)) if os.path.exists(info_p) else {}
br = json.load(open(br_p)) if os.path.exists(br_p) else {}
nid = max([v['id'] for v in info.values()] + [-1]) + 1
for f in sorted(os.listdir(src)):
    if not f.lower().endswith(('.mov', '.mp4')) or f in info: continue
    p = os.path.join(src, f)
    r = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                        'stream=width,height,codec_name,r_frame_rate,color_transfer:stream_side_data=rotation:format=duration',
                        '-of', 'json', p], capture_output=True, text=True)
    try:
        j = json.loads(r.stdout); s = j['streams'][0]; dur = float(j['format']['duration'])
    except Exception:
        print('ÜBERSPRUNGEN (nicht lesbar):', f); continue
    rot = 0
    for sd in s.get('side_data_list', []): rot = int(sd.get('rotation', 0))
    w, h = s['width'], s['height']
    if abs(rot) == 90: w, h = h, w
    info[f] = {'id': nid, 'w': w, 'h': h, 'rot': rot, 'dur': round(dur, 2), 'codec': s['codec_name'],
               'fps': s['r_frame_rate'], 'transfer': s.get('color_transfer', 'bt709')}
    vals = {}
    for q in range(6):
        t = dur * (q + 0.5) / 6
        r = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t:.2f}', '-i', p, '-frames:v', '1', '-vf', 'scale=64:-1,format=gray',
                            '-f', 'rawvideo', '-'], capture_output=True)
        if r.stdout: vals[str(q)] = round(sum(r.stdout) / len(r.stdout), 1)
    br[str(nid)] = vals
    print(nid, f, f'{w}x{h}', info[f]['dur'], 's', info[f]['transfer'], 'Helligkeit', vals)
    nid += 1
    json.dump(info, open(info_p, 'w'), ensure_ascii=False, indent=1); json.dump(br, open(br_p, 'w'), indent=1)
print('fertig:', len(info), 'Clips')

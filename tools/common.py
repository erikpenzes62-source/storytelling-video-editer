"""Gemeinsame Helfer: Projekt laden, Pfade, ffmpeg-Version."""
import json, os, subprocess, functools

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H, FPS = 1080, 1920, 60

def load(proj):
    p = json.load(open(os.path.join(proj, 'project.json')))
    p['_dir'] = os.path.abspath(proj)
    return p

def path(p, name):
    return os.path.join(p['_dir'], name)

def clips_dir():
    d = os.environ.get('CLIPS_DIR')
    if not d:
        raise SystemExit('FEHLER: CLIPS_DIR ist nicht gesetzt. Beispiel:  export CLIPS_DIR="$HOME/Downloads/Neuer Ordner"')
    return os.path.expanduser(d)

def data_dir():
    return os.path.expanduser(os.environ.get('DATA_DIR', os.path.join(ROOT, 'data')))

def sfx_dir():
    return os.path.expanduser(os.environ.get('SFX_DIR', os.path.join(ROOT, 'sounds')))

@functools.lru_cache()
def passthrough_flag():
    """ffmpeg >= 5 kennt -fps_mode, ältere Versionen (z. B. 4.4) nur -vsync."""
    h = subprocess.run(['ffmpeg', '-hide_banner', '-h', 'full'], capture_output=True, text=True).stdout
    return ['-fps_mode', 'passthrough'] if 'fps_mode' in h else ['-vsync', 'passthrough']

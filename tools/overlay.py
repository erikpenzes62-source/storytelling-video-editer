"""Overlay engine v2 (60 fps): 4 caption styles + inserts (clock, alarm, sticker, checklist, payday, VHS, film, titles)."""
import json, math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920
import os
FD = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts') + '/'
CAP_Y = int(H * 0.68)
MAX_W = 520
EMOJI = '/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'
_fc = {}

def font(name, size, var=None):
    key = (name, size, var)
    if key not in _fc:
        path = {'anton': FD + 'Anton-Regular.ttf', 'barlow': FD + 'BarlowCondensed-ExtraBold.ttf',
                'barlowb': FD + 'BarlowCondensed-Bold.ttf', 'mont': FD + 'Montserrat[wght].ttf',
                'montI': FD + 'Montserrat-Italic[wght].ttf',
                'poppins': FD + 'Poppins-Bold.ttf'}[name]
        f = ImageFont.truetype(path, size)
        if var: f.set_variation_by_name(var)
        _fc[key] = f
    return _fc[key]

def clamp(x, a=0., b=1.): return max(a, min(b, x))
def ease_out(x): x = clamp(x); return 1 - (1 - x) ** 3
def ease_back(x):
    x = clamp(x); c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

def shadowed(img, layer, xy=(0, 0), blur=6, alpha=0.75, off=3):
    a = layer.split()[3].filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * alpha))
    sh = Image.new('RGBA', layer.size, (0, 0, 0, 255)); sh.putalpha(a)
    img.alpha_composite(sh, (xy[0], xy[1] + off)); img.alpha_composite(layer, xy)

# ---------------------------------------------------------------- captions
STY = {
 'S1': dict(f=('anton', 50, None), up=True, col=(255, 255, 255), key=(255, 214, 10), anim='slide', stroke=3),
 'S2': dict(f=('poppins', 38, None), up=True, col=(255, 255, 255), key=(34, 197, 94), anim='karaoke', stroke=2),
 'S3': dict(f=('mont', 40, 'Black'), up=True, col=(255, 255, 255), key=(255, 122, 0), anim='bounce', stroke=3),
 'S4': dict(f=('barlowb', 46, None), up=True, col=(255, 255, 255), key=(239, 68, 68), anim='bar', stroke=0),
 'S5': dict(f=('barlow', 46, None), up=True, col=(255, 255, 255), key=(59, 130, 246), anim='pill', stroke=3),
 'S6': dict(f=('poppins', 40, None), up=False, col=(255, 255, 255), key=(250, 204, 21), anim='marker', stroke=3),
 'S7': dict(f=('mont', 40, 'ExtraBold'), up=False, col=(255, 255, 255), key=(52, 211, 153), anim='fade', stroke=3),
 'S8': dict(f=('montI', 40, 'Black Italic'), up=True, col=(255, 255, 255), key=(255, 255, 255), anim='invert', stroke=3),
 'S9': dict(f=('barlow', 48, None), up=True, col=(255, 255, 255), key=(255, 140, 0), anim='zoom', stroke=3),
 'S10': dict(f=('poppins', 38, None), up=False, col=(255, 255, 255), key=(255, 64, 129), anim='type', stroke=3),
 'S13': dict(f=('mont', 34, 'ExtraBold'), up=True, col=(255, 255, 255), key=(255, 45, 120), anim='plain', stroke=3),
 'S14': dict(f=('poppins', 34, None), up=False, col=(255, 255, 255), key=(96, 165, 250), anim='plain', stroke=3),
 'S15': dict(f=('poppins', 36, None), up=False, col=(255, 255, 255), key=(163, 230, 53), anim='pillbg', stroke=0),
 'S16': dict(f=('mont', 34, 'ExtraBold'), up=True, col=(255, 255, 255), key=(250, 204, 21), anim='plain', stroke=3),
 'S17': dict(f=('mont', 34, 'ExtraBold'), up=True, col=(255, 255, 255), key=(37, 99, 235), anim='redbox', stroke=2),
 'S18': dict(f=('poppins', 34, None), up=False, col=(255, 255, 255), key=(251, 146, 60), anim='plain', stroke=3),
 'S19': dict(f=('barlowb', 44, None), up=True, col=(255, 255, 255), key=(74, 222, 128), anim='plain', stroke=3),
 'S12': dict(f=('mont', 34, 'ExtraBold'), up=True, col=(255, 255, 255), key=(225, 29, 72), anim='redbox', stroke=2),
 'S11': dict(f=('barlowb', 50, None), up=False, col=(255, 255, 255), key=(56, 189, 248), anim='glow', stroke=3),
}
BAND_H = 420; BAND_Y = CAP_Y - BAND_H // 2

class Captions:
    def __init__(self, path, style, start=0.0):
        self.ch = json.load(open(path)); self.st = STY[style]; self.start = start
        self.f = font(*self.st['f']); self.lay = [self._layout(c) for c in self.ch]

    def _t(self, s): return s.upper() if self.st['up'] else s

    def _layout(self, c):
        f = self.f; sp = f.getlength(' ')
        ws = [(self._t(x['t']), f.getlength(self._t(x['t']))) for x in c]
        lines, cur, cw = [], [], 0
        for i, (s, w) in enumerate(ws):
            add = w if not cur else cw + sp + w
            if cur and add > MAX_W: lines.append((cur, cw)); cur, cw = [i], w
            else: cur.append(i); cw = add
        lines.append((cur, cw))
        asc, desc = f.getmetrics(); lh = int((asc + desc) * 1.05)
        top = BAND_H / 2 - lh * len(lines) / 2; pos = {}
        for li, (idx, lw) in enumerate(lines):
            x = W / 2 - lw / 2
            for i in idx: pos[i] = (x, top + li * lh, ws[i][1]); x += ws[i][1] + sp
        return ws, pos, lh, lines

    def active(self, t):
        for ci, c in enumerate(self.ch):
            s = c[0]['s']; nxt = self.ch[ci + 1][0]['s'] if ci + 1 < len(self.ch) else c[-1]['e'] + 0.8
            if s - 0.05 <= t < min(nxt, c[-1]['e'] + 0.9): return ci
        return None

    def draw(self, img, t):
        if t < self.start: return
        ci = self.active(t)
        if ci is None: return
        c = self.ch[ci]; ws, pos, lh, lines = self.lay[ci]; st = self.st; f = self.f
        L = Image.new('RGBA', (W, BAND_H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
        asc, desc = f.getmetrics(); anim = st['anim']; G = None
        if anim == 'pillbg':
            for li, (idx, lw) in enumerate(lines):
                xs = [pos[i][0] for i in idx]; x0 = min(xs) - 20; x1 = max(pos[i][0] + pos[i][2] for i in idx) + 20
                y0 = pos[idx[0]][1] - 4; app = ease_out((t - c[0]['s'] + 0.05) / 0.1)
                d.rounded_rectangle([x0, y0, x1, y0 + lh + 2], radius=int(lh / 2), fill=(10, 10, 12, int(185 * app)))
        if anim == 'bar':  # dark rounded bar behind whole chunk
            ys = [pos[i][1] for i in pos]; y0 = min(ys) - 8; y1 = max(ys) + lh + 2
            xs = [pos[i][0] for i in pos]; x0 = min(xs) - 22; x1 = max(pos[i][0] + pos[i][2] for i in pos) + 22
            app = ease_out((t - c[0]['s'] + 0.05) / 0.12)
            d.rounded_rectangle([x0, y0, x1, y1], radius=14, fill=(0, 0, 0, int(150 * app)))
        for i, x in enumerate(c):
            s, w = ws[i]; px, py, _ = pos[i]; age = t - x['s']; spoken = age >= -0.03
            col = st['col'] + (255,)
            if anim in ('slide', 'bounce', 'pill') and not spoken: continue
            if x['k'] and spoken and anim not in ('karaoke', 'pill', 'marker', 'invert', 'redbox'): col = st['key'] + (255,)
            if anim == 'pill':
                p = ease_out(age / 0.12); col = col[:3] + (int(255 * p),)
                if x['k']:
                    sc = ease_back(age / 0.16)
                    cx, cy = px + w / 2, py + (asc + desc * 0.2) / 2 + asc * 0.08
                    hw, hh = (w / 2 + 12) * sc, ((asc - asc * 0.1) / 2 + 6) * sc
                    d.rounded_rectangle([cx - hw, cy - hh, cx + hw, cy + hh], radius=int(hh), fill=st['key'] + (255,))
            if anim == 'marker':
                if not spoken: col = (255, 255, 255, 140)
                elif x['k']:
                    p = ease_out(age / 0.2)
                    d.rectangle([px - 3, py + asc * 0.35, px - 3 + (w + 6) * p, py + asc + desc * 0.1], fill=st['key'] + (230,))
                    col = (20, 20, 20, 255)
            if anim == 'redbox' and x['k']:
                d.rectangle([px - 7, py + asc * 0.08, px + w + 7, py + asc + desc * 0.35], fill=st['key'] + (255,))
            if anim == 'glow':
                p = ease_out((age + 0.03) / 0.1)
                if p <= 0: continue
                col = col[:3] + (int(255 * p),)
                if x['k']:
                    if G is None: G = Image.new('RGBA', (W, BAND_H), (0, 0, 0, 0)); gd = ImageDraw.Draw(G)
                    gd.text((px, py), s, font=f, fill=st['key'] + (int(255 * p),), stroke_width=6, stroke_fill=st['key'] + (int(200 * p),))
                    col = (230, 247, 255, int(255 * p))
            if anim == 'zoom':
                if not spoken: continue
                if age < 0.12:
                    sc = 1.12 - 0.12 * ease_out(age / 0.12); fs = max(8, int(st['f'][1] * sc)); ff = font(st['f'][0], fs, st['f'][2])
                    ww = ff.getlength(s); cx, cy = px + w / 2, py + lh / 2
                    d.text((cx - ww / 2, cy - lh * sc / 2), s, font=ff, fill=col, stroke_width=st['stroke'], stroke_fill=(0, 0, 0, 200))
                    continue
            if anim == 'type':
                if not spoken: continue
                nch = max(1, int(len(s) * clamp((age + 0.03) / 0.12)))
                if nch < len(s):
                    d.text((px, py), s[:nch], font=f, fill=col, stroke_width=st['stroke'], stroke_fill=(0, 0, 0, 200))
                    continue
            if anim == 'fade':
                p = ease_out((age + 0.03) / 0.16)
                if p <= 0: continue
                py += (1 - p) * -10; col = col[:3] + (int(255 * p),)
            if anim == 'invert':
                if not spoken: continue
                if x['k']:
                    p = ease_back(age / 0.18); cx, cy = px + w / 2, py + (asc + desc * 0.2) / 2 + asc * 0.06
                    hw, hh = (w / 2 + 10) * p, ((asc * 0.9) / 2 + 7) * p
                    d.rectangle([cx - hw, cy - hh, cx + hw, cy + hh], fill=(255, 255, 255, 255))
                    col = (12, 12, 14, 255)
            if anim == 'slide':
                p = ease_out(age / 0.14); py += (1 - p) * 22; col = col[:3] + (int(255 * p),)
            if anim == 'bar' and not spoken: col = (255, 255, 255, 115)
            if anim == 'karaoke':
                cur = x['s'] - 0.03 <= t < (c[i + 1]['s'] - 0.03 if i + 1 < len(c) else x['e'] + 0.3)
                if cur:
                    d.rounded_rectangle([px - 10, py + asc * 0.12, px + w + 10, py + asc + desc * 0.25], radius=10,
                                        fill=st['key'] + (255,))
            if anim == 'bounce' and age < 0.18:
                sc = ease_back(age / 0.18); fs = max(8, int(st['f'][1] * sc)); ff = font(st['f'][0], fs, st['f'][2])
                ww = ff.getlength(s); cx, cy = px + w / 2, py + lh / 2
                d.text((cx - ww / 2, cy - lh * sc / 2), s, font=ff, fill=col, stroke_width=st['stroke'], stroke_fill=(0, 0, 0, 200))
                continue
            sw = 0 if (anim in ('marker', 'invert', 'redbox') and x['k'] and (spoken or anim == 'redbox')) or (anim == 'pill' and x['k']) else st['stroke']
            d.text((px, py), s, font=f, fill=col, stroke_width=sw, stroke_fill=(0, 0, 0, min(col[3], 200)))
            if anim == 'bar' and x['k'] and spoken:
                p = ease_out(age / 0.15)
                d.rectangle([px, py + asc + desc * 0.15, px + w * p, py + asc + desc * 0.15 + 6], fill=st['key'] + (255,))
        if G is not None:
            g = G.filter(ImageFilter.GaussianBlur(9)); img.alpha_composite(g, (0, BAND_Y)); img.alpha_composite(g, (0, BAND_Y))
        shadowed(img, L, (0, BAND_Y), blur=5, alpha=0.7 if anim != 'bar' else 0.4)

# ---------------------------------------------------------------- inserts
class Insert:
    def __init__(self, t0, t1): self.t0, self.t1 = t0, t1
    def on(self, t): return self.t0 <= t < self.t1
    def ap(self, t, fin=0.18, fout=0.18):
        return min(ease_out((t - self.t0) / fin), ease_out((self.t1 - t) / fout))

class BigTitle(Insert):
    """Big bold title (number) with pop-in; optional sub line."""
    def __init__(self, t0, t1, text, sub=None, y=0.36, size=170, col=(255, 255, 255), fnt=('mont', 'Black'), punch=None):
        super().__init__(t0, t1); self.text, self.sub, self.y, self.size, self.col, self.fnt, self.punch = text, sub, y, size, tuple(col), tuple(fnt), punch
    def draw(self, img, t):
        if not self.on(t): return
        a = self.ap(t, 0.2, 0.15); sc = ease_back((t - self.t0) / 0.25)
        if self.punch and t >= self.punch: sc *= 1 + 0.15 * max(0, 1 - (t - self.punch) / 0.2)
        f = font(self.fnt[0], max(8, int(self.size * sc)), self.fnt[1])
        L = Image.new('RGBA', (W, 520), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
        w = f.getlength(self.text); asc, desc = f.getmetrics()
        d.text((W / 2 - w / 2 - 30, 200 - asc / 2), self.text, font=f, fill=self.col + (int(255 * a),))
        if self.sub and t > self.t0 + 0.25:
            fs = font('mont', 54, 'ExtraBold'); a2 = a * ease_out((t - self.t0 - 0.25) / 0.2)
            ws = fs.getlength(self.sub); d.text((W / 2 - ws / 2 - 30, 200 + asc / 2 + 20), self.sub, font=fs, fill=(255, 255, 255, int(255 * a2)))
        shadowed(img, L, (0, int(H * self.y) - 200), blur=14, alpha=0.8, off=6)

class Sticker(Insert):
    """Emoji sticker card with caption text, wobbling."""
    def __init__(self, t0, t1, emoji, text, y=0.30):
        super().__init__(t0, t1); self.e, self.text, self.y = emoji, text, y
        ef = ImageFont.truetype(EMOJI, 109); em = Image.new('RGBA', (160, 160), (0, 0, 0, 0))
        ImageDraw.Draw(em).text((10, 10), self.e, font=ef, embedded_color=True)
        self.em = em.crop(em.getbbox()).resize((300, 300), Image.LANCZOS)
    def draw(self, img, t):
        if not self.on(t): return
        a = self.ap(t, 0.15, 0.15); sc = ease_back((t - self.t0) / 0.22)
        card = Image.new('RGBA', (460, 470), (0, 0, 0, 0)); d = ImageDraw.Draw(card)
        d.rounded_rectangle([0, 0, 459, 469], radius=36, fill=(255, 255, 255, 255))
        card.alpha_composite(self.em, (80, 30))
        f = font('mont', 40, 'Black'); lines = self.text.split('\n')
        for k, ln in enumerate(lines):
            w = f.getlength(ln); d.text((230 - w / 2, 345 + k * 46), ln, font=f, fill=(15, 15, 15, 255))
        ang = 4 * math.sin((t - self.t0) * 9)
        card = card.resize((max(1, int(460 * sc)), max(1, int(470 * sc))), Image.BICUBIC).rotate(ang, expand=True, resample=Image.BICUBIC)
        card.putalpha(card.split()[3].point(lambda v: int(v * a)))
        x = W // 2 - card.width // 2 - 30; y = int(H * self.y) - card.height // 2
        shadowed(img, card, (x, y), blur=16, alpha=0.6, off=10)

class AnalogClock(Insert):
    """Alarm clock: hands tick toward 6:00, rings (shake) at ring time."""
    def __init__(self, t0, t1, ring, y=0.33, r=170):
        super().__init__(t0, t1); self.ring, self.y, self.r = ring, y, r
    def draw(self, img, t):
        if not self.on(t): return
        a = self.ap(t, 0.2, 0.2); r = self.r; S = 2 * r + 120
        L = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(L); c = S / 2
        # bells
        for sgn in (-1, 1):
            bx = c + sgn * r * 0.62; by = c - r * 0.92
            d.pieslice([bx - 62, by - 62, bx + 62, by + 62], 180, 360, fill=(235, 235, 235, 255))
        d.ellipse([c - r - 14, c - r - 14, c + r + 14, c + r + 14], fill=(30, 30, 34, 255))
        d.ellipse([c - r, c - r, c + r, c + r], fill=(250, 250, 248, 255))
        for k in range(60):
            ang = k / 60 * 2 * math.pi; l = 26 if k % 5 == 0 else 10; wdt = 6 if k % 5 == 0 else 2
            x1, y1 = c + math.sin(ang) * (r - 12), c - math.cos(ang) * (r - 12)
            x2, y2 = c + math.sin(ang) * (r - 12 - l), c - math.cos(ang) * (r - 12 - l)
            d.line([x1, y1, x2, y2], fill=(30, 30, 34, 255), width=wdt)
        # time: 5:59:50 -> 6:00:00 at ring, seconds tick
        secs = 10 - max(0, self.ring - t) * (10 / max(0.01, self.ring - self.t0))
        tot = 5 * 3600 + 59 * 60 + 50 + min(10, int(secs)) if t < self.ring else 6 * 3600 + (t - self.ring)
        hh = (tot / 3600) % 12; mm = (tot / 60) % 60; ss = int(tot) % 60
        for val, ln, wd, col in [(hh / 12, r * 0.5, 14, (30, 30, 34)), (mm / 60, r * 0.75, 10, (30, 30, 34)), (ss / 60, r * 0.82, 4, (230, 40, 40))]:
            ang = val * 2 * math.pi
            d.line([c, c, c + math.sin(ang) * ln, c - math.cos(ang) * ln], fill=col + (255,), width=wd)
        d.ellipse([c - 14, c - 14, c + 14, c + 14], fill=(230, 40, 40, 255))
        sc = ease_back((t - self.t0) / 0.25)
        ang = 0
        if t >= self.ring: ang = 9 * math.sin((t - self.ring) * 55) * max(0.25, 1 - (t - self.ring) / 1.2)
        L = L.resize((max(1, int(S * sc)), max(1, int(S * sc))), Image.BICUBIC).rotate(ang, resample=Image.BICUBIC)
        L.putalpha(L.split()[3].point(lambda v: int(v * a)))
        shadowed(img, L, (W // 2 - L.width // 2 - 30, int(H * self.y) - L.height // 2), blur=18, alpha=0.6, off=10)
        if t >= self.ring:  # label
            f = font('mont', 64, 'Black'); s = '06:00'; w = f.getlength(s)
            T = Image.new('RGBA', (W, 120), (0, 0, 0, 0))
            ImageDraw.Draw(T).text((W / 2 - w / 2 - 30, 20), s, font=f, fill=(255, 255, 255, int(255 * a)))
            shadowed(img, T, (0, int(H * self.y) + r + 70), blur=8)

class DigitalAlarm(Insert):
    """Big digital clock 05:59 -> 06:00 with blinking colon and flip."""
    def __init__(self, t0, t1, flip, y=0.34, s0='05:59', s1='06:00'):
        super().__init__(t0, t1); self.flip, self.y, self.s0, self.s1 = flip, y, s0, s1
    def draw(self, img, t):
        if not self.on(t): return
        a = self.ap(t, 0.15, 0.2)
        s = self.s0 if t < self.flip else self.s1
        if int((t - self.t0) * 2) % 2 == 1 and t < self.flip: s = s.replace(':', ' ')
        f = font('barlow', 260)
        L = Image.new('RGBA', (W, 420), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
        w = f.getlength(s); col = (255, 255, 255) if t < self.flip else (255, 70, 70)
        sq = 1.0
        if t >= self.flip: sq = 1 + 0.12 * max(0, 1 - (t - self.flip) / 0.2)
        if self.flip - 0.08 <= t < self.flip + 0.08:  # flip squash
            sq = 0.6
        ff = font('barlow', int(260 * sq)); w = ff.getlength(s)
        d.text((W / 2 - w / 2 - 30, 60), s, font=ff, fill=col + (int(255 * a),))
        fl = font('mont', 46, 'ExtraBold'); lab = '⏰ WECKER' if False else 'WECKER'
        wl = fl.getlength(lab); d.text((W / 2 - wl / 2 - 30, 10), lab, font=fl, fill=(255, 255, 255, int(200 * a)))
        shadowed(img, L, (0, int(H * self.y) - 210), blur=20, alpha=0.85, off=6)

class Checklist(Insert):
    """Items appear at given times with red X; final item with green check."""
    def __init__(self, t0, t1, items, y=0.30):
        super().__init__(t0, t1); self.items, self.y = items, y   # items: [(text, time, ok)]
    def draw(self, img, t):
        if not self.on(t): return
        a = self.ap(t, 0.15, 0.2); f = font('mont', 54, 'Black')
        rows = [it for it in self.items if t >= it[1] - 0.02]
        if not rows: return
        L = Image.new('RGBA', (W, 120 * len(self.items) + 60), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
        bw = max(560, int(max(f.getlength(it[0].upper()) for it in self.items)) + 150); x0 = W / 2 - bw / 2 - 30
        for k, (txt, ti, ok) in enumerate(rows):
            p = ease_back((t - ti) / 0.2); y = 20 + k * 112
            xo = (1 - clamp(p)) * -80
            d.rounded_rectangle([x0 + xo, y, x0 + bw + xo, y + 92], radius=22, fill=(255, 255, 255, int(235 * a)))
            d.text((x0 + 110 + xo, y + 12), txt.upper(), font=f, fill=(20, 20, 20, int(255 * a)))
            cx, cy = x0 + 52 + xo, y + 46
            if ok:
                d.ellipse([cx - 30, cy - 30, cx + 30, cy + 30], fill=(34, 197, 94, int(255 * a)))
                d.line([cx - 14, cy, cx - 3, cy + 12, cx + 16, cy - 12], fill=(255, 255, 255, int(255 * a)), width=8)
            else:
                d.ellipse([cx - 30, cy - 30, cx + 30, cy + 30], fill=(239, 68, 68, int(255 * a)))
                d.line([cx - 12, cy - 12, cx + 12, cy + 12], fill=(255, 255, 255, int(255 * a)), width=8)
                d.line([cx - 12, cy + 12, cx + 12, cy - 12], fill=(255, 255, 255, int(255 * a)), width=8)
        shadowed(img, L, (0, int(H * self.y) - 60), blur=14, alpha=0.5, off=8)

class Payday(Insert):
    """Calendar '15.' + salary bar draining with expense chips."""
    def __init__(self, t0, t1, chips, y=0.28, day='15.'):
        super().__init__(t0, t1); self.chips, self.y, self.day = chips, y, day  # chips: [(text, time)]
    def draw(self, img, t):
        if not self.on(t): return
        a = self.ap(t, 0.2, 0.2); A = int(255 * a)
        L = Image.new('RGBA', (W, 560), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
        cx = W / 2 - 30
        # calendar
        sc = ease_back((t - self.t0) / 0.25); cw, chh = 230 * sc, 250 * sc
        d.rounded_rectangle([cx - cw / 2, 10, cx + cw / 2, 10 + chh], radius=24, fill=(255, 255, 255, A))
        d.rounded_rectangle([cx - cw / 2, 10, cx + cw / 2, 10 + 62 * sc], radius=24, fill=(239, 68, 68, A))
        d.rectangle([cx - cw / 2, 40 * sc, cx + cw / 2, 72 * sc], fill=(239, 68, 68, A))
        fm = font('mont', max(8, int(34 * sc)), 'Black'); s = 'GEHALT'; d.text((cx - fm.getlength(s) / 2, 22 * sc), s, font=fm, fill=(255, 255, 255, A))
        fn = font('mont', max(8, int(130 * sc)), 'Black'); s = self.day; d.text((cx - fn.getlength(s) / 2, 80 * sc), s, font=fn, fill=(20, 20, 20, A))
        # bar
        n_done = sum(1 for _, ti in self.chips if t >= ti)
        target = 1 - n_done / len(self.chips);
        prog = target + sum((1 / len(self.chips)) * (1 - ease_out((t - ti) / 0.35)) for _, ti in self.chips if t >= ti)
        bx0, bx1, by = cx - 260, cx + 260, 300
        d.rounded_rectangle([bx0, by, bx1, by + 46], radius=23, fill=(255, 255, 255, int(90 * a)))
        if prog > 0.01:
            d.rounded_rectangle([bx0, by, bx0 + (bx1 - bx0) * prog, by + 46], radius=23,
                                fill=((34, 197, 94) if prog > 0.4 else (239, 68, 68)) + (A,))
        # chips
        fc = font('mont', 40, 'ExtraBold'); x = cx - 260
        shown = [(s, ti) for s, ti in self.chips if t >= ti]
        tw = sum(fc.getlength('− ' + s) + 50 for s, _ in self.chips) - 18; x = cx - tw / 2
        for s, ti in self.chips:
            w = fc.getlength('− ' + s) + 32
            if t >= ti:
                p = ease_back((t - ti) / 0.2); yy = 380 + (1 - clamp(p)) * 30
                d.rounded_rectangle([x, yy, x + w, yy + 64], radius=18, fill=(20, 20, 20, int(220 * a)))
                d.text((x + 16, yy + 8), '− ' + s, font=fc, fill=(255, 90, 90, A))
            x += w + 18
        shadowed(img, L, (0, int(H * self.y) - 150), blur=14, alpha=0.6, off=8)

class SpinClock(Insert):
    """Small clock whose hands race (time running away)."""
    def __init__(self, t0, t1, y=0.30, r=120):
        super().__init__(t0, t1); self.y, self.r = y, r
    def draw(self, img, t):
        if not self.on(t): return
        a = self.ap(t, 0.2, 0.2); r = self.r; S = 2 * r + 40
        L = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(L); c = S / 2
        d.ellipse([c - r, c - r, c + r, c + r], outline=(255, 255, 255, 255), width=10)
        for k in range(12):
            ang = k / 12 * 2 * math.pi
            d.line([c + math.sin(ang) * (r - 14), c - math.cos(ang) * (r - 14), c + math.sin(ang) * (r - 34), c - math.cos(ang) * (r - 34)], fill=(255, 255, 255, 255), width=6)
        el = t - self.t0; hm = el * 1.6; mm = el * 9
        for val, ln, wd in [(hm, r * 0.5, 12), (mm, r * 0.78, 8)]:
            d.line([c, c, c + math.sin(val * 2 * math.pi) * ln, c - math.cos(val * 2 * math.pi) * ln], fill=(255, 255, 255, 255), width=wd)
        d.ellipse([c - 10, c - 10, c + 10, c + 10], fill=(255, 255, 255, 255))
        L.putalpha(L.split()[3].point(lambda v: int(v * a)))
        shadowed(img, L, (W // 2 - S // 2 - 30, int(H * self.y) - S // 2), blur=10, alpha=0.8)

class VHS(Insert):
    """Camcorder HUD: PLAY, running timecode, REC dot, date, scanlines."""
    def __init__(self, t0, t1, date='SEPT. 06 2025', rew=None):
        super().__init__(t0, t1); self.date, self.rew = date, rew or []
        sl = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(sl)
        for y in range(0, H, 6): d.line([0, y, W, y], fill=(0, 0, 0, 38), width=2)
        self.scan = sl
    def draw(self, img, t):
        if not self.on(t): return
        img.alpha_composite(self.scan)
        f = font('mont', 46, 'Bold'); d = ImageDraw.Draw(img)
        rew = any(a <= t < b for a, b in self.rew)
        lab = '◀◀ REW' if rew else 'PLAY ▶'
        el = (t - self.t0) * (-1 if rew else 1); el = abs(el)
        tc = f"{int(el // 3600):02d}:{int(el // 60) % 60:02d}:{int(el) % 60:02d}:{int((el % 1) * 30):02d}"
        fm = font('mont', 46, 'Bold')
        for (x, y, s, ff) in [(70, 150, lab, fm), (520, 150, tc, fm), (90, 1380, 'AM 00:00', fm), (90, 1440, self.date, fm)]:
            d.text((x + 2, y + 2), s, font=ff, fill=(0, 0, 0, 160)); d.text((x, y), s, font=ff, fill=(255, 255, 255, 235))
        if int((t - self.t0) * 2) % 2 == 0:
            d.ellipse([480 - 40, 160, 480 - 14, 186], fill=(230, 30, 30, 255))

class FilmLabel(Insert):
    """Black & white 'früher' label with film frame."""
    def __init__(self, t0, t1, text='FRÜHER'):
        super().__init__(t0, t1); self.text = text
    def draw(self, img, t):
        if not self.on(t): return
        d = ImageDraw.Draw(img)
        for y0 in (0, H - 70):
            d.rectangle([0, y0, W, y0 + 70], fill=(0, 0, 0, 255))
            for x in range(20, W, 70): d.rounded_rectangle([x, y0 + 20, x + 36, y0 + 50], radius=6, fill=(220, 220, 220, 255))
        a = self.ap(t, 0.3, 0.3); f = font('montI', 58, 'Black Italic')
        L = Image.new('RGBA', (W, 140), (0, 0, 0, 0)); dd = ImageDraw.Draw(L)
        w = f.getlength(self.text); dd.text((W / 2 - w / 2 - 30, 30), self.text, font=f, fill=(255, 255, 255, int(255 * a)))
        shadowed(img, L, (0, 170), blur=8)

class Hook:
    """Generic hook motion: push-in zoom, impact flash+shake, cut flashes."""
    def __init__(self, end, impacts=(), cuts=(), zoom=0.10, seed=3):
        self.end, self.impacts, self.cuts, self.zoom = end, list(impacts), list(cuts), zoom
        self.rng = random.Random(seed)
    def frame(self, im, t):
        if t < self.end:
            z = 1 + self.zoom * (t / self.end) ** 1.4; dx = dy = 0
            for ip in self.impacts:
                if ip <= t < ip + 0.25: z += 0.05 * (1 - (t - ip) / 0.25)
                if ip <= t < ip + 0.4:
                    a = 18 * (1 - (t - ip) / 0.4); dx, dy = self.rng.uniform(-a, a), self.rng.uniform(-a, a)
            cw, ch = W / z, H / z; x0 = clamp((W - cw) / 2 + dx, 0, W - cw); y0 = clamp((H - ch) / 2 + dy, 0, H - ch)
            im = im.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))
        fl = 0
        for ip in self.impacts:
            if ip <= t < ip + 0.2: fl = max(fl, 0.7 * (1 - (t - ip) / 0.2))
        for c in self.cuts:
            if c <= t < c + 0.06: fl = max(fl, 0.28)
        if fl > 0: im = Image.blend(im, Image.new('RGBA', (W, H), (255, 255, 255, 255)), fl)
        return im


class Chips(Insert):
    """Word chips appear one by one; optional strike-through line + label at strike time."""
    def __init__(self, t0, t1, items, strike=None, label=None, y=0.30, col=(255, 255, 255), label_col=(239, 68, 68)):
        super().__init__(t0, t1); self.items, self.strike, self.label, self.y, self.col, self.lcol = items, strike, label, y, tuple(col), tuple(label_col)
    def draw(self, img, t):
        if not self.on(t): return
        a = self.ap(t, 0.15, 0.2); A = int(255 * a); f = font('mont', 44, 'ExtraBold')
        L = Image.new('RGBA', (W, 420), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
        rows, cur, cw = [], [], 0; maxw = 700
        for txt, ti in self.items:
            w = f.getlength(txt.upper()) + 48
            if cur and cw + w + 16 > maxw: rows.append((cur, cw)); cur, cw = [], 0
            cur.append((txt, ti, w)); cw += w + (16 if cw else 0)
        if cur: rows.append((cur, cw))
        y = 20
        for row, rw in rows:
            x = W / 2 - rw / 2 - 30
            for txt, ti, w in row:
                if t >= ti:
                    p = ease_back((t - ti) / 0.2); yy = y + (1 - clamp(p)) * 24
                    d.rounded_rectangle([x, yy, x + w, yy + 78], radius=39, fill=(15, 15, 18, int(225 * a)))
                    d.text((x + 24, yy + 12), txt.upper(), font=f, fill=self.col + (A,))
                    if self.strike and t >= self.strike:
                        q = ease_out((t - self.strike) / 0.25)
                        d.line([x + 14, yy + 40, x + 14 + (w - 28) * q, yy + 40], fill=(239, 68, 68, A), width=7)
                x += w + 16
            y += 96
        if self.label and self.strike and t >= self.strike + 0.15:
            fl = font('mont', 52, 'Black'); q = ease_back((t - self.strike - 0.15) / 0.2)
            wl = fl.getlength(self.label); d.text((W / 2 - wl / 2 - 30, y + 10 - (1 - clamp(q)) * 20), self.label, font=fl, fill=self.lcol + (A,))
        shadowed(img, L, (0, int(H * self.y) - 100), blur=12, alpha=0.5, off=6)

class BalanceCard(Insert):
    """Account balance card: shows v0, later counts to v1 (green) with label."""
    def __init__(self, t0, t1, v0, v1, t_count, t_end, label0='KONTOSTAND', label1='3 WOCHEN SPÄTER', badge='×10', y=0.30):
        super().__init__(t0, t1); self.v0, self.v1, self.tc, self.te = v0, v1, t_count, t_end
        self.l0, self.l1, self.badge, self.y = label0, label1, badge, y
    def draw(self, img, t):
        if not self.on(t): return
        a = self.ap(t, 0.2, 0.25); A = int(255 * a); sc = ease_back((t - self.t0) / 0.3)
        cw, ch = int(640 * sc), int(300 * sc)
        if cw < 10: return
        L = Image.new('RGBA', (W, 460), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
        cx = W / 2 - 30; x0, y0 = cx - cw / 2, 40
        d.rounded_rectangle([x0, y0, x0 + cw, y0 + ch], radius=int(36 * sc), fill=(18, 18, 22, int(235 * a)))
        if t < self.tc: v = self.v0; lab = self.l0; col = (255, 255, 255)
        else:
            p = ease_out((t - self.tc) / max(0.05, self.te - self.tc)); v = self.v0 + (self.v1 - self.v0) * p
            lab = self.l1; col = (34, 197, 94) if t >= self.te else (255, 255, 255)
        punch = 1 + (0.12 * max(0, 1 - (t - self.te) / 0.25) if t >= self.te else 0)
        fl = font('mont', max(8, int(34 * sc)), 'ExtraBold'); d.text((x0 + 40 * sc, y0 + 34 * sc), lab, font=fl, fill=(170, 170, 180, A))
        s = f"{v:,.2f} €".replace(',', 'X').replace('.', ',').replace('X', '.')
        fn = font('mont', max(8, int(96 * sc * punch)), 'Black'); d.text((x0 + 40 * sc, y0 + 100 * sc - (punch - 1) * 40), s, font=fn, fill=col + (A,))
        if t >= self.te and self.badge:
            q = ease_back((t - self.te) / 0.25); fb = font('mont', max(8, int(46 * q)), 'Black'); wb = fb.getlength(self.badge)
            bx, by = x0 + cw - wb - 70, y0 - 26
            d.rounded_rectangle([bx - 18, by - 6, bx + wb + 18, by + 62], radius=30, fill=(34, 197, 94, A))
            d.text((bx, by), self.badge, font=fb, fill=(255, 255, 255, A))
        shadowed(img, L, (0, int(H * self.y) - 200), blur=16, alpha=0.6, off=8)

class VideoCounter(Insert):
    """Small 'VIDEO #n' label that jumps to given values at given times."""
    def __init__(self, t0, t1, steps, y=0.16):
        super().__init__(t0, t1); self.steps, self.y = steps, y
    def draw(self, img, t):
        if not self.on(t): return
        a = self.ap(t, 0.15, 0.2); A = int(255 * a)
        n = [v for ti, v in self.steps if t >= ti]
        if not n: return
        last = max(ti for ti, v in self.steps if t >= ti); pop = 1 + 0.15 * max(0, 1 - (t - last) / 0.15)
        s = f"VIDEO #{n[-1]}"; f = font('mont', int(46 * pop), 'Black'); w = f.getlength(s)
        L = Image.new('RGBA', (W, 140), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
        d.rounded_rectangle([W / 2 - w / 2 - 54, 30, W / 2 + w / 2 - 6, 110], radius=40, fill=(15, 15, 18, int(200 * a)))
        d.text((W / 2 - w / 2 - 30, 42), s, font=f, fill=(255, 255, 255, A))
        shadowed(img, L, (0, int(H * self.y) - 70), blur=10, alpha=0.5, off=5)


class StrikeTitle(Insert):
    """Huge title pops in, then a red bar slashes through it (anti-hook)."""
    def __init__(self, t0, t1, text, strike, sub=None, y=0.33, size=150, fnt=('mont', 'Black')):
        super().__init__(t0, t1); self.text, self.strike, self.sub, self.y, self.size, self.fnt = text, strike, sub, y, size, tuple(fnt)
    def draw(self, img, t):
        if not self.on(t): return
        a = self.ap(t, 0.12, 0.15); A = int(255 * a); sc = ease_back((t - self.t0) / 0.22)
        if t >= self.strike: sc *= 1 - 0.06 * max(0, 1 - (t - self.strike) / 0.15)
        f = font(self.fnt[0], max(8, int(self.size * sc)), self.fnt[1])
        L = Image.new('RGBA', (W, 560), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
        w = f.getlength(self.text); asc, desc = f.getmetrics(); cx, cy = W / 2 - 30, 230
        struck = t >= self.strike
        d.text((cx - w / 2, cy - asc / 2 - 10), self.text, font=f, fill=((255, 255, 255) if not struck else (225, 225, 225)) + (A,))
        if struck:
            q = ease_out((t - self.strike) / 0.14); x0, x1 = cx - w / 2 - 30, cx + w / 2 + 30
            xe = x0 + (x1 - x0) * q; y0, y1 = cy + 34, cy - 20
            ye = y0 + (y1 - y0) * q
            d.line([x0, y0, xe, ye], fill=(239, 45, 45, A), width=max(6, int(self.size * 0.13)))
        if self.sub and t > self.t0 + 0.2:
            fs = font('mont', 50, 'ExtraBold'); a2 = a * ease_out((t - self.t0 - 0.2) / 0.2); ws = fs.getlength(self.sub)
            d.text((cx - ws / 2, cy + asc / 2 + 30), self.sub, font=fs, fill=(255, 255, 255, int(255 * a2)))
        shadowed(img, L, (0, int(H * self.y) - 230), blur=14, alpha=0.8, off=6)

class Stamp(Insert):
    """Rubber-stamp label slams onto the frame (rotated, red border)."""
    def __init__(self, t0, t1, text, sub=None, y=0.32, ang=-8, col=(239, 45, 45)):
        super().__init__(t0, t1); self.text, self.sub, self.y, self.ang, self.col = text, sub, y, ang, tuple(col)
    def draw(self, img, t):
        if not self.on(t): return
        a = self.ap(t, 0.06, 0.2); A = int(255 * a); p = clamp((t - self.t0) / 0.13)
        sc = 2.2 - 1.2 * ease_out(p)
        f = font('mont', 78, 'Black'); fs = font('mont', 40, 'ExtraBold')
        w = f.getlength(self.text); ws = fs.getlength(self.sub) if self.sub else 0
        bw = int(max(w, ws) + 90); bh = 150 + (60 if self.sub else 0)
        L = Image.new('RGBA', (bw + 40, bh + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
        d.rounded_rectangle([20, 20, 20 + bw, 20 + bh], radius=22, outline=self.col + (A,), width=12, fill=(0, 0, 0, int(90 * a)))
        d.text((20 + bw / 2 - w / 2, 50), self.text, font=f, fill=self.col + (A,))
        if self.sub: d.text((20 + bw / 2 - ws / 2, 160), self.sub, font=fs, fill=(255, 255, 255, A))
        L = L.rotate(self.ang, Image.BICUBIC, expand=True)
        L = L.resize((max(1, int(L.width * sc)), max(1, int(L.height * sc))), Image.BICUBIC)
        shadowed(img, L, (int(W / 2 - 30 - L.width / 2), int(H * self.y - L.height / 2)), blur=12, alpha=0.6, off=8)

class FakeSwipe(Insert):
    """Frame gets swiped up like scrolling away, then snaps back (rubber band)."""
    def __init__(self, t0, t1, amt=0.42):
        super().__init__(t0, t1); self.amt = amt
    def draw(self, img, t):
        if not self.on(t): return
        p = (t - self.t0) / (self.t1 - self.t0)
        off = int(H * self.amt * (math.sin(math.pi * min(1, p * 1.15)) if p < 0.87 else 0))
        if off <= 0: return
        src = img.copy(); img.paste((14, 14, 16, 255), (0, 0, W, H)); img.alpha_composite(src.crop((0, off, W, H)), (0, 0))
        L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L); f = font('mont', 40, 'ExtraBold'); s = 'Nächstes Video'
        d.text((W / 2 - f.getlength(s) / 2 - 30, H - off + off * 0.4), s, font=f, fill=(255, 255, 255, 120))
        fy = H * 0.8 - off * 0.9; d.ellipse([W * 0.55 - 40, fy - 40, W * 0.55 + 40, fy + 40], fill=(255, 255, 255, 80))
        img.alpha_composite(L)

class DayCard(Insert):
    """Calendar sheet with a day number + revenue line that counts up."""
    def __init__(self, t0, t1, day, label, v1, t_count, t_end, prefix='FAST ', y=0.29):
        super().__init__(t0, t1); self.day, self.label, self.v1, self.tc, self.te, self.prefix, self.y = day, label, v1, t_count, t_end, prefix, y
    def draw(self, img, t):
        if not self.on(t): return
        a = self.ap(t, 0.2, 0.2); A = int(255 * a); sc = ease_back((t - self.t0) / 0.28)
        L = Image.new('RGBA', (W, 520), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
        cx = W / 2 - 30; cw, ch = 250 * sc, 270 * sc
        if cw < 10: return
        x0 = cx - 330; y0 = 30
        d.rounded_rectangle([x0, y0, x0 + cw, y0 + ch], radius=int(28 * sc), fill=(255, 255, 255, A))
        d.rounded_rectangle([x0, y0, x0 + cw, y0 + 70 * sc], radius=int(28 * sc), fill=(239, 68, 68, A))
        d.rectangle([x0, y0 + 40 * sc, x0 + cw, y0 + 70 * sc], fill=(239, 68, 68, A))
        fl = font('mont', max(8, int(30 * sc)), 'Black'); s = self.label; d.text((x0 + cw / 2 - fl.getlength(s) / 2, y0 + 16 * sc), s, font=fl, fill=(255, 255, 255, A))
        fd = font('mont', max(8, int(150 * sc)), 'Black'); s = self.day; d.text((x0 + cw / 2 - fd.getlength(s) / 2, y0 + 78 * sc), s, font=fd, fill=(20, 20, 24, A))
        if t >= self.tc:
            q = ease_out((t - self.tc) / max(0.05, self.te - self.tc)); v = self.v1 * q
            punch = 1 + (0.12 * max(0, 1 - (t - self.te) / 0.25) if t >= self.te else 0)
            fv = font('mont', int(92 * punch), 'Black'); s = f"{v:,.0f} €".replace(',', '.')
            col = (34, 197, 94) if t >= self.te else (255, 255, 255)
            fp = font('mont', 38, 'ExtraBold'); d.text((x0 + cw + 40, y0 + 40), self.prefix + 'UMSATZ', font=fp, fill=(255, 255, 255, int(220 * a)))
            d.text((x0 + cw + 40, y0 + 92 - (punch - 1) * 30), s, font=fv, fill=col + (A,))
        shadowed(img, L, (0, int(H * self.y) - 150), blur=16, alpha=0.6, off=8)


class WordPop(Insert):
    """One big word at a time (e.g. LAGER / BAU / BÜRO), punch-in on each change."""
    def __init__(self, t0, t1, words, y=0.34, size=170, col=(255, 255, 255)):
        super().__init__(t0, t1); self.words, self.y, self.size, self.col = words, y, size, tuple(col)
    def draw(self, img, t):
        if not self.on(t): return
        cur = [(w, ti) for w, ti in self.words if t >= ti]
        if not cur: return
        w, ti = cur[-1]; a = self.ap(t, 0.08, 0.12); A = int(255 * a)
        sc = 1.25 - 0.25 * ease_out((t - ti) / 0.12)
        f = font('anton', int(self.size * sc)); L = Image.new('RGBA', (W, 520), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
        ww = f.getlength(w); asc, desc = f.getmetrics()
        d.text((W / 2 - ww / 2 - 30, 260 - (asc + desc) / 2), w, font=f, fill=self.col + (A,))
        shadowed(img, L, (0, int(H * self.y) - 260), blur=16, alpha=0.8, off=6)

class PauseFreeze(Insert):
    """Pause icon + label over a desaturated, slightly darkened frame."""
    def __init__(self, t0, t1, label='WARTE MAL', y=0.36):
        super().__init__(t0, t1); self.label, self.y = label, y
    def draw(self, img, t):
        if not self.on(t): return
        a = self.ap(t, 0.06, 0.15)
        g = img.convert('L').convert('RGBA'); dim = Image.blend(img, g, 0.85 * a)
        dim = Image.blend(dim, Image.new('RGBA', (W, H), (0, 0, 0, 255)), 0.35 * a); img.paste(dim)
        L = Image.new('RGBA', (W, 420), (0, 0, 0, 0)); d = ImageDraw.Draw(L); A = int(255 * a)
        sc = ease_back((t - self.t0) / 0.2); cx = W / 2 - 30
        bw, bh, gap = 46 * sc, 150 * sc, 34 * sc
        d.rounded_rectangle([cx - gap / 2 - bw, 40, cx - gap / 2, 40 + bh], radius=12, fill=(255, 255, 255, A))
        d.rounded_rectangle([cx + gap / 2, 40, cx + gap / 2 + bw, 40 + bh], radius=12, fill=(255, 255, 255, A))
        f = font('anton', 96); w = f.getlength(self.label)
        if t > self.t0 + 0.15: d.text((cx - w / 2, 230), self.label, font=f, fill=(255, 255, 255, A))
        shadowed(img, L, (0, int(H * self.y) - 160), blur=14, alpha=0.7, off=6)

class SlotNumber(Insert):
    """Number whose digits roll like a slot machine and lock in left to right."""
    def __init__(self, t0, t1, text, lock0, lock_dt=0.12, sub=None, y=0.33, size=170, col_end=(255, 255, 255)):
        super().__init__(t0, t1); self.text, self.l0, self.dt, self.sub, self.y, self.size, self.ce = text, lock0, lock_dt, sub, y, size, tuple(col_end)
        self.rng = random.Random(7)
    def draw(self, img, t):
        if not self.on(t): return
        a = self.ap(t, 0.1, 0.2); A = int(255 * a)
        f = font('mont', self.size, 'Black'); L = Image.new('RGBA', (W, 560), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
        digits = [k for k, ch in enumerate(self.text) if ch.isdigit()]
        w = f.getlength(self.text); x = W / 2 - 30 - w / 2; asc, desc = f.getmetrics()
        done = t >= self.l0 + self.dt * (len(digits) - 1)
        for k, ch in enumerate(self.text):
            cw = f.getlength(ch); yo = 0; c = ch
            if ch.isdigit():
                lt = self.l0 + self.dt * digits.index(k)
                if t < lt:
                    ph = (t * 22 + k * 0.37) % 1; c = str(int(t * 22 + k * 3) % 10); yo = (ph - 0.5) * 50
                else:
                    yo = -18 * max(0, 1 - (t - lt) / 0.1)
            col = self.ce if done else (255, 255, 255)
            d.text((x + cw / 2 - f.getlength(c) / 2, 200 - asc / 2 + yo), c, font=f, fill=col + (A,)); x += cw
        if self.sub and done:
            fs = font('mont', 52, 'ExtraBold'); q = ease_out((t - self.l0 - self.dt * (len(digits) - 1)) / 0.2)
            ws = fs.getlength(self.sub); d.text((W / 2 - 30 - ws / 2, 200 + asc / 2 + 30), self.sub, font=fs, fill=(255, 255, 255, int(A * q)))
        shadowed(img, L, (0, int(H * self.y) - 200), blur=14, alpha=0.8, off=6)

class BarCompare(Insert):
    """Two bars: small 'before' vs tall 'now', growing in sequence."""
    def __init__(self, t0, t1, l0, v0txt, t_a, l1, v1txt, t_b, ratio=0.1, y=0.30):
        super().__init__(t0, t1); self.l0, self.v0, self.ta, self.l1, self.v1, self.tb, self.r, self.y = l0, v0txt, t_a, l1, v1txt, t_b, ratio, y
    def draw(self, img, t):
        if not self.on(t): return
        a = self.ap(t, 0.2, 0.2); A = int(255 * a)
        L = Image.new('RGBA', (W, 600), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
        cx = W / 2 - 30; base = 470; maxh = 380; bw = 170
        d.rounded_rectangle([cx - 330, 20, cx + 330, 580], radius=36, fill=(15, 15, 18, int(200 * a)))
        fl = font('mont', 32, 'ExtraBold'); fv = font('mont', 44, 'Black')
        for k, (lab, vt, tt, h, col) in enumerate([(self.l0, self.v0, self.ta, maxh * self.r, (150, 150, 160)), (self.l1, self.v1, self.tb, maxh, (34, 197, 94))]):
            x = cx - 200 + k * 230
            if t < tt: continue
            p = ease_out((t - tt) / 0.45); hh = max(6, h * p)
            d.rounded_rectangle([x, base - hh, x + bw, base], radius=16, fill=col + (A,))
            d.text((x + bw / 2 - fl.getlength(lab) / 2, base + 22), lab, font=fl, fill=(220, 220, 230, A))
            if p > 0.6: d.text((x + bw / 2 - fv.getlength(vt) / 2, base - hh - 62), vt, font=fv, fill=(255, 255, 255, A))
        shadowed(img, L, (0, int(H * self.y) - 240), blur=16, alpha=0.6, off=8)

class CommentCard(Insert):
    """Fake-free generic comment bubble (no real names): avatar initial + text, slides in."""
    def __init__(self, t0, t1, items, y=0.30):
        super().__init__(t0, t1); self.items, self.y = items, y   # items: [(user, text, time)]
    def draw(self, img, t):
        if not self.on(t): return
        a = self.ap(t, 0.15, 0.2); A = int(255 * a)
        L = Image.new('RGBA', (W, 520), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
        fu = font('mont', 30, 'Bold'); ft = font('mont', 38, 'ExtraBold')
        y = 20
        for user, txt, ti in self.items:
            if t < ti: continue
            p = ease_back((t - ti) / 0.22); x0 = 150 - (1 - clamp(p)) * 120; w = max(fu.getlength(user), ft.getlength(txt)) + 150
            d.rounded_rectangle([x0, y, x0 + w, y + 130], radius=28, fill=(255, 255, 255, int(240 * a)))
            d.ellipse([x0 + 22, y + 32, x0 + 88, y + 98], fill=(120, 120, 135, A))
            fi = font('mont', 32, 'Black'); d.text((x0 + 55 - fi.getlength(user[0].upper()) / 2, y + 46), user[0].upper(), font=fi, fill=(255, 255, 255, A))
            d.text((x0 + 108, y + 20), user, font=fu, fill=(120, 120, 130, A)); d.text((x0 + 108, y + 58), txt, font=ft, fill=(20, 20, 24, A))
            y += 150
        shadowed(img, L, (0, int(H * self.y) - 160), blur=14, alpha=0.6, off=8)


class SplitLabels(Insert):
    """Labels for a top/bottom split screen (e.g. FRÜHER / HEUTE) + divider line."""
    def __init__(self, t0, t1, top='FRÜHER', bottom='HEUTE', t_bottom=None, col_top=(239, 68, 68), col_bottom=(34, 197, 94)):
        super().__init__(t0, t1); self.top, self.bot, self.tb, self.ct, self.cb = top, bottom, t_bottom if t_bottom is not None else t0, tuple(col_top), tuple(col_bottom)
    def draw(self, img, t):
        if not self.on(t): return
        a = self.ap(t, 0.12, 0.15); A = int(255 * a)
        L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
        d.rectangle([0, H / 2 - 4, W, H / 2 + 4], fill=(255, 255, 255, A))
        f = font('mont', 54, 'Black')
        for txt, y, col, tt in [(self.top, H / 2 - 130, self.ct, self.t0), (self.bot, H / 2 + 40, self.cb, self.tb)]:
            if t < tt: continue
            p = ease_back((t - tt) / 0.2); w = f.getlength(txt)
            x0 = W / 2 - 30 - w / 2 - 30
            d.rounded_rectangle([x0, y, x0 + (w + 60) * p, y + 86], radius=20, fill=col + (A,))
            if p > 0.6: d.text((x0 + 30, y + 10), txt, font=f, fill=(255, 255, 255, A))
        shadowed(img, L, (0, 0), blur=10, alpha=0.5, off=5)


class LockScreen(Insert):
    """Phone lock screen over a darkened/blurred frame: big clock + notifications sliding in from the top."""
    def __init__(self, t0, t1, clock, date, notes):
        super().__init__(t0, t1); self.clock, self.date, self.notes = clock, date, notes   # notes: [(app, title, body, time)]
    def draw(self, img, t):
        if not self.on(t): return
        a = self.ap(t, 0.01, 0.2)
        bg = img.resize((W // 8, H // 8)).filter(ImageFilter.GaussianBlur(3)).resize((W, H), Image.BICUBIC)
        bg = Image.blend(bg, Image.new('RGBA', (W, H), (0, 0, 0, 255)), 0.45); img.paste(Image.blend(img, bg, a))
        L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L); A = int(255 * a)
        fd = font('mont', 40, 'SemiBold'); w = fd.getlength(self.date); d.text((W / 2 - w / 2, 250), self.date, font=fd, fill=(255, 255, 255, int(220 * a)))
        fc = font('mont', 230, 'Bold'); w = fc.getlength(self.clock); d.text((W / 2 - w / 2, 290), self.clock, font=fc, fill=(255, 255, 255, A))
        shown = [n for n in self.notes if t >= n[3]]
        y = 700
        fa = font('mont', 30, 'SemiBold'); ft = font('mont', 38, 'ExtraBold'); fb = font('mont', 34, 'SemiBold')
        for k, (app, title, body, tn) in enumerate(reversed(shown)):
            p = ease_back((t - tn) / 0.3) if k == 0 else 1
            yy = y + k * 205 - (1 - clamp(p)) * 260
            x0, x1 = 70, W - 70
            d.rounded_rectangle([x0, yy, x1, yy + 185], radius=40, fill=(245, 245, 247, int(225 * a)))
            d.rounded_rectangle([x0 + 30, yy + 30, x0 + 100, yy + 100], radius=18, fill=(34, 197, 94, A))
            fe = font('mont', 46, 'Black'); d.text((x0 + 65 - fe.getlength('€') / 2, yy + 36), '€', font=fe, fill=(255, 255, 255, A))
            d.text((x0 + 125, yy + 28), app, font=fa, fill=(100, 100, 110, A)); d.text((x1 - 40 - fa.getlength('jetzt'), yy + 28), 'jetzt', font=fa, fill=(120, 120, 130, A))
            d.text((x0 + 125, yy + 70), title, font=ft, fill=(15, 15, 20, A)); d.text((x0 + 125, yy + 118), body, font=fb, fill=(60, 60, 70, A))
        img.alpha_composite(L)

class GridReveal(Insert):
    """2x2 grid base: tiles stay dark until their time, then reveal with a label."""
    def __init__(self, t0, t1, tiles):
        super().__init__(t0, t1); self.tiles = tiles   # [(label, time)] order TL, TR, BL, BR
    def draw(self, img, t):
        if not self.on(t): return
        L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L); f = font('mont', 46, 'Black')
        for k, (lab, tt) in enumerate(self.tiles):
            x0, y0 = (k % 2) * W // 2, (k // 2) * H // 2
            if t < tt: d.rectangle([x0, y0, x0 + W // 2, y0 + H // 2], fill=(0, 0, 0, 235)); continue
            p = ease_back((t - tt) / 0.2); fl = max(0, 1 - (t - tt) / 0.15)
            if fl > 0: d.rectangle([x0, y0, x0 + W // 2, y0 + H // 2], fill=(255, 255, 255, int(150 * fl)))
            w = f.getlength(lab); cx, cy = x0 + W / 4, y0 + H / 4
            d.rounded_rectangle([cx - w / 2 - 22, cy - 40, cx - w / 2 - 22 + (w + 44) * clamp(p), cy + 44], radius=16, fill=(15, 15, 18, 220))
            if p > 0.6: d.text((cx - w / 2, cy - 30), lab, font=f, fill=(255, 255, 255, 255))
        d.rectangle([W // 2 - 3, 0, W // 2 + 3, H], fill=(0, 0, 0, 255)); d.rectangle([0, H // 2 - 3, W, H // 2 + 3], fill=(0, 0, 0, 255))
        img.alpha_composite(L)

class EuroBurst(Insert):
    """Burst of € coins/notes flying out + big amount pop."""
    def __init__(self, t0, t1, text, y=0.34, n=26, seed=3):
        super().__init__(t0, t1); self.text, self.y = text, y
        r = random.Random(seed); self.parts = [(r.uniform(0, 2 * math.pi), r.uniform(500, 1100), r.uniform(-300, 300), '€', r.uniform(50, 100)) for _ in range(n)]
    def draw(self, img, t):
        if not self.on(t): return
        a = self.ap(t, 0.05, 0.25); dt = t - self.t0
        L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
        cx, cy = W / 2 - 30, H * self.y
        for ang, v, spin, ch, sz in self.parts:
            x = cx + math.cos(ang) * v * dt; y = cy + math.sin(ang) * v * dt + 900 * dt * dt
            al = int(255 * a * max(0, 1 - dt / 1.6))
            if al <= 0: continue
            f = font('mont', int(sz), 'Black'); d.text((x, y), ch, font=f, fill=(250, 204, 21, al), stroke_width=3, stroke_fill=(120, 80, 0, al))
        sc = ease_back(dt / 0.25); f = font('mont', max(8, int(170 * sc)), 'Black'); w = f.getlength(self.text); asc, desc = f.getmetrics()
        d.text((cx - w / 2, cy - asc / 2), self.text, font=f, fill=(34, 197, 94, int(255 * a)), stroke_width=6, stroke_fill=(0, 0, 0, int(160 * a)))
        img.alpha_composite(L)

class StackTitle(Insert):
    """Lines stack in one after another (e.g. MARKETING / VERTRIEB)."""
    def __init__(self, t0, t1, lines, y=0.32, size=110, col=(255, 255, 255)):
        super().__init__(t0, t1); self.lines, self.y, self.size, self.col = lines, y, size, tuple(col)   # [(text, time)]
    def draw(self, img, t):
        if not self.on(t): return
        a = self.ap(t, 0.12, 0.15); L = Image.new('RGBA', (W, 600), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
        f = font('anton', self.size); asc, desc = f.getmetrics(); y = 40
        for txt, tt in self.lines:
            if t >= tt:
                p = ease_out((t - tt) / 0.18); w = f.getlength(txt)
                d.text((W / 2 - 30 - w / 2 - (1 - p) * 140, y), txt, font=f, fill=self.col + (int(255 * a * p),))
            y += asc + desc + 6
        shadowed(img, L, (0, int(H * self.y) - 200), blur=14, alpha=0.8, off=6)

class StationBoard(Insert):
    """Split-flap departure board: destination rolls in, 'ABFAHRT: JETZT' blinks."""
    def __init__(self, t0, t1, dest, t_lock, y=0.30):
        super().__init__(t0, t1); self.dest, self.tl, self.y = dest, t_lock, y
    def draw(self, img, t):
        if not self.on(t): return
        a = self.ap(t, 0.15, 0.2); A = int(255 * a)
        L = Image.new('RGBA', (W, 520), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
        x0, x1 = 90, W - 150; d.rounded_rectangle([x0, 20, x1, 470], radius=26, fill=(18, 20, 24, int(235 * a)))
        fh = font('mont', 32, 'ExtraBold'); d.text((x0 + 40, 48), 'ZUG', font=fh, fill=(150, 150, 160, A)); d.text((x0 + 260, 48), 'ZIEL', font=fh, fill=(150, 150, 160, A))
        fz = font('barlow', 74); d.text((x0 + 40, 100), 'HTS 1', font=fz, fill=(250, 204, 21, A))
        chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ '; out = ''
        for k, ch in enumerate(self.dest):
            lt = self.tl + k * 0.04
            out += ch if t >= lt else chars[int(t * 30 + k * 7) % len(chars)]
        d.text((x0 + 260, 100), out, font=fz, fill=(250, 204, 21, A))
        d.line([x0 + 30, 210, x1 - 30, 210], fill=(60, 60, 70, A), width=3)
        d.text((x0 + 40, 240), 'ABFAHRT', font=fh, fill=(150, 150, 160, A))
        if t >= self.tl + len(self.dest) * 0.04:
            on = int((t - self.tl) * 2.5) % 2 == 0
            fj = font('barlow', 110); d.text((x0 + 40, 285), 'JETZT', font=fj, fill=((34, 197, 94) if on else (20, 120, 60)) + (A,))
        shadowed(img, L, (0, int(H * self.y) - 200), blur=14, alpha=0.6, off=8)

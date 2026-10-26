#!/usr/bin/env python3
"""Genera la pixel art segnaposto del gioco (sprite, tileset, sfondi, effetti sonori).

Uso:  python3 tools/gen_assets.py      (richiede Pillow: pip install pillow)
Tutti i file finiscono in assets/. Sono segnaposto: sostituiscili con la grafica
definitiva mantenendo dimensioni dei frame e nomi dei file.
"""
import math
import os
import random
import struct
import wave

from PIL import Image

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
for sub in ("sprites", "tiles", "backgrounds", "sfx"):
    os.makedirs(os.path.join(ROOT, sub), exist_ok=True)

OUTLINE = (22, 16, 24, 255)


def rgba(c, a=255):
    return (c[0], c[1], c[2], a)


def shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c[:3]) + (255,)


# ---------------------------------------------------------------------------
# Strumenti di disegno "a pixel"
# ---------------------------------------------------------------------------
class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.px = [[None] * w for _ in range(h)]  # (colore, tag)

    def put(self, x, y, c, tag=0):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < self.w and 0 <= y < self.h:
            self.px[y][x] = (rgba(c), tag)

    def rect(self, x0, y0, x1, y1, c, tag=0):
        for y in range(int(y0), int(y1) + 1):
            for x in range(int(x0), int(x1) + 1):
                self.put(x, y, c, tag)

    def disc(self, cx, cy, r, c, tag=0):
        for y in range(int(cy - r - 1), int(cy + r + 2)):
            for x in range(int(cx - r - 1), int(cx + r + 2)):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r + 0.3:
                    self.put(x, y, c, tag)

    def line(self, x0, y0, x1, y1, c, width=2, tag=0):
        n = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1
        for i in range(n + 1):
            t = i / n
            x = x0 + (x1 - x0) * t
            y = y0 + (y1 - y0) * t
            for dy in range(width):
                for dx in range(width):
                    self.put(math.floor(x) + dx - width // 2 + (1 if width == 1 else 0) * 0,
                             math.floor(y) + dy - width // 2, c, tag)

    def shade_pass(self):
        """Luce dall'alto a sinistra: schiarisce i bordi superiori, scurisce quelli inferiori/destri
        (solo verso pixel di un'altra 'parte', così ogni pezzo ha volume)."""
        src = [row[:] for row in self.px]
        for y in range(self.h):
            for x in range(self.w):
                p = src[y][x]
                if not p:
                    continue
                c, tag = p
                if tag < 0:  # pixel "piatti" (occhi, visiera)
                    continue

                def other(xx, yy):
                    if not (0 <= xx < self.w and 0 <= yy < self.h):
                        return True
                    q = src[yy][xx]
                    return q is None or q[1] != tag

                if other(x, y - 1):
                    self.px[y][x] = (shade(c, 1.28), tag)
                elif other(x, y + 1) or other(x + 1, y):
                    self.px[y][x] = (shade(c, 0.72), tag)

    def outline_pass(self, color=OUTLINE):
        src = [row[:] for row in self.px]
        for y in range(self.h):
            for x in range(self.w):
                if src[y][x]:
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    xx, yy = x + dx, y + dy
                    if 0 <= xx < self.w and 0 <= yy < self.h and src[yy][xx] and src[yy][xx][1] != 99:
                        self.px[y][x] = (color, 99)
                        break

    def image(self):
        img = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        for y in range(self.h):
            for x in range(self.w):
                if self.px[y][x]:
                    img.putpixel((x, y), self.px[y][x][0])
        return img


def pol(x, y, ang_deg, length):
    a = math.radians(ang_deg)
    return x + math.sin(a) * length, y + math.cos(a) * length


# ---------------------------------------------------------------------------
# Goblin Slayer (giocatore): 32x32 per frame, piedi a y=31, guarda a destra
# ---------------------------------------------------------------------------
ARMORED = {
    "helm": (122, 124, 128), "helm_dark": (82, 84, 90), "visor": (10, 8, 12), "eye": (230, 48, 36),
    "crest": (150, 34, 30),
    "mail": (98, 96, 92), "mail_dot": (64, 62, 60), "tabard": (92, 70, 48),
    "arm": (150, 152, 160), "glove": (84, 56, 34),
    "leg": (84, 78, 70), "boot": (58, 40, 28), "belt": (64, 42, 26), "buckle": (196, 160, 70),
    "shield": (128, 92, 52), "rim": (150, 152, 158),
}
UNARMORED = dict(ARMORED)
UNARMORED.update({
    "helm": (66, 46, 32), "helm_dark": (44, 30, 22), "visor": (214, 168, 128), "eye": (30, 20, 20),
    "crest": (66, 46, 32),
    "mail": (196, 180, 146), "mail_dot": (170, 154, 122), "tabard": (176, 160, 128),
    "arm": (196, 180, 146), "leg": (150, 128, 96),
})

BASE_POSE = dict(bob=0, fl=(8, 4), bl=(-8, 4), fa=(10, 20), ba=(-12, 30), crouch=0, throw=None,
                 shield=True)


def draw_knight(pal, **kw):
    p = dict(BASE_POSE)
    p.update(kw)
    cv = Canvas(32, 32)
    hx = 15
    hy = 19 + p["bob"] + p["crouch"]
    thigh, shin = 6, 6

    def leg(params, dark, tag):
        ha, kb = params
        kx, ky = pol(hx, hy, ha, thigh)
        fx, fy = pol(kx, ky, ha - kb, shin)
        c = shade(pal["leg"], 0.8 if dark else 1.0)
        cv.line(hx, hy, kx, ky, c, 3, tag)
        cv.line(kx, ky, fx, fy - 1, c, 2, tag)
        bc = shade(pal["boot"], 0.8 if dark else 1.0)
        cv.rect(fx - 1, fy - 2, fx + 2, fy, bc, tag + 1)
        return fy

    def arm(params, dark, tag, throw=None):
        sx, sy = hx + 1, hy - 8
        if throw is not None:
            sa, ea = throw
        else:
            sa, ea = params
        ex, ey = pol(sx, sy, sa, 5)
        wx, wy = pol(ex, ey, sa + ea, 4)
        c = shade(pal["arm"], 0.8 if dark else 1.0)
        cv.line(sx, sy, ex, ey, c, 2, tag)
        cv.line(ex, ey, wx, wy, c, 2, tag)
        cv.rect(wx - 1, wy - 1, wx, wy, shade(pal["glove"], 0.85 if dark else 1.0), tag + 1)
        return wx, wy

    # gamba e braccio dietro
    leg(p["bl"], True, 10)
    bwx, bwy = arm(p["ba"], True, 20)
    # busto: cotta di maglia + tabarro
    top = hy - 9
    cv.rect(hx - 3, top, hx + 4, hy, pal["mail"], 30)
    for y in range(top + 1, hy, 2):
        for x in range(hx - 3 + (y % 4 == 1), hx + 5, 2):
            cv.put(x, y, pal["mail_dot"], 30)
    cv.rect(hx - 2, hy - 3, hx + 4, hy + 1, pal["tabard"], 31)
    cv.rect(hx - 3, hy - 4, hx + 4, hy - 4, pal["belt"], 32)
    cv.put(hx + 2, hy - 4, pal["buckle"], -1)
    # gamba davanti
    leg(p["fl"], False, 40)
    # elmo (il celebre elmo sporco con visiera a fessura)
    ht = top - 8
    cv.rect(hx - 3, ht + 1, hx + 4, ht + 8, pal["helm"], 50)
    cv.rect(hx - 2, ht, hx + 3, ht, pal["helm"], 50)
    cv.rect(hx - 3, ht + 7, hx + 5, ht + 8, pal["helm_dark"], 51)  # bordo/guardia del collo
    cv.rect(hx + 1, ht + 3, hx + 4, ht + 4, pal["visor"], -2)
    cv.put(hx + 3, ht + 3, pal["eye"], -3)
    cv.rect(hx - 1, ht + 5, hx + 4, ht + 5, pal["helm_dark"], 52)  # griglia sotto la visiera
    # piccolo pennacchio/corno sul lato
    cv.line(hx - 3, ht + 1, hx - 6, ht - 2, pal["crest"], 2, 53)
    # scudo rotondo legato all'avambraccio
    if p["shield"]:
        sx, sy = hx + 2, hy - 4
        cv.disc(sx, sy, 3.6, pal["rim"], 60)
        cv.disc(sx, sy, 2.6, pal["shield"], 61)
        cv.put(sx, sy, pal["rim"], 62)
    # braccio davanti (quello che lancia)
    wx, wy = arm(p["fa"], False, 70, p["throw"])
    if p.get("dagger"):
        cv.line(wx, wy - 1, wx + p["dagger"][0], wy - 1 + p["dagger"][1], (200, 204, 212), 1, 80)
    cv.shade_pass()
    cv.outline_pass()
    return cv.image()


def knight_frames(pal):
    f = []
    # 0-1 idle (respiro)
    f.append(draw_knight(pal))
    f.append(draw_knight(pal, bob=1, fa=(10, 24), ba=(-12, 34)))
    # 2-5 corsa
    f.append(draw_knight(pal, fl=(30, 10), bl=(-25, 40), fa=(-25, 40), ba=(30, 40), bob=-1))
    f.append(draw_knight(pal, fl=(10, 50), bl=(-5, 5), fa=(-5, 40), ba=(10, 40), bob=0))
    f.append(draw_knight(pal, fl=(-25, 40), bl=(30, 10), fa=(30, 40), ba=(-25, 40), bob=-1))
    f.append(draw_knight(pal, fl=(-5, 5), bl=(10, 50), fa=(10, 40), ba=(-5, 40), bob=0))
    # 6 salto (su), 7 salto (giù)
    f.append(draw_knight(pal, fl=(35, 70), bl=(-15, 60), fa=(-60, 40), ba=(40, 20), bob=-2))
    f.append(draw_knight(pal, fl=(15, 20), bl=(-20, 30), fa=(-120, 20), ba=(60, 10), bob=-2))
    # 8-9 lancio
    f.append(draw_knight(pal, throw=(-150, 30), fl=(20, 5), bl=(-15, 10)))
    f.append(draw_knight(pal, throw=(-90, 0), fl=(20, 5), bl=(-15, 10)))
    # 10 accovacciato, 11 lancio accovacciato
    f.append(draw_knight(pal, crouch=5, fl=(70, 140), bl=(40, 130), fa=(20, 40), ba=(0, 40)))
    f.append(draw_knight(pal, crouch=5, fl=(70, 140), bl=(40, 130), throw=(-90, 0)))
    # 12 colpito
    f.append(draw_knight(pal, fl=(-20, 30), bl=(-35, 20), fa=(-150, 10), ba=(-120, 10), bob=-1))
    # 13 a terra (morto)
    dead = draw_knight(pal, fl=(0, 0), bl=(0, 0), fa=(0, 0), ba=(0, 0)).rotate(90, expand=False)
    dead = dead.transform(dead.size, Image.AFFINE, (1, 0, 0, 0, 1, -8))
    f.append(dead)
    return f


def sheet(frames, w, h):
    img = Image.new("RGBA", (w * len(frames), h), (0, 0, 0, 0))
    for i, fr in enumerate(frames):
        img.paste(fr, (i * w, 0))
    return img


# ---------------------------------------------------------------------------
# Goblin: 32x32, piedi a y=31, guarda a destra
# ---------------------------------------------------------------------------
GOB = {"skin": (104, 146, 58), "skin_dark": (66, 100, 40), "eye": (250, 210, 40), "pupil": (180, 20, 20),
       "cloth": (110, 74, 44), "club": (120, 84, 50), "teeth": (236, 226, 190), "rust": (150, 80, 40)}


def draw_goblin(step=0, jump=False, hurt=False, attack=False):
    g = dict(GOB)
    if hurt:
        g = {k: (240, 240, 240) for k in GOB}
    cv = Canvas(32, 32)
    hx, hy = 15, 24
    legs = [((20, 10), (-20, 10)), ((5, 30), (-5, 5)), ((-20, 10), (20, 10)), ((-5, 5), (5, 30))][step % 4]
    if jump:
        legs = ((40, 80), (-10, 70))
        hy -= 1

    def leg(params, dark, tag):
        ha, kb = params
        kx, ky = pol(hx, hy, ha, 4)
        fx, fy = pol(kx, ky, ha - kb, 4)
        c = shade(g["skin"], 0.75 if dark else 1)
        cv.line(hx, hy, kx, ky, c, 2, tag)
        cv.line(kx, ky, fx, fy, c, 2, tag)
        cv.rect(fx, fy, fx + 2, fy, c, tag)

    leg(legs[1], True, 10)
    # braccio dietro
    cv.line(hx, hy - 6, hx - 3, hy - 2, shade(g["skin"], 0.75), 2, 15)
    # corpo ricurvo con pancia
    cv.disc(hx + 1, hy - 4, 4, g["skin"], 20)
    cv.rect(hx - 2, hy - 2, hx + 4, hy + 1, g["cloth"], 21)
    leg(legs[0], False, 30)
    # testa grossa, protesa in avanti
    tx, ty = hx + 3, hy - 11
    cv.disc(tx, ty, 4.2, g["skin"], 40)
    cv.rect(tx + 2, ty + 1, tx + 6, ty + 3, g["skin"], 41)  # muso
    cv.put(tx + 7, ty + 1, g["skin"], 41)                   # naso a uncino
    # orecchie a punta
    cv.line(tx - 3, ty - 1, tx - 9, ty - 5, g["skin"], 2, 42)
    cv.line(tx + 1, ty - 4, tx + 2, ty - 8, g["skin"], 1, 43)
    # occhi e denti
    cv.rect(tx + 2, ty - 1, tx + 3, ty - 1, g["eye"], -1)
    cv.put(tx + 3, ty - 1, g["pupil"], -2)
    cv.put(tx + 4, ty + 3, g["teeth"], -3)
    cv.put(tx + 6, ty + 3, g["teeth"], -3)
    # braccio davanti con pugnale arrugginito / clava
    sa = -100 if attack else (30 if step % 2 else 10)
    ex, ey = pol(hx + 2, hy - 6, sa, 4)
    cv.line(hx + 2, hy - 6, ex, ey, g["skin"], 2, 50)
    cx2, cy2 = pol(ex, ey, sa - 150 if attack else 160, 6)
    cv.line(ex, ey, cx2, cy2, g["club"], 2, 51)
    cv.disc(cx2, cy2, 1.5, g["club"], 51)
    cv.shade_pass()
    cv.outline_pass()
    return cv.image()


# ---------------------------------------------------------------------------
# Piccoli sprite: pugnale, nuvola di fumo, scintilla, armatura, pezzi di armatura
# ---------------------------------------------------------------------------
def dagger():
    cv = Canvas(12, 5)
    cv.rect(0, 2, 2, 2, (110, 74, 44), 1)          # impugnatura
    cv.rect(3, 1, 3, 3, (196, 160, 70), 2)         # guardia
    cv.rect(4, 2, 10, 2, (210, 214, 222), 3)       # lama
    cv.put(4, 1, (150, 154, 162), 3)
    cv.put(11, 2, (240, 240, 248), 3)
    cv.outline_pass()
    return cv.image()


def puff_frames():
    out = []
    rnd = random.Random(3)
    for i in range(5):
        cv = Canvas(16, 16)
        r = 2 + i * 1.4
        for k in range(7):
            a = k / 7 * math.tau + i * 0.4
            cx, cy = 8 + math.cos(a) * r * 0.8, 8 + math.sin(a) * r * 0.8
            col = (220, 210, 190) if i < 2 else (150, 140, 130) if i < 4 else (90, 84, 80)
            cv.disc(cx, cy, max(0.6, 2.4 - i * 0.45 + rnd.random() * 0.4), col, 1)
        out.append(cv.image())
    return out


def spark_frames():
    out = []
    for i in range(3):
        cv = Canvas(8, 8)
        L = 1 + i
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            for k in range(L + 1):
                cv.put(4 + dx * k, 4 + dy * k, (255, 236, 140) if k < L else (255, 140, 40))
        out.append(cv.image())
    return out


def armor_pickup():
    """Forziere che restituisce l'armatura."""
    cv = Canvas(16, 16)
    cv.rect(2, 6, 13, 14, (120, 80, 44), 1)
    cv.rect(2, 4, 13, 7, (140, 96, 54), 2)
    cv.rect(2, 7, 13, 7, (196, 160, 70), 3)
    cv.rect(7, 7, 8, 9, (220, 190, 90), 4)
    cv.rect(2, 4, 2, 14, (150, 152, 158), 5)
    cv.rect(13, 4, 13, 14, (150, 152, 158), 5)
    cv.shade_pass()
    cv.outline_pass()
    return cv.image()


def armor_bits():
    """Pezzi di armatura che volano via quando si viene colpiti (4 frame da 8x8)."""
    out = []
    shapes = [[(1, 2), (6, 5)], [(2, 1), (5, 6)], [(1, 3), (6, 4)], [(3, 1), (4, 6)]]
    for (a, b) in shapes:
        cv = Canvas(8, 8)
        cv.rect(a[0], a[1], b[0], b[1], ARMORED["helm"], 1)
        cv.shade_pass()
        cv.outline_pass()
        out.append(cv.image())
    return out


# ---------------------------------------------------------------------------
# Tileset 16x16 (8 colonne x 2 righe)
# ---------------------------------------------------------------------------
def tileset():
    T = 16
    img = Image.new("RGBA", (T * 8, T * 2), (0, 0, 0, 0))
    rnd = random.Random(7)
    dirt = [(74, 52, 46), (62, 44, 40), (88, 62, 52), (54, 38, 36)]
    grass = [(70, 110, 64), (50, 84, 52), (96, 136, 78)]
    stone = [(92, 92, 108), (72, 72, 88), (112, 112, 128), (56, 56, 70)]

    def tile(ix, iy, fn):
        t = Image.new("RGBA", (T, T), (0, 0, 0, 0))
        fn(t)
        img.paste(t, (ix * T, iy * T))

    def dirt_fill(t, top=0):
        for y in range(top, T):
            for x in range(T):
                c = dirt[0]
                r = rnd.random()
                if r < 0.18:
                    c = dirt[1]
                elif r < 0.25:
                    c = dirt[2]
                if (x + y * 3) % 11 == 0:
                    c = dirt[3]
                t.putpixel((x, y), rgba(c))
        # sassolini
        for _ in range(2):
            sx, sy = rnd.randrange(1, T - 3), rnd.randrange(max(top + 2, 3), T - 2)
            for dx in range(2):
                t.putpixel((sx + dx, sy), rgba((104, 94, 100)))
                t.putpixel((sx + dx, sy + 1), rgba((70, 64, 70)))

    def grass_top(t):
        dirt_fill(t, 0)
        for x in range(T):
            h = 3 + (1 if (x * 7) % 5 == 0 else 0) + (1 if (x * 3) % 7 == 0 else 0)
            for y in range(h):
                t.putpixel((x, y), rgba(grass[1] if y == h - 1 else grass[0]))
            t.putpixel((x, 0), rgba(grass[2] if x % 3 else grass[0]))
            t.putpixel((x, h), rgba(dirt[3]))

    def bricks(t):
        for y in range(T):
            for x in range(T):
                row = y // 4
                off = 4 if row % 2 else 0
                mortar = (y % 4 == 3) or ((x + off) % 8 == 7)
                if mortar:
                    c = stone[3]
                else:
                    c = stone[0]
                    if y % 4 == 0:
                        c = stone[2]
                    elif (x + off) % 8 == 6 or y % 4 == 2 and rnd.random() < 0.3:
                        c = stone[1]
                    if rnd.random() < 0.06:
                        c = (70, 96, 64)  # muschio
                t.putpixel((x, y), rgba(c))

    def brick_top(t):
        bricks(t)
        for x in range(T):
            t.putpixel((x, 0), rgba((140, 140, 156)))
            if rnd.random() < 0.4:
                t.putpixel((x, 1), rgba((70, 110, 64)))

    def plank(t):
        for x in range(T):
            for y in range(0, 5):
                c = (126, 86, 50) if y in (1, 2) else (96, 62, 36)
                if y == 0:
                    c = (156, 112, 68)
                if y == 4:
                    c = (60, 38, 24)
                t.putpixel((x, y), rgba(c))
        for x in (2, 13):
            t.putpixel((x, 2), rgba((180, 180, 190)))
        for y in range(5, 9):
            t.putpixel((3, y), rgba((80, 52, 30)))
            t.putpixel((12, y), rgba((80, 52, 30)))

    def grave(t):
        for y in range(3, T):
            for x in range(3, 13):
                if y < 6 and (x - 8) ** 2 + (y - 6) ** 2 > 22:
                    continue
                c = stone[0] if x < 11 else stone[1]
                if x == 3 or y == 3:
                    c = stone[2]
                t.putpixel((x, y), rgba(c))
        for y in range(6, 11):
            t.putpixel((8, y), rgba(stone[3]))
        for x in range(6, 11):
            t.putpixel((x, 8), rgba(stone[3]))
        for x in range(2, 14):
            t.putpixel((x, 15), rgba(grass[0]))

    def bones(t):
        for x in range(3, 13):
            t.putpixel((x, 13), rgba((220, 214, 196)))
        for p in ((2, 12), (2, 14), (13, 12), (13, 14)):
            t.putpixel(p, rgba((220, 214, 196)))
        for p in ((6, 9), (7, 9), (8, 9), (6, 10), (8, 10), (7, 11)):
            t.putpixel(p, rgba((236, 230, 212)))
        t.putpixel((6, 10), rgba((20, 16, 20)))
        t.putpixel((8, 10), rgba((20, 16, 20)))

    def cave_wall(t):
        for y in range(T):
            for x in range(T):
                c = (40, 32, 44) if rnd.random() < 0.8 else (54, 44, 58)
                t.putpixel((x, y), rgba(c))

    def spikes(t):
        for i in range(4):
            bx = i * 4
            for y in range(8, T):
                w = (y - 8) // 2
                for x in range(bx + 2 - w, bx + 2 + w):
                    if 0 <= x < T:
                        t.putpixel((x, y), rgba((160, 164, 176) if x < bx + 2 else (110, 112, 126)))

    tile(0, 0, grass_top)   # 0: terra con erba (superficie)
    tile(1, 0, dirt_fill)   # 1: terra
    tile(2, 0, brick_top)   # 2: pietra rovine (superficie)
    tile(3, 0, bricks)      # 3: pietra rovine
    tile(4, 0, plank)       # 4: piattaforma di legno (attraversabile dal basso)
    tile(5, 0, grave)       # 5: lapide (decorazione)
    tile(6, 0, bones)       # 6: ossa (decorazione)
    tile(7, 0, spikes)      # 7: punte (mortali)
    tile(0, 1, cave_wall)   # 8: parete grotta (sfondo)
    return img


# ---------------------------------------------------------------------------
# Sfondi parallax 384x216 (ripetibili in orizzontale), stile notte di Monkey Island
# ---------------------------------------------------------------------------
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def dither_grad(img, y0, y1, stops):
    """Gradiente a bande con dithering ordinato, come nei giochi VGA."""
    w = img.width
    n = len(stops) - 1
    for y in range(y0, y1):
        t = (y - y0) / max(1, (y1 - y0 - 1)) * n
        i = min(int(t), n - 1)
        f = t - i
        for x in range(w):
            c = stops[i + 1] if f * 16 > BAYER[y % 4][x % 4] + 0.5 else stops[i]
            img.putpixel((x, y), rgba(c))


def sky():
    W, H = 384, 216
    img = Image.new("RGBA", (W, H))
    dither_grad(img, 0, H, [(14, 10, 38), (24, 22, 70), (40, 44, 106), (70, 62, 128), (112, 82, 136)])
    rnd = random.Random(11)
    for _ in range(90):
        x, y = rnd.randrange(W), rnd.randrange(int(H * 0.6))
        c = rnd.choice([(255, 255, 255), (200, 210, 255), (255, 240, 200)])
        img.putpixel((x, y), rgba(c, 255 if rnd.random() < 0.4 else 150))
        if rnd.random() < 0.08:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                img.putpixel(((x + dx) % W, max(0, y + dy)), rgba(c, 110))
    # luna grande con alone
    mx, my, mr = 300, 48, 22
    for y in range(my - mr - 14, my + mr + 14):
        for x in range(mx - mr - 14, mx + mr + 14):
            d = math.hypot(x - mx, y - my)
            if d <= mr:
                base = (236, 232, 206)
                if math.hypot(x - mx - 6, y - my + 5) < 5 or math.hypot(x - mx + 8, y - my - 7) < 4:
                    base = (206, 200, 176)
                if d > mr - 2:
                    base = (210, 206, 182)
                img.putpixel((x, y), rgba(base))
            elif d < mr + 14 and (x + y) % 2 == 0 and d < mr + 6 + BAYER[y % 4][x % 4] / 2:
                old = img.getpixel((x, y))
                img.putpixel((x, y), rgba(lerp(old, (150, 140, 190), 0.4)))
    # nuvole sottili davanti alla luna
    for cy, cx0, cx1 in ((58, 250, 350), (66, 270, 330), (30, 60, 140), (38, 40, 110)):
        for x in range(cx0, cx1):
            for y in range(cy, cy + 3):
                if (x + y) % 2 == 0 or y == cy + 1:
                    img.putpixel((x % W, y), rgba((84, 76, 140)))
    return img


def silhouette(seed, base_y, amp, col, col_top, features=None):
    W, H = 384, 216
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rnd = random.Random(seed)
    # profilo periodico (somma di sinusoidi con periodo = W) così si ripete senza giunture
    waves = [(rnd.randrange(1, 4), rnd.random() * math.tau, rnd.random()) for _ in range(4)]
    heights = []
    for x in range(W):
        h = base_y
        for k, ph, a in waves:
            h += math.sin(x / W * math.tau * k + ph) * amp * a / 2
        heights.append(int(h))
    for x in range(W):
        for y in range(heights[x], H):
            c = col_top if y - heights[x] < 2 else col
            img.putpixel((x, y), rgba(c))
    if features:
        features(img, heights, rnd)
    return img


def mountains():
    return silhouette(5, 120, 70, (36, 34, 76), (60, 56, 110))


def hills():
    dark = (22, 20, 44)

    def feats(img, hts, rnd):
        W = img.width
        # castello in rovina (la tana dei goblin sul colle)
        cx = 230
        gy = hts[cx]
        for x in range(cx - 26, cx + 26):
            top = gy - 30
            if abs(x - cx) > 14:
                top = gy - 22
            if (x - (cx - 26)) % 6 < 3:
                top -= 3
            if cx - 26 + 34 < x < cx - 26 + 40:
                top += 9  # crollo
            for y in range(top, gy + 2):
                img.putpixel((x, y), rgba(dark))
        for x, y in ((cx - 5, gy - 22), (cx + 6, gy - 18)):
            img.putpixel((x, y), rgba((240, 180, 60)))  # finestre illuminate
            img.putpixel((x, y + 1), rgba((200, 120, 40)))
        # alberi spogli
        for _ in range(7):
            x = rnd.randrange(W)
            if abs(x - cx) < 40:
                continue
            gy = hts[x]
            h = rnd.randrange(14, 26)

            def branch(x0, y0, ang, ln, d):
                if ln < 2 or d > 4:
                    return
                x1, y1 = x0 + math.sin(ang) * ln, y0 - math.cos(ang) * ln
                n = int(ln) + 1
                for i in range(n + 1):
                    t = i / n
                    img.putpixel((int(x0 + (x1 - x0) * t) % W, max(0, int(y0 + (y1 - y0) * t))), rgba(dark))
                branch(x1, y1, ang - 0.6 + rnd.random() * 0.2, ln * 0.65, d + 1)
                branch(x1, y1, ang + 0.5 + rnd.random() * 0.2, ln * 0.6, d + 1)

            for i in range(h // 2):
                img.putpixel((x, gy - i), rgba(dark))
                img.putpixel(((x + 1) % W, gy - i), rgba(dark))
            branch(x, gy - h // 2, 0, h / 2, 0)

    return silhouette(9, 160, 40, dark, (40, 38, 70), feats)


def fog():
    W, H = 384, 216
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for y in range(150, H):
        for x in range(W):
            band = math.sin(x / W * math.tau * 3 + y * 0.15) * 0.5 + 0.5
            if (y - 150) / 66 * 16 * band > BAYER[y % 4][x % 4] + 4:
                img.putpixel((x, y), rgba((120, 110, 170), 70))
    return img


# ---------------------------------------------------------------------------
# Effetti sonori 8-bit (wav mono 22 kHz)
# ---------------------------------------------------------------------------
def sfx(name, dur, f0, f1, wave_kind="square", noise=0.0, vol=0.35):
    rate = 22050
    n = int(rate * dur)
    rnd = random.Random(name)
    ph = 0.0
    data = []
    for i in range(n):
        t = i / n
        f = f0 + (f1 - f0) * t
        ph += f / rate
        if wave_kind == "square":
            v = 1.0 if (ph % 1) < 0.5 else -1.0
        else:
            v = 2 * abs(2 * (ph % 1) - 1) - 1
        v = v * (1 - noise) + (rnd.random() * 2 - 1) * noise
        env = min(1.0, i / 200) * (1 - t) ** 1.5
        data.append(int(max(-1, min(1, v * env * vol)) * 32767))
    with wave.open(os.path.join(ROOT, "sfx", name + ".wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(b"".join(struct.pack("<h", s) for s in data))


def cave_exit():
    """Ingresso della tana dei goblin (fine livello), 48x48."""
    cv = Canvas(48, 48)
    for y in range(4, 48):
        for x in range(2, 46):
            d = math.hypot((x - 24) / 21, (y - 30) / 26)
            if d < 1:
                cv.put(x, y, (96, 92, 108) if ((x // 6 + y // 5) % 2) else (82, 78, 94), 1)
    for y in range(14, 48):
        for x in range(10, 38):
            d = math.hypot((x - 24) / 13, (y - 34) / 20)
            if d < 1:
                cv.put(x, y, (8, 6, 10) if d < 0.8 else (24, 18, 26), -1)
    # occhi gialli nel buio
    for ex in (19, 22, 28, 31):
        cv.put(ex, 30 if ex < 25 else 36, (250, 210, 40), -2)
    cv.shade_pass()
    cv.outline_pass()
    return cv.image()


def main():
    # Il giocatore, il tileset, gli sfondi e gli oggetti ora vengono dai pacchetti Gothicvania
    # (tools/import_packs.py). Qui restano i goblin, gli effetti e i suoni.
    cave_exit().save(os.path.join(ROOT, "sprites", "cave.png"))
    gob = [draw_goblin(i) for i in range(4)] + [draw_goblin(0, jump=True), draw_goblin(1, hurt=True),
                                                 draw_goblin(0, attack=True)]
    sheet(gob, 32, 32).save(os.path.join(ROOT, "sprites", "goblin.png"))
    sheet(puff_frames(), 16, 16).save(os.path.join(ROOT, "sprites", "puff.png"))
    sheet(spark_frames(), 8, 8).save(os.path.join(ROOT, "sprites", "spark.png"))
    sheet(armor_bits(), 8, 8).save(os.path.join(ROOT, "sprites", "armor_bits.png"))
    sfx("throw", 0.12, 900, 300, noise=0.3)
    sfx("jump", 0.15, 220, 520, "tri", vol=0.4)
    sfx("hit", 0.18, 300, 60, noise=0.6)
    sfx("goblin_die", 0.3, 500, 80, noise=0.4)
    sfx("armor_lost", 0.4, 700, 120, noise=0.5, vol=0.4)
    sfx("pickup", 0.25, 400, 1200, "tri", vol=0.4)
    sfx("death", 0.9, 400, 40, vol=0.4)
    print("Asset generati in", os.path.normpath(ROOT))


if __name__ == "__main__":
    main()

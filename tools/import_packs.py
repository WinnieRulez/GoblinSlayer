#!/usr/bin/env python3
"""Converte la grafica dei pacchetti Gothicvania (assets_src/) nei file usati dal gioco (assets/).

Uso:  python3 tools/import_packs.py      (richiede Pillow)
- Goblin Slayer: l'eroe di "Gothic hero" ricolorato (armatura d'acciaio sporca, mantello di cuoio,
  pennacchio rosso) in due versioni: con armatura e senza.
- Lupo dei goblin: "Hell hound".
- Tileset, sfondi e decorazioni: "Gothic horror", "Night town", oggetti e scenografie.
- Spettro: "Ghost"; palla di fuoco del bastone: "Hell beast".
- Armi da raccogliere: pacchetto "5 RPG weapons" (assets_src/rpgweapons).
- Lapidi, alberi morti, scale, fianco delle colline e nebbia: disegnati qui, con la tavolozza del pacchetto,
  seguendo i riferimenti di Ghosts'n Goblins (cimitero con colline a due piani e scale).
"""
import math
import random
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "assets_src", "gothicvania")
OUT = os.path.join(HERE, "..", "assets")


def src(*p):
    return Image.open(os.path.join(SRC, *p)).convert("RGBA")


def out(img, *p):
    path = os.path.join(OUT, *p)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)


def frames(img, n):
    w = img.width // n
    return [img.crop((i * w, 0, (i + 1) * w, img.height)) for i in range(n)]


def recolor(img, mapping):
    img = img.copy()
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            if a and (r, g, b) in mapping:
                px[x, y] = mapping[(r, g, b)] + (a,)
    return img


# --------------------------------------------------------------------------- eroe
GOLD = [(255, 204, 97), (225, 146, 77), (188, 108, 23), (152, 62, 29), (103, 25, 21), (105, 26, 23)]
CAPE = [(237, 5, 62), (129, 9, 54), (128, 7, 53)]
SKIN = [(255, 217, 185), (255, 201, 139)]
HAIR = [(175, 151, 133)]
CLOTH = [(87, 59, 96), (150, 100, 149)]

ARMOR_MAP = dict(zip(GOLD, [(178, 180, 184), (138, 140, 146), (104, 106, 112), (74, 74, 80), (48, 46, 52), (48, 46, 52)]))
ARMOR_MAP.update(dict(zip(CAPE, [(112, 86, 60), (72, 54, 40), (72, 54, 40)])))
ARMOR_MAP.update(dict(zip(SKIN, [(138, 140, 146), (74, 74, 80)])))       # il viso diventa elmo
ARMOR_MAP.update(dict(zip(HAIR, [(170, 40, 36)])))                         # i capelli diventano pennacchio
ARMOR_MAP.update(dict(zip(CLOTH, [(62, 52, 46), (96, 82, 70)])))

PLAIN_MAP = dict(zip(GOLD, [(222, 204, 164), (184, 160, 120), (142, 116, 84), (102, 80, 58), (66, 50, 38), (66, 50, 38)]))
PLAIN_MAP.update(dict(zip(CAPE, [(112, 86, 60), (72, 54, 40), (72, 54, 40)])))
PLAIN_MAP.update(dict(zip(HAIR, [(88, 64, 46)])))
PLAIN_MAP.update(dict(zip(CLOTH, [(62, 52, 46), (96, 82, 70)])))

CELL_W, CELL_H, COLS = 96, 80, 12
# animazione: (file, n. fotogrammi, quali usare)
HERO_ANIMS = [
    ("idle", "gothic-hero-idle.png", 4, None),
    ("run", "gothic-hero-run.png", 12, None),
    ("attack", "gothic-hero-attack.png", 6, None),
    ("jump", "gothic-hero-jump.png", 5, None),
    ("crouch", "gothic-hero-crouch.png", 3, None),
    ("crouch_attack", "gothic-hero-crouch-slash.png", 4, None),
    ("hurt", "gothic-hero-hurt.png", 3, None),
    ("jump_attack", "gothic-hero-jump-attack.png", 6, None),
]


def snap_palette(img):
    """I fotogrammi del secondo pacchetto dell'eroe hanno colori leggermente diversi: li porto
    sulla tavolozza del primo, così il ricolore funziona anche su di loro."""
    pal = GOLD + CAPE + SKIN + HAIR + CLOTH
    img = img.copy()
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            if not a:
                continue
            best = min(pal, key=lambda c: (c[0] - r) ** 2 + (c[1] - g) ** 2 + (c[2] - b) ** 2)
            if (best[0] - r) ** 2 + (best[1] - g) ** 2 + (best[2] - b) ** 2 < 60 ** 2:
                px[x, y] = best + (a,)
    return img


def body_x(fr):
    """Centro orizzontale del corpo: media delle x dei pixel nelle 10 righe più alte (testa)."""
    px = fr.load()
    bb = fr.getbbox()
    xs = []
    for y in range(bb[1], min(bb[1] + 10, fr.height)):
        for x in range(fr.width):
            if px[x, y][3]:
                xs.append(x)
    return sum(xs) / len(xs)


def build_hero():
    rows = []
    for name, fname, n, _ in HERO_ANIMS:
        frs = frames(src("hero", fname), n)
        anchor = sum(body_x(f) for f in frs) / len(frs)
        row = []
        for f in frs:
            cell = Image.new("RGBA", (CELL_W, CELL_H))
            # piedi in fondo alla cella, corpo al centro (x = 48)
            bottom = f.getbbox()[3]
            cell.alpha_composite(f, (int(round(CELL_W / 2 - anchor)), CELL_H - bottom))
            row.append(cell)
        rows.append(row)
    # morto: ultimo fotogramma di "hurt" coricato a terra
    lying = rows[6][2].rotate(90, expand=False)
    bb = lying.getbbox()
    dead = Image.new("RGBA", (CELL_W, CELL_H))
    dead.alpha_composite(lying.crop(bb), (CELL_W // 2 - (bb[2] - bb[0]) // 2, CELL_H - (bb[3] - bb[1])))
    rows.append([dead])
    # scala a pioli: i due fotogrammi "braccio in alto" del salto-arrampicata, più le versioni specchiate
    climb = []
    for f in frames(src("hero", "gothic-hero-jump-climb.png"), 7)[2:4]:
        f = f.crop(f.getbbox())
        climb.append(snap_palette(f))
    climb += [f.transpose(Image.FLIP_LEFT_RIGHT) for f in climb]
    row = []
    for f in climb:
        cell = Image.new("RGBA", (CELL_W, CELL_H))
        cell.alpha_composite(f, (CELL_W // 2 - f.width // 2, CELL_H - f.height))
        row.append(cell)
    rows.append(row)
    sheet = Image.new("RGBA", (CELL_W * COLS, CELL_H * len(rows)))
    for r, row in enumerate(rows):
        for c, cell in enumerate(row):
            sheet.alpha_composite(cell, (c * CELL_W, r * CELL_H))
    out(recolor(sheet, ARMOR_MAP), "sprites", "slayer_armor.png")
    out(recolor(sheet, PLAIN_MAP), "sprites", "slayer_noarmor.png")


# --------------------------------------------------------------------------- lupo
def build_hound():
    anims = [("hell-hound-walk.png", 12), ("hell-hound-run.png", 5), ("hell-hound-jump.png", 6), ("hell-hound-idle.png", 6)]
    W, H, cols = 72, 48, 12
    sheet = Image.new("RGBA", (W * cols, H * len(anims)))
    for r, (f, n) in enumerate(anims):
        for c, fr in enumerate(frames(src("hound", f), n)):
            bb = fr.getbbox()
            sheet.alpha_composite(fr, (c * W + (W - fr.width) // 2, r * H + H - bb[3]))
    # da cane infernale a lupo grigio: la lava diventa pelo, gli occhi azzurri diventano gialli
    px = sheet.load()
    for y in range(sheet.height):
        for x in range(sheet.width):
            r, g, b, a = px[x, y]
            if not a:
                continue
            if r > b + 30:
                l = (r * 0.5 + g * 0.35 + b * 0.15)
                px[x, y] = (int(l * 0.62 + 40), int(l * 0.56 + 34), int(l * 0.5 + 30), a)
            elif b > r + 60 and g > r + 40:
                px[x, y] = (250, 210, 60, a)
    out(sheet, "sprites", "wolf.png")


# --------------------------------------------------------------------------- tileset 16x16
def build_tiles():
    h = src("horror", "tiles.png")
    T = 16
    ts = Image.new("RGBA", (T * 8, T * 3))

    def put(i, img):
        ts.alpha_composite(img, ((i % 8) * T, (i // 8) * T))

    crop = lambda x, y: h.crop((x, y, x + T, y + T))
    put(0, crop(48, 64))    # superficie con erba
    put(8, crop(64, 64))    # superficie con erba (variante)
    put(1, crop(32, 80))    # terra/mattoni sotto la superficie
    put(9, crop(64, 80))    # variante
    put(2, crop(176, 64))   # pietra: superficie
    put(10, crop(192, 64))  # pietra: superficie (variante)
    put(3, crop(336, 80))   # pietra: riempimento
    put(11, crop(352, 80))
    put(16, crop(384, 96))
    put(17, crop(400, 96))
    put(12, crop(32, 16))   # asse: estremità sinistra
    put(4, crop(48, 16))    # asse: centro
    put(13, crop(96, 16))   # asse: estremità destra
    # punte arrugginite (disegnate a mano, nello stile del pacchetto)
    sp = Image.new("RGBA", (T, T))
    px = sp.load()
    for i in range(4):
        bx = i * 4
        for y in range(6, T):
            w = (y - 6) // 2
            for x in range(bx + 2 - w, bx + 2 + w):
                if 0 <= x < T:
                    c = (186, 168, 150) if x < bx + 2 else (120, 92, 76)
                    if y > 12:
                        c = (92, 50, 36)
                    px[x, y] = c + (255,)
    put(7, sp)
    out(ts, "tiles", "tileset.png")


# --------------------------------------------------------------------------- decorazioni e oggetti
DECOR = {  # nome: (file, riquadro)
    "skull_pike": ("misc_scenery.png", (141, 5, 152, 72)),
    "pike": ("misc_scenery.png", (121, 5, 126, 72)),
    "skull_totem": ("misc_scenery.png", (39, 88, 49, 108)),
    "skull_totem2": ("misc_scenery.png", (52, 90, 62, 108)),
    "mushroom": ("misc_scenery.png", (25, 111, 39, 131)),
    "mushrooms": ("misc_scenery.png", (5, 118, 20, 131)),
    "rock": ("misc_scenery.png", (85, 130, 112, 154)),
    "sword_rock": ("misc_scenery.png", (84, 88, 111, 126)),
    "candle": ("misc_scenery.png", (72, 132, 79, 153)),
    "cage": ("misc_scenery.png", (44, 8, 76, 85)),
}
ITEMS = {
    "armor": ("00_items.png", (35, 6, 64, 36)),
    "heart": ("00_items.png", (137, 49, 148, 60)),
    "shield": ("00_items.png", (11, 75, 27, 91)),
}


def build_decor():
    for name, (f, box) in DECOR.items():
        out(src("extra", f).crop(box), "decor", name + ".png")
    for name, (f, box) in ITEMS.items():
        out(src("extra", f).crop(box), "sprites", name + ".png")
    # pugnale da lancio: preso dal set di oggetti e coricato in orizzontale
    dag = src("extra", "00_items.png").crop((202, 83, 207, 104)).rotate(-90, expand=True)
    out(dag, "sprites", "dagger.png")


# --------------------------------------------------------------------------- sfondi
def build_backgrounds():
    W, H = 384, 224
    def tiled(img, y=0):
        o = Image.new("RGBA", (W, H))
        x = 0
        while x < W:
            o.alpha_composite(img, (x, y))
            x += img.width
        return o
    out(tiled(src("town-bg", "night-town-background-sky.png")), "backgrounds", "sky.png")
    clouds = src("town-bg", "night-town-background-clouds.png")
    c = Image.new("RGBA", (clouds.width, H)); c.alpha_composite(clouds)
    out(c, "backgrounds", "clouds.png")
    out(tiled(src("town-bg", "night-town-background-mountains.png")), "backgrounds", "mountains.png")
    forest = tiled(src("town-bg", "night-town-background-forest.png"), 128)
    out(forest, "backgrounds", "forest.png")
    town = Image.new("RGBA", (512, H)); town.alpha_composite(src("town-bg", "night-town-background-town.png"), (0, 125))
    out(town, "backgrounds", "town.png")

# --------------------------------------------------------------------------- spettro
def build_ghost():
    """Spettro incappucciato: celle 64x80, una riga per animazione (idle 7, appare 6, svanisce 7, urlo 4)."""
    W, H, cols = 64, 80, 7
    anims = [("ghost-idle.png", 7), ("ghost-appears.png", 6), ("ghost-vanish.png", 7), ("ghost-shriek.png", 4)]
    sheet = Image.new("RGBA", (W * cols, H * len(anims)))
    for r, (f, n) in enumerate(anims):
        for c, fr in enumerate(frames(src("ghost", f), n)):
            sheet.alpha_composite(fr, (c * W + (W - fr.width) // 2, r * H + (H - fr.height) // 2))
    out(sheet, "sprites", "ghost.png")
    out(src("fire", "fire-ball.png"), "sprites", "fireball.png")


# --------------------------------------------------------------------------- armi
WEAPONS = ["silverhalberd", "battlehammer", "enchantedbow", "earthstaff", "machete"]


def build_weapons():
    """Icone 16x16 (raccolta e HUD) e proiettili: l'icona punta in alto a sinistra, la giro verso destra."""
    for name in WEAPONS:
        icon = Image.open(os.path.join(HERE, "..", "assets_src", "rpgweapons", name + ".png")).convert("RGBA")
        out(icon, "sprites", "weapons", name + ".png")
        if name not in ("enchantedbow", "earthstaff"):
            pr = icon.rotate(-135, resample=Image.NEAREST, expand=True)
            out(pr.crop(pr.getbbox()), "sprites", "weapons", name + "_shot.png")
    # freccia per l'arco
    a = Image.new("RGBA", (14, 5))
    px = a.load()
    for x in range(2, 11):
        px[x, 2] = (150, 100, 60, 255)
    for x, y in [(0, 0), (1, 1), (0, 4), (1, 3), (1, 0), (2, 1), (1, 4), (2, 3)]:
        px[x, y] = (230, 230, 220, 255)
    for x, y in [(11, 1), (11, 2), (11, 3), (12, 2), (13, 2), (12, 1), (12, 3)]:
        px[x, y] = (200, 206, 214, 255) if x < 13 else (240, 244, 250, 255)
    out(a, "sprites", "weapons", "arrow.png")


# --------------------------------------------------------------------------- disegno a pixel
OUTLINE = (24, 18, 28, 255)


def outline(img, color=OUTLINE):
    """Bordo scuro di 1 pixel attorno alle parti opache (come gli sprite del pacchetto)."""
    o = img.copy()
    src_px, px = img.load(), o.load()
    for y in range(img.height):
        for x in range(img.width):
            if src_px[x, y][3]:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                xx, yy = x + dx, y + dy
                if 0 <= xx < img.width and 0 <= yy < img.height and src_px[xx, yy][3]:
                    px[x, y] = color
                    break
    return o


STONE = [(58, 56, 72), (88, 86, 104), (118, 116, 134), (152, 150, 166)]
MOSS = [(52, 84, 46), (84, 120, 58)]


def tombstone(kind, seed):
    rnd = random.Random(seed)
    if kind == "round":
        w, h = 16, 20
        inside = lambda x, y: (y >= 7 and 1 <= x <= w - 2) or (x - 7.5) ** 2 + (y - 7.5) ** 2 <= 6.8 ** 2
    elif kind == "cross":
        w, h = 14, 22
        inside = lambda x, y: (5 <= x <= 8 and y >= 1) or (1 <= x <= 12 and 5 <= y <= 8) or (y >= 18 and 2 <= x <= 11)
    else:  # lastra larga e bassa
        w, h = 22, 15
        inside = lambda x, y: 1 <= x <= w - 2 and y >= 2 and not ((x in (1, w - 2)) and y == 2)
    img = Image.new("RGBA", (w, h))
    px = img.load()
    for y in range(h - 1):
        for x in range(w):
            if not inside(x, y):
                continue
            # luce dall'alto a sinistra, ombra a destra
            edge_l = not inside(x - 1, y) or not inside(x, y - 1)
            edge_r = not inside(x + 1, y) or not inside(x + 2, y)
            c = STONE[3] if edge_l else (STONE[1] if edge_r else STONE[2])
            if rnd.random() < 0.08:
                c = STONE[1]
            px[x, y] = c + (255,)
    # incisione
    cx = w // 2
    if kind == "round":
        for y in range(8, 15):
            px[cx, y] = STONE[0] + (255,)
        for x in range(cx - 2, cx + 3):
            px[x, 10] = STONE[0] + (255,)
    elif kind == "slab":
        for x in range(5, w - 5, 2):
            px[x, 6] = STONE[0] + (255,)
        for x in range(4, w - 4, 3):
            px[x, 9] = STONE[0] + (255,)
    # crepa
    x, y = rnd.randint(3, w - 4), rnd.randint(3, 6)
    for _ in range(5):
        if inside(x, y):
            px[x, y] = STONE[0] + (255,)
        x += rnd.choice((-1, 0, 1)); y += 1
    # muschio alla base
    for x in range(w):
        for y in range(h - 5, h - 1):
            if px[x, y][3] and rnd.random() < 0.35 + (y - (h - 5)) * 0.15:
                px[x, y] = rnd.choice(MOSS) + (255,)
    return outline(img)


BARK = [(46, 30, 34), (74, 50, 46), (108, 76, 62)]


def dead_tree(seed, w=72, h=96):
    """Albero morto e contorto, come quelli del cimitero di Ghosts'n Goblins."""
    rnd = random.Random(seed)
    img = Image.new("RGBA", (w, h))
    px = img.load()

    def disc(cx, cy, r, shade):
        for y in range(int(cy - r - 1), int(cy + r + 2)):
            for x in range(int(cx - r - 1), int(cx + r + 2)):
                if 0 <= x < w and 0 <= y < h and (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                    lit = (x - cx) < -r * 0.3
                    px[x, y] = (BARK[2] if lit else BARK[1] if shade else BARK[0]) + (255,)

    def branch(x, y, ang, length, r, depth):
        steps = int(length)
        for i in range(steps):
            ang += rnd.uniform(-0.12, 0.12)
            x += math.cos(ang)
            y -= math.sin(ang)
            rr = max(0.5, r * (1 - i / steps * 0.45))
            disc(x, y, rr, True)
        if depth <= 0 or r < 0.8:
            return
        for d in (-1, 1):
            if rnd.random() < 0.9:
                branch(x, y, ang + d * rnd.uniform(0.35, 0.9), length * rnd.uniform(0.5, 0.75), r * 0.62, depth - 1)

    # radici
    for d in (-1, 1):
        branch(w / 2, h - 3, math.pi / 2 + d * 1.35, 10, 2.2, 0)
    branch(w / 2, h - 2, math.pi / 2 + rnd.uniform(-0.1, 0.1), h * 0.42, 4.2, 4)
    return outline(img)


def build_graveyard():
    for i, (kind, seed) in enumerate([("round", 3), ("cross", 5), ("slab", 7), ("round", 11)]):
        out(tombstone(kind, seed), "decor", "tomb_%d.png" % i)
    out(dead_tree(4), "decor", "dead_tree_0.png")
    out(dead_tree(9, 56, 80), "decor", "dead_tree_1.png")


def build_hill_tiles():
    """Tessere per le colline a due piani (cima attraversabile, fianco di terra, scale a pioli).
    Vengono aggiunte al tileset già creato da build_tiles()."""
    T = 16
    path = os.path.join(OUT, "tiles", "tileset.png")
    ts = Image.open(path).convert("RGBA")
    h = src("horror", "tiles.png")

    def put(i, img):
        ts.paste(img, ((i % 8) * T, (i // 8) * T))

    put(5, h.crop((48, 64, 64, 80)))
    put(6, h.crop((64, 64, 80, 80)))
    # fianco della collina: terra scura con radici e sassi (ripetibile)
    rnd = random.Random(21)
    for n, i in enumerate((14, 15, 22, 23)):
        t = Image.new("RGBA", (T, T), (62, 36, 38, 255))
        px = t.load()
        for y in range(T):
            for x in range(T):
                v = rnd.random()
                if v < 0.12:
                    px[x, y] = (78, 46, 44, 255)
                elif v < 0.16:
                    px[x, y] = (46, 26, 30, 255)
        for _ in range(2):  # sassi
            cx, cy = rnd.randint(2, 13), rnd.randint(2, 13)
            for y in range(cy - 1, cy + 2):
                for x in range(cx - 2, cx + 2):
                    if 0 <= x < T and 0 <= y < T:
                        px[x, y] = (112, 78, 66, 255) if y == cy - 1 else (88, 58, 52, 255)
            if cy + 2 < T:
                for x in range(cx - 2, cx + 2):
                    if 0 <= x < T:
                        px[x, cy + 2] = (40, 22, 26, 255)
        x, y = rnd.randint(0, 15), 0  # radice
        while y < T:
            if 0 <= x < T:
                px[x, y] = (104, 70, 50, 255)
            y += 1
            x += rnd.choice((-1, 0, 0, 1))
        put(i, t)
    # scala a pioli
    lad = Image.new("RGBA", (T, T))
    px = lad.load()
    for y in range(T):
        for x, c in ((2, (40, 24, 24)), (3, (168, 112, 64)), (4, (110, 66, 40)), (5, (40, 24, 24)),
                     (10, (40, 24, 24)), (11, (168, 112, 64)), (12, (110, 66, 40)), (13, (40, 24, 24))):
            px[x, y] = c + (255,)
    for ry in (2, 7, 12):
        for x in range(5, 11):
            px[x, ry] = (40, 24, 24, 255)
            px[x, ry + 1] = (150, 98, 56, 255)
            px[x, ry + 2] = (90, 54, 34, 255)
    put(18, lad)
    # cima della collina con la scala che spunta
    top = h.crop((48, 64, 64, 80))
    top.alpha_composite(lad.crop((0, 6, T, T)), (0, 6))
    put(19, top)
    ts.save(path)


def build_fog():
    W, H = 384, 64
    img = Image.new("RGBA", (W, H))
    px = img.load()
    for y in range(H):
        for x in range(W):
            a = x / W * 2 * math.pi
            n = (math.sin(a * 3 + y * 0.09) + math.sin(a * 7 + 1.3) * 0.6 + math.sin(a * 13 + y * 0.2) * 0.3) / 1.9
            v = max(0.0, (y / H) * 0.9 + n * 0.35 - 0.25)
            alpha = int(min(1.0, v) * 110)
            # retino a 2x2 per restare "pixel art"
            if (x + y) % 2 and alpha < 40:
                alpha = 0
            px[x, y] = (150, 170, 200, alpha)
    out(img, "backgrounds", "fog.png")


if __name__ == "__main__":
    build_hero()
    build_hound()
    build_tiles()
    build_decor()
    build_backgrounds()
    build_ghost()
    build_weapons()
    build_graveyard()
    build_hill_tiles()
    build_fog()
    print("Grafica importata in", os.path.normpath(OUT))

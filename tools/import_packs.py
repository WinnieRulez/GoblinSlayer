#!/usr/bin/env python3
"""Converte la grafica dei pacchetti Gothicvania (assets_src/) nei file usati dal gioco (assets/).

Uso:  python3 tools/import_packs.py      (richiede Pillow)
- Goblin Slayer: l'eroe di "Gothic hero" ricolorato (armatura d'acciaio sporca, mantello di cuoio,
  pennacchio rosso) in due versioni: con armatura e senza.
- Lupo dei goblin: "Hell hound".
- Tileset, sfondi e decorazioni: "Gothic horror", "Night town", oggetti e scenografie.
"""
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


if __name__ == "__main__":
    build_hero()
    build_hound()
    build_tiles()
    build_decor()
    build_backgrounds()
    print("Grafica importata in", os.path.normpath(OUT))

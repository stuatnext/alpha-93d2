#!/usr/bin/env python3
"""
NEXT Retreats 2026 — banner ad generator (SUMMERY theme).

Bright, sun-drenched treatment per Martin's feedback (the dark luxury version is in
git history): turquoise-sea-to-warm-sand gradient, sunny glow, deep teal-navy text,
NEXT signature yellow on the CTA, and the NEXT>.io wordmark recoloured dark so it
reads on a light background.

Run:  python3 generate_banners.py
Output: ../<edition>/banners/*.png

SCENIC PHOTO / NEW LOGO:
- To use a real venue photo as the background, drop a JPG/PNG at the path in each
  edition's "photo" key (see EDITIONS) and re-run — it will be cover-fitted with a
  light scrim so text stays legible.
- LatAm has a new co-branded logo: drop it at brand/next-logo-latam.png and set the
  edition's "logo" key; otherwise the default wordmark is used.
"""

import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
BRAND = os.path.join(ROOT, "brand")
DEFAULT_LOGO = os.path.join(BRAND, "next-logo.png")
FONTS = "/mnt/skills/examples/canvas-design/canvas-fonts"

# --- Summery palette ---
YELLOW = (255, 207, 51)        # #ffcf33 — NEXT signature (CTA + chevron)
INK = (10, 54, 61)             # deep teal-navy — primary text on light bg
SUBINK = (74, 99, 102)         # muted supporting text
DIVIDER = (188, 206, 208)      # soft light divider
SS = 3                         # supersample factor

# Gradient stops (sky -> sea -> sand)
SKY = (203, 237, 244)
SEA = (90, 204, 198)
SAND = (248, 240, 221)


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), int(size * SS))


F_DISPLAY = "BigShoulders-Bold.ttf"
F_BOLD = "Outfit-Bold.ttf"
F_MED = "Outfit-Medium.ttf"
F_REG = "WorkSans-Regular.ttf"
for cand in ("Outfit-Medium.ttf", "Outfit-Regular.ttf", "WorkSans-Medium.ttf"):
    if os.path.exists(os.path.join(FONTS, cand)):
        F_MED = cand
        break

EDITIONS = {
    "europe-cyprus": {
        "region": "EUROPE",
        "place": "CYPRUS",
        "dates": "12–14 OCTOBER 2026",
        "venue": "Cap St George Resort",
        "accent_b": (13, 108, 150),    # Mediterranean azure (place name + accents)
        "glow": (175, 226, 232),       # soft aqua glow
        "photo": os.path.join(BRAND, "photo-europe.jpg"),   # optional
        "logo": DEFAULT_LOGO,
    },
    "latam-cancun": {
        "region": "LATAM",
        "place": "CANCÚN",
        "dates": "17–19 NOVEMBER 2026",
        "venue": "Secrets Maroma Beach",
        "accent_b": (228, 74, 38),     # Caribbean coral (place name + accents)
        "glow": (255, 214, 178),       # soft peach glow
        "photo": os.path.join(BRAND, "photo-latam.jpg"),    # optional (the beach shot)
        "logo": os.path.join(BRAND, "next-logo-latam.png"), # new co-branded lockup
    },
}

SUBLINE = "50 operators · 50 suppliers · by invitation only"
CTA = "SPONSOR NOW"
CTA_SHORT = "SPONSOR NOW"


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
def s(v):
    return int(v * SS)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def text_size(d, s_, f):
    b = d.textbbox((0, 0), s_, font=f)
    return b[2] - b[0], b[3] - b[1]


def draw_text(d, xy, s_, f, fill, anchor="la", tracking=0):
    if tracking == 0:
        d.text(xy, s_, font=f, fill=fill, anchor=anchor)
        return
    tr = tracking * SS
    widths = [text_size(d, ch, f)[0] for ch in s_]
    total = sum(widths) + tr * (len(s_) - 1)
    x, y = xy
    if anchor[0] == "m":
        x -= total / 2
    elif anchor[0] == "r":
        x -= total
    va = anchor[1] if len(anchor) > 1 else "a"
    for ch, w in zip(s_, widths):
        d.text((x, y), ch, font=f, fill=fill, anchor="l" + va)
        x += w + tr


def chevron(d, x, y, h, color):
    w = h * 0.62
    t = h * 0.42
    d.polygon([(x, y), (x + t, y), (x + w, y + h / 2),
               (x + t, y + h), (x, y + h), (x + w - t, y + h / 2)], fill=color)


def rounded(d, box, r, fill):
    d.rounded_rectangle(box, radius=r, fill=fill)


def radial_glow(img, center, radius, color, max_alpha):
    cx, cy = center
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    steps = 30
    for i in range(steps, 0, -1):
        rr = radius * i / steps
        a = int(max_alpha * (1 - i / steps) ** 1.6)
        gd.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=color + (a,))
    img.alpha_composite(glow)


_logo_cache = {}


def load_logo(path, target_w, darken=True):
    if not path or not os.path.exists(path):
        path = DEFAULT_LOGO   # fall back until the real asset is committed
    key = (path, int(target_w), darken)
    if key in _logo_cache:
        return _logo_cache[key]
    logo = Image.open(path).convert("RGBA")
    if darken:
        # recolour near-white pixels to INK so the wordmark reads on light bg;
        # leave coloured (yellow/red) pixels untouched.
        px = logo.load()
        w, h = logo.size
        for yy in range(h):
            for xx in range(w):
                r, g, b, a = px[xx, yy]
                if a > 0 and r > 200 and g > 200 and b > 200:
                    px[xx, yy] = (INK[0], INK[1], INK[2], a)
    w, h = logo.size
    tw = int(target_w)
    th = int(h * tw / w)
    out = logo.resize((tw, th), Image.LANCZOS)
    _logo_cache[key] = out
    return out


def gradient_base(W, H):
    """Vertical sky->sea->sand gradient via a 1px column resized up."""
    col = Image.new("RGB", (1, H))
    cp = col.load()
    for y in range(H):
        f = y / max(1, H - 1)
        if f < 0.52:
            c = lerp(SKY, SEA, f / 0.52)
        else:
            c = lerp(SEA, SAND, (f - 0.52) / 0.48)
        cp[0, y] = c
    return col.resize((W, H)).convert("RGBA")


def base_canvas(w, h, ed):
    W, H = w * SS, h * SS
    photo = ed.get("photo")
    if photo and os.path.exists(photo):
        img = Image.open(photo).convert("RGBA")
        # cover-fit
        iw, ih = img.size
        scale = max(W / iw, H / ih)
        img = img.resize((int(iw * scale), int(ih * scale)), Image.LANCZOS)
        img = img.crop((0, 0, W, H))
        # light wash so dark text reads, keeps it bright & summery
        wash = Image.new("RGBA", (W, H), (255, 255, 255, 90))
        img.alpha_composite(wash)
    else:
        img = gradient_base(W, H)
    # sunny highlight top-right + soft accent glow bottom-left
    radial_glow(img, (W * 0.9, H * 0.05), max(W, H) * 0.7, (255, 255, 255), 150)
    radial_glow(img, (W * 0.04, H * 0.96), max(W, H) * 0.7, ed["glow"], 110)
    return img


def finish(img, w, h, path):
    out = img.convert("RGB").resize((w, h), Image.LANCZOS)
    out.save(path, "PNG")
    print(f"  {os.path.basename(path):28s} {w}x{h}")


def pill(d, cx, y, text, f, pad_x=18, pad_y=11, fill=YELLOW, fg=INK):
    tw, th = text_size(d, text, f)
    pad_x *= SS
    pad_y *= SS
    bw = tw + pad_x * 2
    bh = th + pad_y * 2
    rounded(d, [cx - bw / 2, y, cx + bw / 2, y + bh], bh / 2, fill)
    d.text((cx, y + bh / 2), text, font=f, fill=fg, anchor="mm")
    return bh / SS


# ----------------------------------------------------------------------------
# Layouts
# ----------------------------------------------------------------------------
def mpu_300x250(ed, path):
    W, H = 300, 250
    img = base_canvas(W, H, ed)
    d = ImageDraw.Draw(img)
    img.alpha_composite(load_logo(ed["logo"], 108 * SS), (s(20), s(20)))
    draw_text(d, (s(20), s(74)), "RETREAT", font(F_DISPLAY, 15), ed["accent_b"], tracking=4)
    draw_text(d, (s(20), s(96)), ed["region"], font(F_DISPLAY, 46), INK)
    draw_text(d, (s(20), s(140)), ed["place"], font(F_DISPLAY, 46), ed["accent_b"])
    d.line([(s(22), s(190)), (s(60), s(190))], fill=ed["accent_b"], width=s(3))
    draw_text(d, (s(20), s(198)), ed["dates"], font(F_BOLD, 13), INK)
    draw_text(d, (s(20), s(216)), "By invitation only", font(F_REG, 10.5), SUBINK)
    pill(d, s(208), s(198), CTA_SHORT, font(F_BOLD, 11.5), pad_x=13, pad_y=8)
    finish(img, W, H, path)


def leaderboard_728x90(ed, path):
    W, H = 728, 90
    img = base_canvas(W, H, ed)
    d = ImageDraw.Draw(img)
    logo = load_logo(ed["logo"], 120 * SS)
    img.alpha_composite(logo, (s(26), (H * SS - logo.size[1]) // 2))
    d.line([(s(170), s(22)), (s(170), s(68))], fill=DIVIDER, width=s(2))
    draw_text(d, (s(192), s(24)), "RETREAT " + ed["region"] + " · " + ed["place"],
              font(F_DISPLAY, 30), INK)
    draw_text(d, (s(193), s(57)), ed["dates"] + "  ·  " + ed["venue"].upper(),
              font(F_MED, 13), ed["accent_b"], tracking=1)
    pill(d, s(648), s(28), CTA, font(F_BOLD, 13), pad_x=16, pad_y=10)
    finish(img, W, H, path)


def skyscraper_300x600(ed, path):
    W, H = 300, 600
    img = base_canvas(W, H, ed)
    d = ImageDraw.Draw(img)
    chevron(d, s(208), s(34), s(80), ed["accent_b"])
    img.alpha_composite(load_logo(ed["logo"], 150 * SS), (s(28), s(46)))
    draw_text(d, (s(30), s(150)), "THE INVITATION-ONLY", font(F_MED, 12), SUBINK, tracking=2)
    draw_text(d, (s(30), s(168)), "iGAMING RETREAT", font(F_MED, 12), SUBINK, tracking=2)
    draw_text(d, (s(30), s(212)), "RETREAT", font(F_DISPLAY, 22), ed["accent_b"], tracking=6)
    draw_text(d, (s(30), s(242)), ed["region"], font(F_DISPLAY, 70), INK)
    draw_text(d, (s(30), s(312)), ed["place"], font(F_DISPLAY, 70), ed["accent_b"])
    d.line([(s(32), s(404)), (s(86), s(404))], fill=ed["accent_b"], width=s(4))
    draw_text(d, (s(30), s(420)), ed["dates"], font(F_BOLD, 19), INK)
    draw_text(d, (s(30), s(448)), ed["venue"], font(F_MED, 15), SUBINK)
    draw_text(d, (s(30), s(486)), "50 operators.", font(F_MED, 14), INK)
    draw_text(d, (s(30), s(506)), "50 suppliers.", font(F_MED, 14), INK)
    draw_text(d, (s(30), s(526)), "By invitation only.", font(F_MED, 14), ed["accent_b"])
    pill(d, s(150), s(556), CTA, font(F_BOLD, 14), pad_x=20, pad_y=11)
    finish(img, W, H, path)


def megabanner_1400x300(ed, path):
    W, H = 1400, 300
    img = base_canvas(W, H, ed)
    d = ImageDraw.Draw(img)
    chevron(d, s(60), s(108), s(86), ed["accent_b"])
    img.alpha_composite(load_logo(ed["logo"], 210 * SS), (s(132), s(74)))
    draw_text(d, (s(136), s(150)), "THE INVITATION-ONLY iGAMING RETREAT",
              font(F_MED, 13), SUBINK, tracking=2)
    draw_text(d, (s(136), s(174)), "50 OPERATORS · 50 SUPPLIERS",
              font(F_MED, 13), ed["accent_b"], tracking=2)
    draw_text(d, (s(636), s(60)), "RETREAT", font(F_DISPLAY, 30), ed["accent_b"], tracking=8)
    draw_text(d, (s(634), s(94)), ed["region"], font(F_DISPLAY, 86), INK)
    draw_text(d, (s(634), s(180)), ed["place"], font(F_DISPLAY, 86), ed["accent_b"])
    draw_text(d, (s(1356), s(96)), ed["dates"], font(F_BOLD, 25), INK, anchor="ra")
    draw_text(d, (s(1356), s(132)), ed["venue"], font(F_MED, 16), SUBINK, anchor="ra")
    pill(d, s(1242), s(180), CTA, font(F_BOLD, 19), pad_x=26, pad_y=15)
    finish(img, W, H, path)


def slidein_300x300(ed, path):
    W, H = 300, 300
    img = base_canvas(W, H, ed)
    d = ImageDraw.Draw(img)
    img.alpha_composite(load_logo(ed["logo"], 116 * SS), (s(22), s(24)))
    draw_text(d, (s(24), s(86)), "RETREAT", font(F_DISPLAY, 16), ed["accent_b"], tracking=5)
    draw_text(d, (s(24), s(110)), ed["region"], font(F_DISPLAY, 52), INK)
    draw_text(d, (s(24), s(160)), ed["place"], font(F_DISPLAY, 52), ed["accent_b"])
    d.line([(s(26), s(222)), (s(70), s(222))], fill=ed["accent_b"], width=s(3))
    draw_text(d, (s(24), s(232)), ed["dates"], font(F_BOLD, 14), INK)
    draw_text(d, (s(24), s(252)), "Invitation only", font(F_REG, 11), SUBINK)
    pill(d, s(214), s(240), CTA_SHORT, font(F_BOLD, 12), pad_x=14, pad_y=8)
    finish(img, W, H, path)


def popup_640x360(ed, path):
    W, H = 640, 360
    img = base_canvas(W, H, ed)
    d = ImageDraw.Draw(img)
    chevron(d, s(548), s(40), s(70), ed["accent_b"])
    img.alpha_composite(load_logo(ed["logo"], 150 * SS), (s(40), s(42)))
    draw_text(d, (s(42), s(120)), "THE INVITATION-ONLY iGAMING RETREAT",
              font(F_MED, 13), SUBINK, tracking=2)
    draw_text(d, (s(42), s(150)), "RETREAT", font(F_DISPLAY, 26), ed["accent_b"], tracking=7)
    draw_text(d, (s(40), s(180)), ed["region"] + " · " + ed["place"],
              font(F_DISPLAY, 74), INK)
    d.line([(s(44), s(268)), (s(96), s(268))], fill=ed["accent_b"], width=s(4))
    draw_text(d, (s(42), s(280)), ed["dates"] + "  ·  " + ed["venue"],
              font(F_BOLD, 17), INK)
    draw_text(d, (s(42), s(304)), SUBLINE, font(F_REG, 13), SUBINK)
    pill(d, s(118), s(330), CTA, font(F_BOLD, 14), pad_x=20, pad_y=11)
    draw_text(d, (s(250), s(338)), "Operators attend by invitation", font(F_MED, 12),
              ed["accent_b"])
    finish(img, W, H, path)


FORMATS = [
    ("MPU_300x250.png", mpu_300x250),
    ("Leaderboard_728x90.png", leaderboard_728x90),
    ("Skyscraper_300x600.png", skyscraper_300x600),
    ("Megabanner_1400x300.png", megabanner_1400x300),
    ("SlideIn_300x300.png", slidein_300x300),
    ("PopUp_640x360.png", popup_640x360),
]


def main():
    for key, ed in EDITIONS.items():
        outdir = os.path.join(ROOT, key, "banners")
        os.makedirs(outdir, exist_ok=True)
        print(f"\n{key}:")
        for fname, fn in FORMATS:
            fn(ed, os.path.join(outdir, fname))


if __name__ == "__main__":
    main()

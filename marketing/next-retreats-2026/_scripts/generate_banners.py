#!/usr/bin/env python3
"""
NEXT Retreats 2026 — banner ad generator.

Produces the full display set for both editions (Europe / Cyprus and LatAm /
Cancun) in the NEXT brand: deep-black canvas, signature yellow (#ffcf33), white
"NEXT>.io" wordmark and a chevron motif lifted from the logo.

Run:  python3 generate_banners.py
Output: ../<edition>/banners/*.png

Everything that marketing might want to tweak (dates, venue, CTA, copy) lives in
the EDITIONS dict below — change a string, re-run, done.
"""

import os
from PIL import Image, ImageDraw, ImageFont

# ----------------------------------------------------------------------------
# Paths & brand constants
# ----------------------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
LOGO = os.path.join(ROOT, "brand", "next-logo.png")
FONTS = "/mnt/skills/examples/canvas-design/canvas-fonts"

YELLOW = (255, 207, 51)        # #ffcf33 — NEXT signature
BLACK = (8, 8, 8)              # near-black canvas
WHITE = (255, 255, 255)
MUTED = (176, 176, 176)        # secondary text
SS = 3                         # supersample factor for crisp anti-aliasing


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size * SS)


# Type stack
F_DISPLAY = "BigShoulders-Bold.ttf"   # condensed headline / dominant
F_BOLD = "Outfit-Bold.ttf"            # geometric, matches NEXT wordmark
F_MED = "Outfit-Medium.ttf"
F_REG = "WorkSans-Regular.ttf"

# Fallbacks if a weight isn't present
for cand in ("Outfit-Medium.ttf", "Outfit-Regular.ttf", "WorkSans-Medium.ttf"):
    if os.path.exists(os.path.join(FONTS, cand)):
        F_MED = cand
        break


# ----------------------------------------------------------------------------
# Edition content  (verify dates/venue against the live page before printing)
# ----------------------------------------------------------------------------
EDITIONS = {
    "europe-cyprus": {
        "region": "EUROPE",
        "place": "CYPRUS",
        "dates": "12–14 OCTOBER 2026",
        "venue": "Cap St George Resort",
        "accent_a": (15, 32, 76),    # deep Mediterranean blue
        "accent_b": (43, 183, 179),  # Aegean teal
        "tagline": "Where iGaming's leaders meet the Med.",
    },
    "latam-cancun": {
        "region": "LATAM",
        "place": "CANCÚN",
        "dates": "NOVEMBER 2026",
        "venue": "Secrets Maroma Beach",
        "accent_a": (122, 24, 84),   # deep magenta
        "accent_b": (255, 138, 76),  # Caribbean sunset
        "tagline": "Where iGaming's leaders meet the Caribbean.",
    },
}

# Shared positioning line
SUBLINE = "50 operators · 50 suppliers · by invitation only"
CTA = "BECOME A SPONSOR"      # full pill (paid sell — never "apply"/"partner")
CTA_SHORT = "SPONSOR"          # tight formats (MPU / SlideIn)


# ----------------------------------------------------------------------------
# Drawing helpers
# ----------------------------------------------------------------------------
def text_size(d, s, f):
    b = d.textbbox((0, 0), s, font=f)
    return b[2] - b[0], b[3] - b[1]


def draw_text(d, xy, s, f, fill, anchor="la", tracking=0):
    """Draw text with optional letter-spacing (tracking in *unscaled* px)."""
    if tracking == 0:
        d.text(xy, s, font=f, fill=fill, anchor=anchor)
        return
    tr = tracking * SS
    widths = [text_size(d, ch, f)[0] for ch in s]
    total = sum(widths) + tr * (len(s) - 1)
    x, y = xy
    if anchor[0] == "m":
        x -= total / 2
    elif anchor[0] == "r":
        x -= total
    va = anchor[1] if len(anchor) > 1 else "a"
    for ch, w in zip(s, widths):
        d.text((x, y), ch, font=f, fill=fill, anchor="l" + va)
        x += w + tr


def chevron(d, x, y, h, color, weight_ratio=0.42, gap_ratio=0.0):
    """The NEXT '>' chevron. x,y = top-left of bounding box, h = height."""
    w = h * 0.62
    t = h * weight_ratio
    pts_outer = [(x, y), (x + w, y + h / 2), (x, y + h)]
    # build a thick chevron as two quads
    inner_w = w - t
    d.polygon([(x, y), (x + t, y), (x + w, y + h / 2),
               (x + t, y + h), (x, y + h), (x + w - t, y + h / 2)], fill=color)


def rounded(d, box, r, fill):
    d.rounded_rectangle(box, radius=r, fill=fill)


def gradient_glow(img, center, radius, color, max_alpha=120):
    """Soft radial glow blended onto img (RGB)."""
    cx, cy = center
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    steps = 28
    for i in range(steps, 0, -1):
        rr = radius * i / steps
        a = int(max_alpha * (1 - i / steps) ** 1.6)
        gd.ellipse([cx - rr, cy - rr, cx + rr, cy + rr],
                   fill=color + (a,))
    img.alpha_composite(glow)


def load_logo(target_w):
    logo = Image.open(LOGO).convert("RGBA")
    w, h = logo.size
    target_w = int(target_w)
    th = int(h * target_w / w)
    return logo.resize((target_w, th), Image.LANCZOS)


def base_canvas(w, h, ed):
    """Black canvas with a region-tinted corner glow and chevron watermark."""
    img = Image.new("RGBA", (w * SS, h * SS), BLACK + (255,))
    gradient_glow(img, (w * SS * 0.86, h * SS * 0.12),
                  max(w, h) * SS * 0.95, ed["accent_b"], 70)
    gradient_glow(img, (w * SS * 0.05, h * SS * 0.95),
                  max(w, h) * SS * 0.8, ed["accent_a"], 90)
    return img


def finish(img, w, h, path):
    out = img.convert("RGB").resize((w, h), Image.LANCZOS)
    out.save(path, "PNG")
    print(f"  {os.path.basename(path):28s} {w}x{h}")


def pill(d, cx, y, text, f, pad_x=18, pad_y=11, fill=YELLOW, fg=BLACK):
    tw, th = text_size(d, text, f)
    pad_x *= SS
    pad_y *= SS
    bw = tw + pad_x * 2
    bh = th + pad_y * 2
    box = [cx - bw / 2, y, cx + bw / 2, y + bh]
    rounded(d, box, bh / 2, fill)
    d.text((cx, y + bh / 2), text, font=f, fill=fg, anchor="mm")
    return bh / SS


# ----------------------------------------------------------------------------
# Per-format layouts (all coordinates in unscaled px, multiplied by SS at draw)
# ----------------------------------------------------------------------------
def s(v):
    return int(v * SS)


def mpu_300x250(ed, path):
    W, H = 300, 250
    img = base_canvas(W, H, ed)
    d = ImageDraw.Draw(img)
    logo = load_logo(108 * SS)
    img.alpha_composite(logo, (s(20), s(20)))
    draw_text(d, (s(20), s(74)), "RETREAT", font(F_DISPLAY, 15), YELLOW, tracking=4)
    draw_text(d, (s(20), s(96)), ed["region"], font(F_DISPLAY, 46), WHITE)
    draw_text(d, (s(20), s(140)), ed["place"], font(F_DISPLAY, 46), ed["accent_b"])
    d.line([(s(22), s(190)), (s(60), s(190))], fill=YELLOW, width=s(3))
    draw_text(d, (s(20), s(198)), ed["dates"], font(F_BOLD, 13), WHITE)
    draw_text(d, (s(20), s(216)), "By invitation only", font(F_REG, 10.5), MUTED)
    pill(d, s(208), s(198), CTA_SHORT, font(F_BOLD, 11.5), pad_x=13, pad_y=8)
    finish(img, W, H, path)


def leaderboard_728x90(ed, path):
    W, H = 728, 90
    img = base_canvas(W, H, ed)
    d = ImageDraw.Draw(img)
    logo = load_logo(120 * SS)
    lh = logo.size[1]
    img.alpha_composite(logo, (s(26), (H * SS - lh) // 2))
    d.line([(s(170), s(22)), (s(170), s(68))], fill=(60, 60, 60), width=s(2))
    draw_text(d, (s(192), s(24)), "RETREAT " + ed["region"] + " · " + ed["place"],
              font(F_DISPLAY, 30), WHITE)
    draw_text(d, (s(193), s(57)), ed["dates"] + "  ·  " + ed["venue"].upper(),
              font(F_MED, 13), ed["accent_b"], tracking=1)
    pill(d, s(648), s(28), CTA, font(F_BOLD, 13), pad_x=16, pad_y=10)
    finish(img, W, H, path)


def skyscraper_300x600(ed, path):
    W, H = 300, 600
    img = base_canvas(W, H, ed)
    d = ImageDraw.Draw(img)
    chevron(d, s(208), s(34), s(80), YELLOW)
    logo = load_logo(150 * SS)
    img.alpha_composite(logo, (s(28), s(46)))
    draw_text(d, (s(30), s(150)), "THE INVITATION-ONLY", font(F_MED, 12), MUTED, tracking=2)
    draw_text(d, (s(30), s(168)), "iGAMING RETREAT", font(F_MED, 12), MUTED, tracking=2)
    draw_text(d, (s(30), s(212)), "RETREAT", font(F_DISPLAY, 22), YELLOW, tracking=6)
    draw_text(d, (s(30), s(242)), ed["region"], font(F_DISPLAY, 70), WHITE)
    draw_text(d, (s(30), s(312)), ed["place"], font(F_DISPLAY, 70), ed["accent_b"])
    d.line([(s(32), s(404)), (s(86), s(404))], fill=YELLOW, width=s(4))
    draw_text(d, (s(30), s(420)), ed["dates"], font(F_BOLD, 19), WHITE)
    draw_text(d, (s(30), s(448)), ed["venue"], font(F_MED, 15), MUTED)
    draw_text(d, (s(30), s(486)), "50 operators.", font(F_MED, 14), WHITE)
    draw_text(d, (s(30), s(506)), "50 suppliers.", font(F_MED, 14), WHITE)
    draw_text(d, (s(30), s(526)), "By invitation only.", font(F_MED, 14), ed["accent_b"])
    pill(d, s(150), s(556), CTA, font(F_BOLD, 14), pad_x=20, pad_y=11)
    finish(img, W, H, path)


def megabanner_1400x300(ed, path):
    W, H = 1400, 300
    img = base_canvas(W, H, ed)
    d = ImageDraw.Draw(img)
    # --- Brand zone (left): chevron + logo + one tidy tagline line ---
    chevron(d, s(60), s(108), s(86), YELLOW)
    logo = load_logo(210 * SS)
    img.alpha_composite(logo, (s(132), s(74)))
    draw_text(d, (s(136), s(150)), "THE INVITATION-ONLY iGAMING RETREAT",
              font(F_MED, 13), MUTED, tracking=2)
    draw_text(d, (s(136), s(174)), "50 OPERATORS · 50 SUPPLIERS",
              font(F_MED, 13), ed["accent_b"], tracking=2)
    # --- Headline zone (centre): clear of the brand zone, room to breathe ---
    draw_text(d, (s(636), s(60)), "RETREAT", font(F_DISPLAY, 30), YELLOW, tracking=8)
    draw_text(d, (s(634), s(94)), ed["region"], font(F_DISPLAY, 86), WHITE)
    draw_text(d, (s(634), s(180)), ed["place"], font(F_DISPLAY, 86), ed["accent_b"])
    # --- CTA zone (right): dates + venue + button, well clear of headline ---
    draw_text(d, (s(1356), s(96)), ed["dates"], font(F_BOLD, 25), WHITE, anchor="ra")
    draw_text(d, (s(1356), s(132)), ed["venue"], font(F_MED, 16), MUTED, anchor="ra")
    pill(d, s(1242), s(180), CTA, font(F_BOLD, 19), pad_x=26, pad_y=15)
    finish(img, W, H, path)


def slidein_300x300(ed, path):
    W, H = 300, 300
    img = base_canvas(W, H, ed)
    d = ImageDraw.Draw(img)
    logo = load_logo(116 * SS)
    img.alpha_composite(logo, (s(22), s(24)))
    draw_text(d, (s(24), s(86)), "RETREAT", font(F_DISPLAY, 16), YELLOW, tracking=5)
    draw_text(d, (s(24), s(110)), ed["region"], font(F_DISPLAY, 52), WHITE)
    draw_text(d, (s(24), s(160)), ed["place"], font(F_DISPLAY, 52), ed["accent_b"])
    d.line([(s(26), s(222)), (s(70), s(222))], fill=YELLOW, width=s(3))
    draw_text(d, (s(24), s(232)), ed["dates"], font(F_BOLD, 14), WHITE)
    draw_text(d, (s(24), s(252)), "Invitation only", font(F_REG, 11), MUTED)
    pill(d, s(214), s(240), CTA_SHORT, font(F_BOLD, 12), pad_x=14, pad_y=8)
    finish(img, W, H, path)


def popup_640x360(ed, path):
    W, H = 640, 360
    img = base_canvas(W, H, ed)
    d = ImageDraw.Draw(img)
    chevron(d, s(548), s(40), s(70), YELLOW)
    logo = load_logo(150 * SS)
    img.alpha_composite(logo, (s(40), s(42)))
    draw_text(d, (s(42), s(120)), "THE INVITATION-ONLY iGAMING RETREAT",
              font(F_MED, 13), MUTED, tracking=2)
    draw_text(d, (s(42), s(150)), "RETREAT", font(F_DISPLAY, 26), YELLOW, tracking=7)
    draw_text(d, (s(40), s(180)), ed["region"] + " · " + ed["place"],
              font(F_DISPLAY, 74), WHITE)
    d.line([(s(44), s(268)), (s(96), s(268))], fill=YELLOW, width=s(4))
    draw_text(d, (s(42), s(280)), ed["dates"] + "  ·  " + ed["venue"],
              font(F_BOLD, 17), WHITE)
    draw_text(d, (s(42), s(304)), SUBLINE, font(F_REG, 13), MUTED)
    pill(d, s(118), s(330)-s(0), CTA, font(F_BOLD, 14), pad_x=20, pad_y=11)
    # second CTA hint for suppliers
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

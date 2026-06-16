# NEXT Retreats 2026 — Marketing Pack

Lead-generation marketing kit for the two 2026 editions of the NEXT Retreat:

| Edition | When | Where | Page |
|---|---|---|---|
| **NEXT Retreat Europe** | 12–14 October 2026 | Cap St George Resort, Cyprus | [next.io/next-retreats/europe-cyprus](https://next.io/next-retreats/europe-cyprus/) |
| **NEXT Retreat LatAm** | November 2026 | Secrets Maroma Beach, Riviera Cancún, Mexico | [next.io/next-retreats/latam-cancun](https://next.io/next-retreats/latam-cancun/) |

> ⚠️ **Verify before publishing.** The live retreat pages were not machine-readable
> at build time, so dates/venues below were taken from NEXT's own 2026 planning and
> sponsorship documents (most recent: June 2026). Confirmed: **Europe = 12–14 Oct
> 2026, Cyprus**. To confirm: **LatAm exact November dates** (planning docs reference
> a Nov 11–13 window at Secrets Maroma Beach) and the final **Cyprus venue** (Cap St
> George vs. a move to Parklane, Limassol — Cap St George used here). All of these are
> single-string edits — see "Editing" below.

---

## What the NEXT Retreat is (positioning used throughout)

An **invitation-only** gathering of **50 top-tier operators and 50 leading suppliers**
— 100 specially invited guests — for three days of high-level discussion, networking
and entertainment at a luxury resort. One region in focus at a time (Europe =
emerging European markets; LatAm = the Latin American market). **Closed-door, no
media.** Where business meets pleasure and the people who shape iGaming actually talk.

**Current campaign focus = selling sponsorships.** Primary CTA across the pack is
**"Become a sponsor"** — deliberately *not* "apply" (implies free) or "partnership"
(also gets misread as free). A price anchor is used in the sponsor emails to make the
commercial nature unmistakable.

- **Sponsors (suppliers)** buy a **paid sponsorship package** → CTA: *Become a sponsor*
- **Operators** attend **free, by invitation** → secondary CTA: *Request your invite*
- Sponsorship packages: **Headline €85k (×1)**, **General €35k (×20)**, **Activity €10–20k (×5)**

**Brand:** near-black canvas (`#080808`), signature yellow (`#FFCF33`), white
`NEXT>.io` wordmark, condensed display type. Region accents — Europe: Aegean
teal/Mediterranean blue; LatAm: Caribbean sunset/magenta.

---

## Contents

```
next-retreats-2026/
├── brand/                      NEXT logo + colour reference
├── europe-cyprus/
│   ├── banners/                6 display sizes (PNG)
│   ├── emails/                 sponsors-sequence + operators-attend-sequence
│   └── social/                 LinkedIn, X, Instagram copy
├── latam-cancun/               (same structure)
├── chatgpt-prompts.md          Image-gen prompts (photo-based banners)
└── _scripts/
    └── generate_banners.py     Regenerates every banner from one config
```

### Banner set (per edition)
| File | Size | Typical placement |
|---|---|---|
| `MPU_300x250.png` | 300×250 | Medium rectangle, in-content |
| `Leaderboard_728x90.png` | 728×90 | Top/bottom of page |
| `Skyscraper_300x600.png` | 300×600 | Sidebar half-page |
| `Megabanner_1400x300.png` | 1400×300 | Wide hero / billboard |
| `SlideIn_300x300.png` | 300×300 | Slide-in square |
| `PopUp_640x360.png` | 640×360 | Interstitial / pop-up |

---

## Editing

All banner copy (dates, venue, CTA, accent colours) lives in the `EDITIONS` dict at
the top of `_scripts/generate_banners.py`. Change a string and regenerate:

```bash
cd _scripts
pip install Pillow      # if not already present
python3 generate_banners.py
```

Banners render at 3× supersampling for crisp text, then downscale to exact spec size.

Email and social copy are plain Markdown — edit directly. Subject lines, preview text
and CTAs are called out so they can be dropped straight into HubSpot / your ESP.

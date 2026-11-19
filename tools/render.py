"""Draw "THE WORLD TODAY" for Thursday 19 November 2026.

A dense broadsheet: 32 stories in three columns, drawn from scratch with
Pillow shapes and text only. No photos, no copied art, no network, no
randomness and no timestamps, so every run writes the same PNG bytes.

Run:  python3 tools/render.py   (from anywhere; paths are script-relative)
Out:  assets/entry.png, 1024x1024, under 1 MiB.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = ROOT / "assets" / "entry.png"
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")

PAGE_W, PAGE_H = 1024, 1024
MARGIN = 34
GUTTER = 18
COL_W = (PAGE_W - 2 * MARGIN - 2 * GUTTER) // 3

PAPER = (248, 244, 233)
INK = (26, 26, 26)
SOFT = (90, 90, 90)
RED = (179, 38, 30)
NAVY = (27, 42, 74)
HAIR = (203, 198, 184)


def load(name, size):
    path = FONT_DIR / name
    if not path.exists():
        raise SystemExit(f"font missing: {path}")
    return ImageFont.truetype(str(path), size)


F = {
    "mast": load("DejaVuSerif-Bold.ttf", 52),
    "date": load("DejaVuSerif-Bold.ttf", 20),
    "lead": load("DejaVuSerif-Bold.ttf", 33),
    "kick": load("DejaVuSans-Bold.ttf", 12),
    "head": load("DejaVuSans-Bold.ttf", 17),
    "head1": load("DejaVuSans-Bold.ttf", 16),
    "body": load("DejaVuSans.ttf", 16),
    "det": load("DejaVuSans.ttf", 13),
    "sect": load("DejaVuSans-Bold.ttf", 13),
    "num": load("DejaVuSerif-Bold.ttf", 22),
    "numlab": load("DejaVuSans.ttf", 12),
    "foot": load("DejaVuSans.ttf", 12),
}

# (kicker, title, detail, featured?)
COLUMNS = [
    ("WORLD", [
        ("GULF CONFLICT", "Iran hits US bases; US strikes Qeshm",
         "Tanker struck in the Strait of Hormuz too.", True),
        ("UKRAINE WAR", "Kerch Bridge hit for a third time this week",
         "Ukraine struck the Crimean Bridge again.", True),
        ("GAZA", "West presses Israel to let aid reach flooded Gaza",
         "Rain displaced 46,000+ households.", True),
        ("ISRAEL", "Eisenkot to form government",
         "Herzog taps Eisenkot, bypassing Netanyahu", False),
        ("THE HAGUE", "World court to rule on Myanmar",
         "Genocide claims over the Rohingya.", False),
        ("TRADE", "EU backs Indonesia trade pact",
         "Pact cuts tariffs, counters US duties.", False),
        ("EUROPE", "EU proposes €45bn Ukraine loan",
         "Repayable after Russian reparations.", False),
        ("AMERICAS", "US and Venezuela restore ties",
         "Training and intelligence sharing resume.", False),
        ("HORN OF AFRICA", "Ethiopia, Eritrea mass troops",
         "Unconfirmed clashes near Badme.", False),
        ("BANGLADESH", "Garment workers strike, week 3",
         "Tear gas used; factories shut.", False),
        ("NORTH KOREA", "North Korea expands enrichment",
         "IAEA cites growth at Yongbyon.", False),
    ]),
    ("MARKETS & TECH", [
        ("MARKETS", "Anthropic debuts after record $81.3bn IPO",
         "Shares trade on Nasdaq as ANT at $83.", True),
        ("AI CHIPS", "Nvidia revenue doubles to $115.8bn",
         "Sales up 103% on a year ago.", True),
        ("FED", "Fed rate hold was a close call",
         "Almost all officials expect more hikes.", False),
        ("BANKS", "Deutsche Bank probed after leak",
         "Over 15 million files leaked.", False),
        ("INDIA", "India seeks 20% defence rise",
         "114 Rafale jets, six submarines.", False),
        ("MALAYSIA", "Malaysia's economy grows 5.5%",
         "Third-quarter GDP beats forecasts.", False),
        ("AUSTRALIA", "Australia jobless rate hits 4.9%",
         "ASX falls 1.04%, sixth day in a row.", False),
    ]),
    ("SCIENCE & HEALTH", [
        ("SPACE", "Voyager 1 reaches a light-day from Earth",
         "NASA probe believed to pass milestone.", True),
        ("CLIMATE", "COP31 awaits deal text",
         "Second Global Stocktake now under way.", False),
        ("HEALTH", "Glucose implant treats diabetes",
         "Device normalises blood sugar in rats.", False),
        ("PHYSICS", "Message sent through gravity",
         "Signal passes through a brick wall.", False),
        ("THE MOON", "First moonquake shaking model",
         "Ground-motion model built for Moon.", False),
        ("WEATHER", "India braces for Cyclone Akvan",
         "Odisha prepares; Delhi schools reopen.", False),
    ]),
    ("SPORT & CULTURE", [
        ("GAMING", "GTA 6 launches today",
         "1,600 Bengaluru developers worked on it.", True),
        ("CRICKET", "India dominate New Zealand in first Test",
         "Hosts 60/4 at lunch in Wellington.", True),
        ("BADMINTON", "Sindhu back in world top five",
         "Indian star climbs the rankings.", False),
        ("CRICKET", "Liton Das sets keeping record",
         "Eight dismissals in one innings.", False),
        ("FOOTBALL", "Chelsea beat PSG 1-0 in Europe",
         "Buurman scores 87th-minute winner.", False),
        ("TENNIS", "Alcaraz beats Medvedev in Turin",
         "Wins 6-2, 6-4 at the ATP Finals.", False),
        ("CRICKET", "England clinch ODI series",
         "Duckett century seals Hobart win.", False),
    ]),
]

# Columns are laid out as: [col1], [col2 top, col2 bottom], [col3 top, col3 bottom]
LAYOUT = [
    [COLUMNS[0]],
    [COLUMNS[1], ("SPACE & CLIMATE", COLUMNS[2][1][:2])],
    [("SCIENCE & HEALTH", COLUMNS[2][1][2:]), COLUMNS[3]],
]

LEAD_KICK = "SHENZHEN SUMMIT — DIPLOMACY"
LEAD_HEAD = "Trump, Xi and Putin meet in first three-way summit"
LEAD_SUM = ("The three leaders held their first talks together in Shenzhen, "
            "on the APEC sidelines, with nuclear arms, Ukraine and the Iran "
            "conflict on the agenda.")

NUMBERS = [
    ("$81.3bn", "Anthropic IPO, largest on record"),
    ("46,000+", "households displaced by Gaza floods"),
    ("1,600", "Bengaluru developers on GTA 6"),
    ("$115.8bn", "Nvidia quarterly revenue, up 103%"),
]

FOOTER = "32 STORIES · ALL FROM REPORTS PUBLISHED THURSDAY 19 NOVEMBER 2026"


def split_words(draw, text, font, width, limit):
    """Greedy wrap on word boundaries; fail loudly instead of clipping."""
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=font) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    if len(lines) > limit:
        raise SystemExit(f"does not fit in {limit} line(s): {text!r} -> {lines}")
    for line in lines:
        if draw.textlength(line, font=font) > width:
            raise SystemExit(f"single word too wide: {line!r}")
    return lines


def draw_lines(draw, x, y, lines, font, fill, gap):
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += font.size + gap
    return y


def story_height(draw, kick, title, detail, featured):
    h = 0
    if featured:
        h += F["kick"].size + 3
        lines = split_words(draw, title, F["head"], COL_W, 2)
        h += len(lines) * (F["head"].size + 2)
        h += 3
        split_words(draw, detail, F["det"], COL_W, 1)
        h += F["det"].size + 2
    else:
        split_words(draw, title, F["head1"], COL_W, 1)
        h += F["head1"].size + 2
        split_words(draw, detail, F["det"], COL_W, 1)
        h += F["det"].size + 2
    return h + 9  # divider + breathing room


def section_height(draw, name, stories):
    h = F["sect"].size + 8
    for kick, title, detail, featured in stories:
        h += story_height(draw, kick, title, detail, featured)
    return h


def main():
    img = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
    d = ImageDraw.Draw(img)

    # --- measure the lead first: its line count sets where the grid starts ---
    head_lines = split_words(d, LEAD_HEAD, F["lead"], PAGE_W - 2 * MARGIN, 2)
    sum_lines = split_words(d, LEAD_SUM, F["body"], PAGE_W - 2 * MARGIN, 2)
    grid_top = (14 + 62 + 4 + 26 + 10 + 17
                + len(head_lines) * (F["lead"].size + 2) + 4
                + len(sum_lines) * (F["body"].size + 3) + 6 + 8)
    grid_bottom = PAGE_H - 12 - 20 - 8 - 58
    grid_h = grid_bottom - grid_top

    # --- measure the grid so nothing can overflow silently ---
    col_h = []
    for groups in LAYOUT:
        total = 0
        for name, stories in groups:
            total += section_height(d, name, stories)
            total += 10  # gap between stacked sections
        col_h.append(total - 10)
    for i, h in enumerate(col_h):
        if h > grid_h:
            raise SystemExit(f"column {i} needs {h}px but only {grid_h}px fit")
    print(f"grid {grid_h}px; column heights {col_h}")

    y = 14
    # --- masthead ---
    title = "THE WORLD TODAY"
    d.text(((PAGE_W - d.textlength(title, font=F["mast"])) / 2, y),
           title, font=F["mast"], fill=INK)
    y += 62
    d.line([(MARGIN, y), (PAGE_W - MARGIN, y)], fill=INK, width=2)
    y += 4
    date = "THURSDAY, 19 NOVEMBER 2026"
    d.text(((PAGE_W - d.textlength(date, font=F["date"])) / 2, y),
           date, font=F["date"], fill=RED)
    y += 26
    d.line([(MARGIN, y), (PAGE_W - MARGIN, y)], fill=INK, width=1)
    y += 10

    # --- lead story, full width ---
    d.text((MARGIN, y), LEAD_KICK, font=F["kick"], fill=RED)
    y += 17
    y = draw_lines(d, MARGIN, y, head_lines, F["lead"], INK, 2)
    y += 4
    y = draw_lines(d, MARGIN, y, sum_lines, F["body"], SOFT, 3)
    y += 6
    d.line([(MARGIN, y), (PAGE_W - MARGIN, y)], fill=INK, width=2)
    y += 8
    assert y == grid_top, f"lead ends at {y}, grid_top {grid_top}"

    # --- three columns; slack is spread evenly so all end at grid_bottom ---
    for ci, groups in enumerate(LAYOUT):
        x = MARGIN + ci * (COL_W + GUTTER)
        cy = float(grid_top)
        n_items = sum(len(stories) for _, stories in groups)
        extra = (grid_h - col_h[ci]) / n_items
        for gi, (name, stories) in enumerate(groups):
            if gi:
                cy += 10
            d.text((x, cy), name, font=F["sect"], fill=RED)
            cy += F["sect"].size + 3
            d.line([(x, cy), (x + COL_W, cy)], fill=RED, width=2)
            cy += 5
            for kick, title, detail, featured in stories:
                if featured:
                    d.text((x, cy), kick, font=F["kick"], fill=NAVY)
                    cy += F["kick"].size + 3
                    lines = split_words(d, title, F["head"], COL_W, 2)
                    cy = draw_lines(d, x, cy, lines, F["head"], INK, 2)
                    cy += 3
                    d.text((x, cy), detail, font=F["det"], fill=SOFT)
                    cy += F["det"].size + 2
                else:
                    d.text((x, cy), title, font=F["head1"], fill=INK)
                    cy += F["head1"].size + 2
                    d.text((x, cy), detail, font=F["det"], fill=SOFT)
                    cy += F["det"].size + 2
                cy += 4
                d.line([(x, cy), (x + COL_W, cy)], fill=HAIR, width=1)
                cy += 5 + extra
        if ci < 2:
            sep_x = x + COL_W + GUTTER // 2
            d.line([(sep_x, grid_top), (sep_x, grid_bottom)], fill=HAIR, width=1)

    # --- numbers strip ---
    y = grid_bottom
    d.line([(MARGIN, y), (PAGE_W - MARGIN, y)], fill=INK, width=2)
    y += 8
    cell_w = (PAGE_W - 2 * MARGIN) // 4
    for i, (num, lab) in enumerate(NUMBERS):
        cx = MARGIN + i * cell_w
        d.text((cx, y), num, font=F["num"], fill=NAVY)
        lab_lines = split_words(d, lab, F["numlab"], cell_w - 12, 2)
        draw_lines(d, cx, y + F["num"].size + 4, lab_lines, F["numlab"], SOFT, 1)
    y = grid_bottom + 58
    d.line([(MARGIN, y), (PAGE_W - MARGIN, y)], fill=INK, width=1)
    y += 6
    d.text(((PAGE_W - d.textlength(FOOTER, font=F["foot"])) / 2, y),
           FOOTER, font=F["foot"], fill=SOFT)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, format="PNG", optimize=True)
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()

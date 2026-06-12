"""Build the final CineEmbed presentation.

v2 — 2026-05-19 PM rebuild after harsh visual QA.

Fixes applied vs v1:
  - add_bullets uses TWO-textbox layout (separate bullet glyph + text box)
    so wrapped lines stay aligned under the first-line text (no col-0 reset).
  - Card grids tightened on slides 3, 5, 7, 8, 11, 14, 22 — eliminates the
    0.8-2.2 in of dead-air per card flagged by QA.
  - Footer proximity resolved on slides 7, 9, 18 — bottom strips moved to
    y ≤ 6.55 in to keep ≥ 0.55 in clearance from the 7.10 in footer line.
  - Figures on slides 12, 13, 16, 17, 18 lifted upward and enlarged ~20 %
    so the projector reads axis labels and legends.
  - Slide 23 conclusion redesigned: best-configuration line converted to
    four metric chips; author line darkened for legibility on dark navy.
  - Italic gray captions darkened from SLATE → NEAR_BLACK_2 across the deck.
  - 4-stripe accent on slide-6 backbone cards reduced from 0.20 in to 0.08 in
    to match the project-wide side-stripe motif.
"""

from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt, Emu

ROOT = Path("/Users/barandincoguz/Desktop/deep learning movie project")
OUT_PATH = ROOT / "docs/final/deliverables/final_presentation.pptx"
FIG_FINAL = ROOT / "docs/final/deliverables/figures"
FIG_ART = ROOT / "artifacts/figures"
FIG_DIA = ROOT / "figures"

# ── Brand palette ─────────────────────────────────────────────────────────
PURPLE = RGBColor(0x6E, 0x56, 0xCF)
PURPLE_DARK = RGBColor(0x4C, 0x3A, 0xA1)
PURPLE_TINT = RGBColor(0xE7, 0xE0, 0xFA)
NEAR_BLACK = RGBColor(0x0F, 0x17, 0x2A)
NEAR_BLACK_2 = RGBColor(0x1E, 0x29, 0x3B)
SLATE = RGBColor(0x47, 0x55, 0x69)              # slate-600 — darkened from 500
SLATE_LIGHT = RGBColor(0xCB, 0xD5, 0xE1)        # slate-300 — brighter on dark bg
CARD_BG = RGBColor(0xFA, 0xFA, 0xFC)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
ORANGE = RGBColor(0xC2, 0x41, 0x0C)
ORANGE_TINT = RGBColor(0xFE, 0xE4, 0xD7)
GREEN = RGBColor(0x15, 0x80, 0x3D)
GREEN_TINT = RGBColor(0xD7, 0xF1, 0xDF)
AMBER = RGBColor(0xB4, 0x53, 0x09)
BORDER = RGBColor(0xE5, 0xE4, 0xEC)
RED = RGBColor(0xB9, 0x1C, 0x1C)

FONT = "Calibri"
SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)
TOTAL_SLIDES = 24


# ── Helpers ───────────────────────────────────────────────────────────────

def add_rect(slide, left, top, w, h, fill, line=None):
    shp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, w, h)
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line
        shp.line.width = Pt(0.5)
    shp.shadow.inherit = False
    return shp


def add_text(slide, left, top, w, h, text, *,
             size=14, color=NEAR_BLACK, bold=False, italic=False, align="left",
             anchor=MSO_ANCHOR.TOP, font=FONT):
    tb = slide.shapes.add_textbox(left, top, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Emu(0); tf.margin_right = Emu(0)
    tf.margin_top = Emu(0); tf.margin_bottom = Emu(0)
    tf.vertical_anchor = anchor
    lines = text.split("\n") if isinstance(text, str) else text
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = {"left": PP_ALIGN.LEFT, "right": PP_ALIGN.RIGHT,
                       "center": PP_ALIGN.CENTER}[align]
        run = p.add_run()
        run.text = line
        run.font.name = font
        run.font.size = Pt(size)
        run.font.color.rgb = color
        run.font.bold = bold
        run.font.italic = italic
    return tb


def add_bullets(slide, left, top, w, h, items, *, size=14,
                color=NEAR_BLACK, indent_color=PURPLE, line_gap=Inches(0.58),
                bullet_w=Inches(0.28)):
    """Render bullets with proper hanging indent.

    Each bullet row is two textboxes side by side: a narrow left box with
    just the bullet glyph, and a wider right box with the text. Wrapped
    text stays aligned under the first character of its own row instead
    of resetting to column 0 (the v1 bug).
    """
    y = top
    text_w = w - bullet_w
    for item in items:
        # Bullet glyph (left)
        bt = slide.shapes.add_textbox(left, y, bullet_w, line_gap * 2)
        btf = bt.text_frame
        btf.word_wrap = False
        btf.margin_left = Emu(0); btf.margin_right = Emu(0)
        btf.margin_top = Emu(0); btf.margin_bottom = Emu(0)
        bp = btf.paragraphs[0]
        br = bp.add_run()
        br.text = "▸"
        br.font.name = FONT; br.font.size = Pt(size)
        br.font.color.rgb = indent_color; br.font.bold = True

        # Text body (right)
        tx = slide.shapes.add_textbox(left + bullet_w, y, text_w, line_gap * 3)
        ttf = tx.text_frame
        ttf.word_wrap = True
        ttf.margin_left = Emu(0); ttf.margin_right = Emu(0)
        ttf.margin_top = Emu(0); ttf.margin_bottom = Emu(0)
        tp = ttf.paragraphs[0]
        if isinstance(item, tuple):
            head, rest = item
            r1 = tp.add_run()
            r1.text = head
            r1.font.name = FONT; r1.font.size = Pt(size)
            r1.font.color.rgb = color; r1.font.bold = True
            r2 = tp.add_run()
            r2.text = " " + rest
            r2.font.name = FONT; r2.font.size = Pt(size)
            r2.font.color.rgb = color
        else:
            r = tp.add_run()
            r.text = item
            r.font.name = FONT; r.font.size = Pt(size)
            r.font.color.rgb = color
        y += line_gap


def add_dotgrid_band(slide, left, top, w, h, color=PURPLE):
    add_rect(slide, left, top, w, h, PURPLE_TINT)
    step_x = Inches(0.18); step_y = Inches(0.18); dot = Inches(0.04)
    x = left + Inches(0.08)
    while x < left + w - Inches(0.08):
        y = top + Inches(0.08)
        while y < top + h - Inches(0.08):
            d = slide.shapes.add_shape(MSO_SHAPE.OVAL, x, y, dot, dot)
            d.fill.solid(); d.fill.fore_color.rgb = color
            d.line.fill.background(); d.shadow.inherit = False
            y += step_y
        x += step_x


def add_picture_safe(slide, path, left, top, w=None, h=None):
    p = ROOT / path if not Path(path).is_absolute() else Path(path)
    if not p.exists():
        add_rect(slide, left, top, w or Inches(4), h or Inches(3), BORDER)
        add_text(slide, left, top, w or Inches(4), h or Inches(3),
                 f"(missing: {p.name})", size=10, color=SLATE,
                 align="center", anchor=MSO_ANCHOR.MIDDLE)
        return
    if w and h:
        slide.shapes.add_picture(str(p), left, top, w, h)
    elif w:
        slide.shapes.add_picture(str(p), left, top, width=w)
    elif h:
        slide.shapes.add_picture(str(p), left, top, height=h)
    else:
        slide.shapes.add_picture(str(p), left, top)


def add_footer(slide, idx):
    add_text(slide, Inches(0.5), Inches(7.15), Inches(8.5), Inches(0.28),
             "CineEmbed · SENG 474 — Spring 2026 · TED University",
             size=10, color=SLATE)
    add_text(slide, Inches(11.0), Inches(7.15), Inches(2.0), Inches(0.28),
             f"{idx:02d} / {TOTAL_SLIDES:02d}",
             size=10, color=SLATE, align="right")


def add_notes(slide, text):
    """Add speaker-defense notes (presenter view). Plain text, no formatting."""
    notes_tf = slide.notes_slide.notes_text_frame
    notes_tf.text = text


def add_left_stripe(slide, color=PURPLE, width=Inches(0.08)):
    add_rect(slide, Inches(0), Inches(0), width, SLIDE_H, color)


def add_title_bar(slide, title, eyebrow=None):
    if eyebrow:
        add_text(slide, Inches(0.5), Inches(0.30), Inches(10), Inches(0.3),
                 eyebrow.upper(), size=11, color=PURPLE, bold=True)
        add_text(slide, Inches(0.5), Inches(0.60), Inches(12), Inches(0.7),
                 title, size=30, color=NEAR_BLACK, bold=True)
    else:
        add_text(slide, Inches(0.5), Inches(0.40), Inches(12), Inches(0.7),
                 title, size=30, color=NEAR_BLACK, bold=True)


def page_bg(slide, color=CARD_BG):
    add_rect(slide, Inches(0), Inches(0), SLIDE_W, SLIDE_H, color)


def add_chip(slide, left, top, w, h, label, value, *, accent=PURPLE):
    """Compact KPI chip: small uppercase label, big bold value."""
    add_rect(slide, left, top, w, h, WHITE, line=BORDER)
    add_rect(slide, left, top, Inches(0.06), h, accent)
    add_text(slide, left + Inches(0.18), top + Inches(0.10), w, Inches(0.28),
             label.upper(), size=9, color=accent, bold=True)
    add_text(slide, left + Inches(0.18), top + Inches(0.35),
             w - Inches(0.3), h - Inches(0.4),
             value, size=18, color=NEAR_BLACK, bold=True)


# ── Build presentation ────────────────────────────────────────────────────

prs = Presentation()
prs.slide_width = SLIDE_W
prs.slide_height = SLIDE_H
BLANK = prs.slide_layouts[6]


def new_slide():
    return prs.slides.add_slide(BLANK)


# ── 01. TITLE ─────────────────────────────────────────────────────────────
s = new_slide()
page_bg(s, NEAR_BLACK)
add_dotgrid_band(s, Inches(10.5), Inches(0), Inches(2.83), SLIDE_H, PURPLE)
add_text(s, Inches(0.7), Inches(1.2), Inches(11), Inches(0.5),
         "SENG 474 — FINAL PROJECT  ·  SPRING 2026",
         size=14, color=PURPLE_TINT, bold=True)
add_text(s, Inches(0.7), Inches(1.7), Inches(11), Inches(2.0),
         "CineEmbed",
         size=80, color=WHITE, bold=True)
add_text(s, Inches(0.7), Inches(3.2), Inches(11), Inches(1.4),
         "A multi-modal unsupervised\nfilm recommendation system",
         size=34, color=WHITE)
# Pre-registered hypotheses + headline at center of dark slide
add_rect(s, Inches(0.7), Inches(5.2), Inches(9.2), Inches(0.7),
         RGBColor(0x29, 0x21, 0x57))
add_text(s, Inches(0.9), Inches(5.30), Inches(8.8), Inches(0.5),
         "All three pre-registered hypotheses PASS  ·  +205 % vs non-deep baseline  ·  Two methodological findings",
         size=14, color=WHITE)
# Team and date
add_text(s, Inches(0.7), Inches(6.10), Inches(11), Inches(0.45),
         "Baran Dinçoğuz   ·   Arda Arvas   ·   Kaan Kaya",
         size=18, color=PURPLE_TINT)
add_text(s, Inches(0.7), Inches(6.55), Inches(11), Inches(0.4),
         "TED University — Department of Computer Engineering   ·   20 May 2026",
         size=14, color=SLATE_LIGHT)


# ── 02. WHY THIS PROBLEM ──────────────────────────────────────────────────
s = new_slide()
page_bg(s)
add_left_stripe(s)
add_title_bar(s, "Why this problem?", eyebrow="Motivation")

# Lead italic
add_text(s, Inches(0.5), Inches(1.50), Inches(7.8), Inches(0.6),
         "Modern catalogues host 100k+ films. No human can browse them.",
         size=18, color=NEAR_BLACK_2, italic=True)

# Bullets (4 items, hanging-indent fixed)
add_bullets(s, Inches(0.5), Inches(2.30), Inches(7.8), Inches(4.0), [
    ("Recommendation is the discovery interface",
     "— content-based, collaborative, or hybrid."),
    ("TMDb has rich metadata but no user labels",
     "— rules out collaborative filtering at source."),
    ("Content-based pipelines are cold-start-robust",
     "— immediate value on new releases."),
    ("CineEmbed asks: can purely unsupervised representation learning",
     "produce competitive retrieval on heterogeneous film metadata?"),
], size=14, line_gap=Inches(0.85))

# Stat card on right
add_rect(s, Inches(8.7), Inches(1.50), Inches(4.2), Inches(5.0), PURPLE_TINT)
add_text(s, Inches(8.7), Inches(1.75), Inches(4.2), Inches(0.5),
         "FILMS IN THE CATALOGUE",
         size=11, color=PURPLE, bold=True, align="center")
add_text(s, Inches(8.7), Inches(2.30), Inches(4.2), Inches(1.6),
         "329,044", size=64, color=PURPLE_DARK, bold=True, align="center")
add_text(s, Inches(8.7), Inches(3.85), Inches(4.2), Inches(0.5),
         "564-DIMENSIONAL FEATURE MATRIX",
         size=11, color=PURPLE, bold=True, align="center")
add_text(s, Inches(8.7), Inches(4.30), Inches(4.2), Inches(0.8),
         "7 modality blocks", size=24, color=NEAR_BLACK_2,
         bold=True, align="center")
add_text(s, Inches(8.7), Inches(4.95), Inches(4.2), Inches(1.0),
         "numerical · genre · language · decade ·\nawards · text · director",
         size=12, color=SLATE, align="center")
# Sub-stats
add_text(s, Inches(8.7), Inches(5.70), Inches(4.2), Inches(0.3),
         "z = 32  ·  L2-normalised cosine  ·  <5 ms query",
         size=11, color=PURPLE_DARK, bold=True, align="center")
add_text(s, Inches(8.7), Inches(6.00), Inches(4.2), Inches(0.3),
         "42 MB index  ·  107 passing tests",
         size=11, color=SLATE, align="center")

add_footer(s, 2)


# ── 03. WHY UNSUPERVISED ──────────────────────────────────────────────────
s = new_slide()
page_bg(s)
add_left_stripe(s)
add_title_bar(s, "Why unsupervised learning?", eyebrow="Method choice")

add_text(s, Inches(0.5), Inches(1.55), Inches(12), Inches(0.6),
         "No interaction logs. No ratings. Learn structure from item metadata alone.",
         size=18, color=NEAR_BLACK_2)

# 3-card layout — taller, denser, with sub-fact line
cards = [
    ("No user labels available",
     "TMDb dump has metadata only —\nno clicks, watches, ratings.",
     "Eliminates supervised and collaborative methods at the source.",
     "0 user IDs in the dump"),
    ("Modality variance imbalance",
     "Ratio 0.046 between text (384-d, dense)\nand sparse one-hot blocks.",
     "The central data problem — drives every architecture choice.",
     "Var(text) / Var(decade) ≈ 22"),
    ("Test-set hygiene",
     "Three label axes (genre, decade, lang)\nused only for evaluation, never training.",
     "Honest measurement of what the latent has learned.",
     "Single seed = 42 across pipeline"),
]
card_x0 = Inches(0.5)
card_y = Inches(2.50)
card_w = Inches(4.06)
card_h = Inches(4.20)
for i, (h, body, foot, stat) in enumerate(cards):
    x = card_x0 + Inches(i * 4.18)
    add_rect(s, x, card_y, card_w, card_h, WHITE, line=BORDER)
    add_rect(s, x, card_y, Inches(0.06), card_h, PURPLE)
    # Heading
    add_text(s, x + Inches(0.22), card_y + Inches(0.20),
             card_w - Inches(0.4), Inches(0.5),
             h, size=17, bold=True, color=NEAR_BLACK)
    # Body
    add_text(s, x + Inches(0.22), card_y + Inches(0.90),
             card_w - Inches(0.4), Inches(1.5),
             body, size=14, color=NEAR_BLACK_2)
    # Stat callout (mid-card)
    add_rect(s, x + Inches(0.22), card_y + Inches(2.30),
             card_w - Inches(0.44), Inches(0.55),
             PURPLE_TINT)
    add_text(s, x + Inches(0.32), card_y + Inches(2.40),
             card_w - Inches(0.64), Inches(0.4),
             stat, size=13, color=PURPLE_DARK, bold=True)
    # Footer line (effect)
    add_text(s, x + Inches(0.22), card_y + Inches(3.10),
             card_w - Inches(0.4), Inches(1.0),
             foot, size=12.5, color=NEAR_BLACK_2, italic=True)

add_footer(s, 3)


# ── 04. DATASET — 7 BLOCKS ────────────────────────────────────────────────
s = new_slide()
page_bg(s)
add_left_stripe(s)
add_title_bar(s, "Dataset · 329,044 TMDb films, 7 modality blocks", eyebrow="Data")

hdrs = ["#", "Block", "Input dim", "Encoding", "Projected dim"]
rows = [
    ["1", "numerical", "6", "log-scaled popularity, vote_count, runtime, ratings", "16"],
    ["2", "genre", "22", "multi-label one-hot over 21 TMDb genres + has_genre", "16"],
    ["3", "language", "31", "one-hot top-30 original_language + lang_other", "16"],
    ["4", "decade", "2", "normalised (year − 1900)/130 + has_release_date", "4"],
    ["5", "awards", "6", "log1p of prior Oscar / Palme nominations & wins", "16"],
    ["6", "text", "384", "MiniLM-L12-v2 overview embedding (L2-normalised)", "64"],
    ["7", "director", "113", "PCA-64 of bio + has_bio + 31 lang + 16 country + flag", "32"],
    ["", "TOTAL", "564", "", "164"],
]
col_w = [Inches(0.5), Inches(1.65), Inches(1.05), Inches(7.40), Inches(1.40)]
col_x = [Inches(0.5)]
for w in col_w[:-1]:
    col_x.append(col_x[-1] + w)
y = Inches(1.60)
for x, w, text in zip(col_x, col_w, hdrs):
    add_rect(s, x, y, w, Inches(0.50), PURPLE)
    add_text(s, x + Inches(0.08), y + Inches(0.13), w, Inches(0.3),
             text, size=13, color=WHITE, bold=True)
y = Inches(2.10)
for ri, row in enumerate(rows):
    bg = CARD_BG if ri % 2 == 0 else WHITE
    is_total = row[1] == "TOTAL"
    for x, w, text in zip(col_x, col_w, row):
        add_rect(s, x, y, w, Inches(0.46),
                 PURPLE_TINT if is_total else bg, line=BORDER)
        add_text(s, x + Inches(0.08), y + Inches(0.12), w, Inches(0.3),
                 text, size=13,
                 color=PURPLE_DARK if is_total else NEAR_BLACK,
                 bold=is_total)
    y += Inches(0.46)

# 4 KPI chips under the table
chips = [
    ("MD5 (canonical)", "e99cee84…"),
    ("seed", "42"),
    ("text encoder", "MiniLM-L12-v2"),
    ("bio coverage", "3.18 % rows"),
]
y = Inches(6.05)
for i, (label, val) in enumerate(chips):
    add_chip(s, Inches(0.5 + i * 3.16), y, Inches(3.02), Inches(0.85),
             label, val, accent=PURPLE)

add_text(s, Inches(0.5), Inches(6.95), Inches(12), Inches(0.25),
         "Ground-truth axes (evaluation only): primary_genre  ·  decade_bin  ·  lang_top10",
         size=11, color=NEAR_BLACK_2, italic=True)

add_footer(s, 4)


# ── 05. PIPELINE OVERVIEW ─────────────────────────────────────────────────
s = new_slide()
page_bg(s)
add_left_stripe(s)
add_title_bar(s, "End-to-end pipeline", eyebrow="System overview")

steps = [
    ("EDA v2",
     "raw TMDb +\ndirector + awards",
     "→ (329k × 564) npz",
     "Notebook"),
    ("Training",
     "MultiModalBackbone\n+ {AE, VAE, DEC,\nContrastive} heads",
     "→ artifacts/models/",
     "PyTorch"),
    ("Index build",
     "encode all 329k →\nL2-normalise →\nMBKMeans k=21",
     "→ embeddings.npy 42 MB",
     "build_index.py"),
    ("API",
     "FastAPI lifespan\nmmap embeddings\n8 endpoints",
     "→ < 5 ms cosine query",
     "uvicorn :8000"),
    ("Frontend",
     "5 routes\nBackboneSwitcher\ncosine heatmap",
     "→ live demo",
     "Next.js 16 :3000"),
]
sw = Inches(2.45)
sx0 = Inches(0.50)
sy = Inches(1.80)
sh = Inches(3.95)
for i, (head, body, output, foot) in enumerate(steps):
    x = sx0 + Inches(i * 2.55)
    add_rect(s, x, sy, sw, sh, WHITE, line=BORDER)
    add_rect(s, x, sy, sw, Inches(0.55), PURPLE)
    add_text(s, x + Inches(0.18), sy + Inches(0.13), sw, Inches(0.45),
             f"{i+1}. {head}", size=14, color=WHITE, bold=True)
    add_text(s, x + Inches(0.18), sy + Inches(0.80), sw - Inches(0.36),
             Inches(1.7),
             body, size=12.5, color=NEAR_BLACK_2)
    # Output row in tint
    add_rect(s, x + Inches(0.18), sy + Inches(2.55),
             sw - Inches(0.36), Inches(0.55), PURPLE_TINT)
    add_text(s, x + Inches(0.28), sy + Inches(2.65),
             sw - Inches(0.56), Inches(0.4),
             output, size=11, color=PURPLE_DARK, bold=True)
    add_text(s, x + Inches(0.18), sy + Inches(3.30), sw - Inches(0.36),
             Inches(0.4),
             foot, size=11.5, color=PURPLE, italic=True, bold=True)
    if i < len(steps) - 1:
        ax = x + sw + Inches(0.02)
        arr = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, ax,
                                 sy + Inches(1.85), Inches(0.16),
                                 Inches(0.26))
        arr.fill.solid(); arr.fill.fore_color.rgb = PURPLE
        arr.line.fill.background(); arr.shadow.inherit = False

# Bottom stat strip
add_text(s, Inches(0.5), Inches(6.05), Inches(12.5), Inches(0.4),
         "Every step is deterministic at seed = 42  ·  Full reproducibility via "
         "107-test pytest suite (1535 LOC)  ·  All artifacts under artifacts/",
         size=13, color=NEAR_BLACK_2, italic=True)

# Mini stat strip
mini = [
    ("FILMS", "329,044"),
    ("FEATURES", "564 → 32"),
    ("BACKBONES", "3 trained"),
    ("CLUSTERS", "k = 21"),
    ("TESTS", "107 pass"),
]
yy = Inches(6.50)
for i, (lbl, val) in enumerate(mini):
    x = Inches(0.5 + i * 2.56)
    add_text(s, x, yy, Inches(2.5), Inches(0.25),
             lbl, size=10, color=PURPLE, bold=True)
    add_text(s, x, yy + Inches(0.25), Inches(2.5), Inches(0.30),
             val, size=15, color=NEAR_BLACK, bold=True)

add_footer(s, 5)


# ── 06. MULTI-MODAL BACKBONE ──────────────────────────────────────────────
s = new_slide()
page_bg(s)
add_left_stripe(s)
add_title_bar(s, "Multi-modal backbone — per-block projection",
              eyebrow="Architecture")

add_text(s, Inches(0.5), Inches(1.55), Inches(7), Inches(0.5),
         "Each block gets its own linear projection",
         size=17, color=NEAR_BLACK_2, bold=True)

block_lines = [
    "numerical[6]   → Linear(6→16)   → ReLU → Dropout 0.10",
    "genre[22]      → Linear(22→16)  → ReLU → Dropout 0.10",
    "language[31]   → Linear(31→16)  → ReLU → Dropout 0.10",
    "decade[2]      → Linear(2→4)    → ReLU → Dropout 0.10",
    "awards[6]      → Linear(6→16)   → ReLU → Dropout 0.10",
    "text[384]      → Linear(384→64) → ReLU → Dropout 0.20",
    "director[113]  → Linear(113→32) → ReLU → Dropout 0.20",
]
add_text(s, Inches(0.5), Inches(2.20), Inches(7), Inches(2.7),
         "\n".join(block_lines),
         size=13, color=NEAR_BLACK, font="Consolas")

# Trunk equation in a tinted bar
add_rect(s, Inches(0.5), Inches(4.95), Inches(7), Inches(0.65), PURPLE_TINT)
add_text(s, Inches(0.65), Inches(5.08), Inches(6.8), Inches(0.4),
         "Concat (164-d) → Linear(164→128) → ReLU → Linear(128→z)",
         size=13.5, color=PURPLE_DARK, bold=True, font="Consolas")

add_text(s, Inches(0.5), Inches(5.80), Inches(7), Inches(0.4),
         "L2-normalised at inference  →  cosine = dot product",
         size=14, color=NEAR_BLACK_2, italic=True)
add_text(s, Inches(0.5), Inches(6.30), Inches(7), Inches(0.4),
         "< 500 k parameters (test-pinned)   ·   z ∈ {32, 64, 128}",
         size=12, color=SLATE)
add_text(s, Inches(0.5), Inches(6.65), Inches(7), Inches(0.4),
         "Symmetric decoder mirrors encoder per-block.",
         size=12, color=SLATE)

# Right: 3 backbone variant cards (uniform 0.08-in stripes)
boxes = [
    ("ae_z32", "32-d", "DEMO BACKBONE", "42 MB index  ·  best gNMI", GREEN),
    ("ae_z64", "64-d", "MVP carry-over", "84 MB index  ·  highest geo_NMI", PURPLE),
    ("ae_z128", "128-d", "over-parameterised", "168 MB index  ·  near-dead dim", ORANGE),
]
bx = Inches(8.0)
for i, (name, dim, label, size_, col) in enumerate(boxes):
    y = Inches(1.65 + i * 1.7)
    add_rect(s, bx, y, Inches(4.85), Inches(1.50), WHITE, line=BORDER)
    add_rect(s, bx, y, Inches(0.08), Inches(1.50), col)
    add_text(s, bx + Inches(0.22), y + Inches(0.12), Inches(4.6), Inches(0.45),
             name, size=18, color=NEAR_BLACK, bold=True, font="Consolas")
    add_text(s, bx + Inches(0.22), y + Inches(0.55), Inches(4.6), Inches(0.4),
             dim, size=12, color=SLATE)
    add_text(s, bx + Inches(2.4), y + Inches(0.13), Inches(2.35), Inches(0.4),
             label, size=11, color=col, bold=True, align="right")
    add_text(s, bx + Inches(0.22), y + Inches(0.95), Inches(4.6), Inches(0.4),
             size_, size=11.5, color=SLATE)

add_footer(s, 6)


# ── 07. LOSS FUNCTIONS ────────────────────────────────────────────────────
s = new_slide()
page_bg(s)
add_left_stripe(s)
add_title_bar(s, "Loss functions", eyebrow="Method · objectives")

losses = [
    ("W2 — variance-balanced block weights",
     "w_b = clip(1 / Σ_j Var(X[:,j]), 0.1, 10)",
     "Each modality block contributes proportionally — "
     "stops 384-d text from drowning out 2-d decade."),
    ("G2 — masked director loss",
     "loss_bio counts only on has_director_bio = 1",
     "Only 3.18 % of films have a bio. Without masking, "
     "the other 97 % would teach the model to predict zeros."),
    ("DEC — clustering refinement loss",
     "L = KL(P‖Q) + 0.1 · L_recon",
     "Pulls each film toward its cluster centre while "
     "keeping reconstruction honest (KL on soft assignments)."),
    ("InfoNCE — contrastive pretext",
     "two views via per-row block mask, τ = 0.1",
     "Two corrupted copies of the same film must look alike. "
     "Masking out genre breaks the target (see ND-1)."),
]
gx0 = Inches(0.5); gy0 = Inches(1.55); gw = Inches(6.16); gh = Inches(2.05)
for i, (head, eq, body) in enumerate(losses):
    col = i % 2; row = i // 2
    x = gx0 + Inches(col * 6.33)
    y = gy0 + Inches(row * 2.15)
    add_rect(s, x, y, gw, gh, WHITE, line=BORDER)
    add_rect(s, x, y, Inches(0.08), gh, PURPLE)
    add_text(s, x + Inches(0.22), y + Inches(0.14),
             gw - Inches(0.4), Inches(0.4),
             head, size=15, bold=True, color=NEAR_BLACK)
    add_rect(s, x + Inches(0.22), y + Inches(0.65),
             gw - Inches(0.44), Inches(0.40), PURPLE_TINT)
    add_text(s, x + Inches(0.32), y + Inches(0.72),
             gw - Inches(0.64), Inches(0.3),
             eq, size=12, color=PURPLE_DARK, font="Consolas")
    add_text(s, x + Inches(0.22), y + Inches(1.15),
             gw - Inches(0.4), Inches(0.9),
             body, size=12, color=NEAR_BLACK_2)

# Training protocol — pulled up to clear footer
add_rect(s, Inches(0.5), Inches(6.05), Inches(12.5), Inches(0.9),
         PURPLE_TINT)
add_text(s, Inches(0.7), Inches(6.18), Inches(12.1), Inches(0.35),
         "TRAINING PROTOCOL",
         size=11, color=PURPLE, bold=True)
add_text(s, Inches(0.7), Inches(6.50), Inches(12.1), Inches(0.4),
         "Adam · weight_decay 1e-5 · grad-clip 1.0 · early-stop patience 10 "
         "· seed 42 · 90/10 split · W&B logging",
         size=13, color=NEAR_BLACK)

add_footer(s, 7)


# ── 08. EVALUATION METHODOLOGY ────────────────────────────────────────────
s = new_slide()
page_bg(s)
add_left_stripe(s)
add_title_bar(s, "Evaluation — two metric families",
              eyebrow="Methodology")

# Left card: clustering
cx = Inches(0.5); cy = Inches(1.55); cw = Inches(6.05); ch = Inches(4.6)
add_rect(s, cx, cy, cw, ch, WHITE, line=BORDER)
add_rect(s, cx, cy, cw, Inches(0.55), PURPLE)
add_text(s, cx + Inches(0.22), cy + Inches(0.13), cw, Inches(0.4),
         "Clustering family — structure exploration",
         size=14, color=WHITE, bold=True)
add_bullets(s, cx + Inches(0.22), cy + Inches(0.78),
            cw - Inches(0.44), Inches(3.5), [
    "Three orthogonal axes: primary_genre · decade · lang_top10.",
    "Per-axis NMI, ARI, AMI (Strehl & Ghosh 2002; Vinh 2010).",
    "Composite geo_NMI = (gNMI · dNMI · lNMI)^(1/3).",
    "Per-axis-k sweep (genre=21, decade=12, lang=11).",
    "Multilabel macro-NMI over 22 genre columns.",
], size=12.5, line_gap=Inches(0.50))
# Small data-mini-table at bottom of clustering card
yy = cy + ch - Inches(0.65)
add_rect(s, cx + Inches(0.22), yy, cw - Inches(0.44), Inches(0.50),
         PURPLE_TINT)
add_text(s, cx + Inches(0.32), yy + Inches(0.10),
         cw - Inches(0.64), Inches(0.35),
         "axis cardinality:  genre = 21  ·  decade = 12  ·  lang = 11",
         size=11.5, color=PURPLE_DARK, bold=True, font="Consolas")

# Right card: retrieval
cx2 = Inches(6.80)
add_rect(s, cx2, cy, cw, ch, WHITE, line=BORDER)
add_rect(s, cx2, cy, cw, Inches(0.55), ORANGE)
add_text(s, cx2 + Inches(0.22), cy + Inches(0.13), cw, Inches(0.4),
         "Retrieval family — deployment selection",
         size=14, color=WHITE, bold=True)
add_bullets(s, cx2 + Inches(0.22), cy + Inches(0.78),
            cw - Inches(0.44), Inches(3.5), [
    "genre@k: fraction of top-k whose primary_genre matches.",
    "316 popular queries × top-5.",
    "Eyeball top-5 on 10 canonical films.",
    "Angular spread: random_pair_cos_{mean, std}.",
    "Latent health: dim_std per latent dimension.",
], size=12.5, line_gap=Inches(0.50))
# Mini-table at bottom
yy = cy + ch - Inches(0.65)
add_rect(s, cx2 + Inches(0.22), yy, cw - Inches(0.44), Inches(0.50),
         ORANGE_TINT)
add_text(s, cx2 + Inches(0.32), yy + Inches(0.10),
         cw - Inches(0.64), Inches(0.35),
         "deploy gate:  genre@5 > 0.70  ·  dim_std_min > 0.05  ·  no cluster collapse",
         size=11.5, color=ORANGE, bold=True, font="Consolas")

# Punchline
add_rect(s, Inches(0.5), Inches(6.30), Inches(12.5), Inches(0.65),
         PURPLE_TINT)
add_text(s, Inches(0.7), Inches(6.43), Inches(12.1), Inches(0.4),
         "The two-family split is the protocol that exposes the F1 finding "
         "(NMI ≠ retrieval — see slide 15).",
         size=13, color=PURPLE_DARK, italic=True, bold=True)

add_footer(s, 8)


# ── 09. HEADLINE — +205% ──────────────────────────────────────────────────
s = new_slide()
page_bg(s)
add_left_stripe(s)
add_title_bar(s, "Headline empirical result", eyebrow="Results · H2 PASS")

# Big number callout
add_rect(s, Inches(0.5), Inches(1.55), Inches(7.5), Inches(5.0),
         WHITE, line=BORDER)
add_rect(s, Inches(0.5), Inches(1.55), Inches(0.08), Inches(5.0), ORANGE)
add_text(s, Inches(0.75), Inches(1.75), Inches(7), Inches(0.5),
         "BEST DEEP vs BEST NON-DEEP BASELINE",
         size=12, color=ORANGE, bold=True)
add_text(s, Inches(0.75), Inches(2.30), Inches(7), Inches(2.5),
         "+205%", size=160, color=ORANGE, bold=True)
add_text(s, Inches(0.75), Inches(4.95), Inches(7), Inches(0.6),
         "relative gain on genre NMI",
         size=22, color=NEAR_BLACK_2)
add_text(s, Inches(0.75), Inches(5.55), Inches(7), Inches(0.5),
         "0.332  (dec_z64_k21)   vs   0.109  (kmeans_raw_k21)",
         size=15, color=NEAR_BLACK, font="Consolas")
add_text(s, Inches(0.75), Inches(6.00), Inches(7), Inches(0.4),
         "Pre-registered H2 success criterion: > 10 % over non-deep baseline.",
         size=11, color=SLATE, italic=True)

# Right: supporting numbers
right = Inches(8.4)
add_text(s, right, Inches(1.55), Inches(4.5), Inches(0.6),
         "Supporting evidence", size=15, color=NEAR_BLACK, bold=True)
supp = [
    ("+287%", "genre ARI vs kmeans_raw  (0.244 vs 0.063)"),
    ("+292%", "lang NMI vs pca_kmeans  (0.294 vs 0.075)"),
    ("+178%", "lang NMI · multi-modal vs vanilla concat-AE"),
    ("+99%",  "genre NMI · W2 vs W1 uniform ablation"),
]
y = Inches(2.15)
for big, label in supp:
    add_rect(s, right, y, Inches(4.5), Inches(0.85), CARD_BG, line=BORDER)
    add_rect(s, right, y, Inches(0.06), Inches(0.85), GREEN)
    add_text(s, right + Inches(0.18), y + Inches(0.10),
             Inches(1.4), Inches(0.65),
             big, size=24, color=GREEN, bold=True)
    add_text(s, right + Inches(1.65), y + Inches(0.25),
             Inches(2.80), Inches(0.6),
             label, size=11.5, color=NEAR_BLACK_2)
    y += Inches(1.05)

# Hypothesis pass-bar (well above footer)
add_rect(s, Inches(0.5), Inches(6.65), Inches(12.5), Inches(0.4),
         GREEN_TINT)
add_text(s, Inches(0.7), Inches(6.71), Inches(12), Inches(0.3),
         "H1 PASS (DEC > AE +1.2 % NMI)  ·  H2 PASS (this slide)  "
         "·  H3 PASS (0.332 ≫ 0.15 absolute floor)",
         size=12, color=GREEN, bold=True)

add_footer(s, 9)


# ── 10. THREE-TIER RESULTS TABLE ──────────────────────────────────────────
s = new_slide()
page_bg(s)
add_left_stripe(s)
add_title_bar(s, "Three-tier comparison @ z = 64, k = 21",
              eyebrow="Results · Phase 0 MVP")

cols = ["Tier", "Model", "genre NMI", "genre ARI", "decade NMI",
        "decade ARI", "lang NMI", "lang ARI", "val_loss", "epochs"]
data = [
    ("Non-deep", "kmeans_raw_k21",  "0.109", "0.063", "0.233", "0.093", "0.075", "0.026", "—",        "—",   False),
    ("Non-deep", "pca_kmeans_k21",  "0.084", "0.061", "0.224", "0.085", "0.094", "0.042", "—",        "—",   False),
    ("Simple",   "vanilla_ae_z64",  "0.287", "0.247", "0.369", "0.175", "0.095", "0.030", "0.0126",   "58",  False),
    ("W1 abl.",  "ae_z64_w1",       "0.165", "0.094", "0.367", "0.176", "0.070", "0.026", "0.0453",   "37",  False),
    ("Multi-modal", "ae_z64",       "0.328", "0.229", "0.341", "0.211", "0.264", "0.090", "0.0208",   "69",  False),
    ("BEST",     "dec_z64_k21",     "0.332", "0.244", "0.342", "0.210", "0.294", "0.090", "0.127 †",  "21",  True),
]
col_w = [Inches(1.05), Inches(1.65), Inches(1.10), Inches(1.10),
         Inches(1.15), Inches(1.15), Inches(1.00), Inches(1.00),
         Inches(1.10), Inches(0.70)]
col_x = [Inches(0.5)]
for w in col_w[:-1]:
    col_x.append(col_x[-1] + w)
y = Inches(1.65)
for x, w, c in zip(col_x, col_w, cols):
    add_rect(s, x, y, w, Inches(0.50), PURPLE)
    add_text(s, x + Inches(0.06), y + Inches(0.12), w, Inches(0.3),
             c, size=11.5, color=WHITE, bold=True)
y = Inches(2.15)
for ri, row in enumerate(data):
    is_win = row[-1]
    cells = list(row[:-1])
    for x, w, c in zip(col_x, col_w, cells):
        bg = PURPLE_TINT if is_win else (CARD_BG if ri % 2 == 0 else WHITE)
        add_rect(s, x, y, w, Inches(0.50), bg, line=BORDER)
        col = PURPLE_DARK if is_win else NEAR_BLACK
        add_text(s, x + Inches(0.06), y + Inches(0.13), w, Inches(0.3),
                 c, size=12, color=col, bold=is_win)
    y += Inches(0.50)

add_text(s, Inches(0.5), Inches(5.40), Inches(12.5), Inches(0.4),
         "† DEC val_loss combines KL + recon — not comparable to AE pure-recon.",
         size=11, color=SLATE, italic=True)

# Three takeaway cards (instead of paragraph text — better space use)
takeaways = [
    ("DEC wins NMI",       "on 2 of 3 axes (genre, lang)", GREEN),
    ("Vanilla wins decade", "0.369 — easy axis, KMeans free", PURPLE),
    ("MM wins decade ARI", "0.211 — Pareto across architectures", AMBER),
]
y = Inches(5.90)
for i, (head, body, col) in enumerate(takeaways):
    x = Inches(0.5 + i * 4.18)
    add_rect(s, x, y, Inches(4.06), Inches(0.95), WHITE, line=BORDER)
    add_rect(s, x, y, Inches(0.06), Inches(0.95), col)
    add_text(s, x + Inches(0.20), y + Inches(0.13),
             Inches(3.7), Inches(0.4),
             head, size=14, color=col, bold=True)
    add_text(s, x + Inches(0.20), y + Inches(0.50),
             Inches(3.7), Inches(0.4),
             body, size=12, color=NEAR_BLACK_2)
add_text(s, Inches(0.5), Inches(6.95), Inches(12.5), Inches(0.3),
         "DEC's contribution is compactness (ARI +6.6 %, lang NMI +11.4 %), not new structural information.",
         size=11, color=PURPLE_DARK, italic=True, bold=True)

add_footer(s, 10)


# ── 11. HERO FINDINGS ─────────────────────────────────────────────────────
s = new_slide()
page_bg(s)
add_left_stripe(s)
add_title_bar(s, "Nine hero findings", eyebrow="Results · cross-cuts")

findings = [
    ("1. Language wins big",
     "Modality projection lifts lang NMI +178 % vs vanilla concat-AE.",
     "→ Finding 1"),
    ("2. W2 is critical",
     "Uniform-weight W1 collapses gNMI 50 %, lang NMI 73 %.",
     "→ Finding 2"),
    ("3. Recon ≠ clustering",
     "Lowest val_loss (vanilla) ≠ best gNMI (multi-modal).",
     "→ Finding 3"),
    ("4. Decade is easy",
     "All architectures reach decade NMI ≈ 0.34–0.37.",
     "→ Finding 4"),
    ("5. Pareto across axes",
     "No architecture wins all six metrics — principled trade-off.",
     "→ Finding 5"),
    ("6. Deep > non-deep 3–5×",
     "+205 % vs kmeans_raw_k21 on genre NMI (the headline).",
     "→ Finding 6"),
    ("7. DEC sharpens, not discovers",
     "ARI +6.6 % > NMI +1.2 % — compactness gain only.",
     "→ Finding 7"),
    ("8. Topology evolves",
     "UMAP: blobs → islands → tight islands (slide 12).",
     "→ Finding 8"),
    ("9. Missing-data manifold",
     "Films without release_date form a coherent sub-region.",
     "→ Finding 9"),
]
gx0 = Inches(0.5); gy0 = Inches(1.55); gw = Inches(4.13); gh = Inches(1.78)
gap_x = Inches(0.06); gap_y = Inches(0.08)
for i, (head, body, pointer) in enumerate(findings):
    col = i % 3; row = i // 3
    x = gx0 + Inches(col * 4.18) + (gap_x if col > 0 else Emu(0))
    y = gy0 + Inches(row * 1.83) + (gap_y if row > 0 else Emu(0))
    add_rect(s, x, y, gw, gh, WHITE, line=BORDER)
    add_rect(s, x, y, Inches(0.06), gh, PURPLE)
    add_text(s, x + Inches(0.18), y + Inches(0.12),
             gw - Inches(0.3), Inches(0.4),
             head, size=14, color=NEAR_BLACK, bold=True)
    add_text(s, x + Inches(0.18), y + Inches(0.55),
             gw - Inches(0.3), Inches(0.9),
             body, size=12, color=NEAR_BLACK_2)
    add_text(s, x + Inches(0.18), y + Inches(1.42),
             gw - Inches(0.3), Inches(0.30),
             pointer, size=10.5, color=PURPLE, bold=True, italic=True)

add_footer(s, 11)


# ── 12. UMAP TOPOLOGY ─────────────────────────────────────────────────────
s = new_slide()
page_bg(s)
add_left_stripe(s)
add_title_bar(s, "Latent topology evolves: blobs → islands → tight islands",
              eyebrow="Finding 8 · hero figure")

# Image enlarged + lifted
add_picture_safe(s, FIG_ART / "umap/umap_comparison_genre.png",
                 Inches(0.5), Inches(1.50), w=Inches(8.9))

# Right side caption + stage cards
right = Inches(9.55); rw = Inches(3.40)
add_text(s, right, Inches(1.55), rw, Inches(0.4),
         "UMAP · 15k subsample · cosine metric",
         size=11.5, color=NEAR_BLACK_2, italic=True)

stages = [
    ("vanilla concat-AE",
     "2 mega-blobs dominated by\nUnknown-genre mass",
     RED),
    ("multi-modal AE (W2)",
     "dozens of small\ngenre-coherent islands",
     ORANGE),
    ("DEC (k = 21)",
     "even more atomised,\ntighter islands",
     GREEN),
]
y = Inches(2.10)
for name, body, col in stages:
    add_rect(s, right, y, rw, Inches(1.35), WHITE, line=BORDER)
    add_rect(s, right, y, Inches(0.08), Inches(1.35), col)
    add_text(s, right + Inches(0.22), y + Inches(0.12),
             rw - Inches(0.4), Inches(0.4),
             name, size=13, bold=True, color=NEAR_BLACK)
    add_text(s, right + Inches(0.22), y + Inches(0.55),
             rw - Inches(0.4), Inches(0.8),
             body, size=11.5, color=NEAR_BLACK_2)
    y += Inches(1.45)

# Bottom takeaway bar
add_rect(s, Inches(0.5), Inches(6.65), Inches(12.5), Inches(0.45),
         PURPLE_TINT)
add_text(s, Inches(0.7), Inches(6.72), Inches(12), Inches(0.35),
         "Visual signature of representation learning — the empirical "
         "fingerprint of modality-specific projection + KL sharpening.",
         size=13, color=PURPLE_DARK, italic=True)

add_footer(s, 12)


# ── 13. ABLATIONS — W2 vs W1 + MISSING-DATA ───────────────────────────────
s = new_slide()
page_bg(s)
add_left_stripe(s)
add_title_bar(s, "Ablations — inverse-variance weighting + missing-data",
              eyebrow="Findings 2 & 9")

# Left side: W2 vs W1 table
add_rect(s, Inches(0.5), Inches(1.55), Inches(6.0), Inches(5.40),
         WHITE, line=BORDER)
add_rect(s, Inches(0.5), Inches(1.55), Inches(6.0), Inches(0.50), PURPLE)
add_text(s, Inches(0.65), Inches(1.66), Inches(6), Inches(0.4),
         "W2 inverse-variance vs W1 uniform",
         size=14, color=WHITE, bold=True)
hdr = ["Metric", "W2", "W1", "Δ rel."]
rows_w = [
    ("genre NMI",            "0.328", "0.165", "−50 %"),
    ("lang NMI",             "0.264", "0.070", "−73 %"),
    ("decade NMI",           "0.341", "0.367", "+8 %"),
    ("epochs early-stop",    "69",    "37",    "—"),
]
y = Inches(2.30)
cw = [Inches(2.0), Inches(1.15), Inches(1.15), Inches(1.55)]
cx = [Inches(0.65)]
for w in cw[:-1]:
    cx.append(cx[-1] + w)
for x, w, txt in zip(cx, cw, hdr):
    add_rect(s, x, y, w, Inches(0.40), PURPLE_TINT, line=BORDER)
    add_text(s, x + Inches(0.08), y + Inches(0.09), w, Inches(0.3),
             txt, size=12.5, color=PURPLE_DARK, bold=True)
y += Inches(0.40)
for r in rows_w:
    for x, w, txt in zip(cx, cw, r):
        add_rect(s, x, y, w, Inches(0.42), CARD_BG, line=BORDER)
        col = RED if txt.startswith("−") else (GREEN if txt.startswith("+") else NEAR_BLACK)
        add_text(s, x + Inches(0.08), y + Inches(0.09), w, Inches(0.3),
                 txt, size=12.5, color=col,
                 bold=txt.startswith(("+", "−")))
    y += Inches(0.42)

# Conclusion below table — inside the same card
add_text(s, Inches(0.65), Inches(4.80), Inches(5.7), Inches(1.0),
         "Asymmetric collapse. Decade (2-d) survives uniform weighting "
         "because StandardScaler gave it per-feature var ≈ 1. Text (384) "
         "and language (31) lose all gradient signal.",
         size=12, color=NEAR_BLACK_2)
add_text(s, Inches(0.65), Inches(6.10), Inches(5.7), Inches(0.6),
         "Model-health diagnostic: W1 patience exhausted at epoch 37.",
         size=12, color=PURPLE_DARK, bold=True, italic=True)

# Right side: missing-data manifold figure
add_text(s, Inches(6.85), Inches(1.65), Inches(6.0), Inches(0.4),
         "Finding 9 · missing-release-date manifold",
         size=14, color=PURPLE_DARK, bold=True)
add_picture_safe(s, FIG_ART / "umap/umap_dec_z64_k21_decade.png",
                 Inches(6.85), Inches(2.10), w=Inches(6.2))
add_rect(s, Inches(6.85), Inches(6.55), Inches(6.2), Inches(0.40),
         RGBColor(0xFE, 0xE4, 0xE4))
add_text(s, Inches(7.0), Inches(6.62), Inches(6.0), Inches(0.3),
         "Red = decade_bin 0 (≈ 7.4 % of films, no release date).",
         size=11.5, color=RED, italic=True, bold=True)

add_footer(s, 13)


# ── 14. NEGATIVE RESULTS ──────────────────────────────────────────────────
s = new_slide()
page_bg(s)
add_left_stripe(s)
add_title_bar(s, "Negative results — own them, learn from them",
              eyebrow="ND-1, ND-2, ND-3")

nds = [
    ("ND-1",
     "Contrastive pretext underperformed",
     "Best Phase 1 gNMI = 0.216 vs MVP ae_z64 = 0.328  (−34 %).",
     "Root cause: modality-dropout includes genre — InfoNCE trains for "
     "genre-invariance, the opposite of the clustering target."),
    ("ND-2",
     "AE→DEC fine-tune inherited the poison",
     "geo_NMI ≤ 0.181 vs MVP DEC = 0.323  (−44 to −67 %).",
     "DEC − KMeans-on-AE-latent delta ≤ 0.001 — DEC was fine; the "
     "contrastive encoder was already broken."),
    ("ND-3",
     "VAE z = 64 likely posterior collapse",
     "Early-stop epoch 12, geo_NMI = 0.127 — below every baseline.",
     "Per-epoch recon vs KL split was not logged — hypothesis strong "
     "but not falsified. Top future-work priority."),
]
y0 = Inches(1.55)
for i, (tag, head, ev, cause) in enumerate(nds):
    y = y0 + Inches(i * 1.55)
    add_rect(s, Inches(0.5), y, Inches(12.5), Inches(1.40), WHITE, line=BORDER)
    add_rect(s, Inches(0.5), y, Inches(0.08), Inches(1.40), RED)
    add_text(s, Inches(0.7), y + Inches(0.12), Inches(1.0), Inches(0.40),
             tag, size=22, color=RED, bold=True, font="Consolas")
    add_text(s, Inches(1.8), y + Inches(0.10), Inches(11), Inches(0.4),
             head, size=15, color=NEAR_BLACK, bold=True)
    add_text(s, Inches(1.8), y + Inches(0.50), Inches(11), Inches(0.35),
             ev, size=12, color=NEAR_BLACK_2, font="Consolas")
    add_text(s, Inches(1.8), y + Inches(0.92), Inches(11), Inches(0.4),
             cause, size=11.5, color=SLATE, italic=True)

# Bottom lessons strip
add_rect(s, Inches(0.5), Inches(6.30), Inches(12.5), Inches(0.65), PURPLE_TINT)
add_text(s, Inches(0.7), Inches(6.43), Inches(12.1), Inches(0.4),
         "LESSONS  ·  augmentations must preserve the target  ·  always log "
         "recon vs KL split  ·  re-audit selection metric when deliverable shifts",
         size=12, color=PURPLE_DARK, bold=True)

add_footer(s, 14)


# ── 15. F1 — NMI ≠ RETRIEVAL ──────────────────────────────────────────────
s = new_slide()
page_bg(s)
add_left_stripe(s)
add_title_bar(s, "F1 — NMI does NOT predict cosine retrieval quality",
              eyebrow="Methodological finding 1")

# Left big number
add_rect(s, Inches(0.5), Inches(1.55), Inches(5.6), Inches(5.30),
         WHITE, line=BORDER)
add_rect(s, Inches(0.5), Inches(1.55), Inches(0.08), Inches(5.30), ORANGE)
add_text(s, Inches(0.75), Inches(1.75), Inches(5.3), Inches(0.5),
         "DEC TOP-5 COSINES · INCEPTION", size=11,
         color=ORANGE, bold=True)
add_text(s, Inches(0.75), Inches(2.25), Inches(5.3), Inches(2.5),
         "≈ 1.000", size=88, color=ORANGE, bold=True)
add_text(s, Inches(0.75), Inches(4.30), Inches(5.3), Inches(0.5),
         "0.99992  0.99989  0.99986  0.99986  0.99986",
         size=12, color=NEAR_BLACK, font="Consolas")
add_text(s, Inches(0.75), Inches(4.80), Inches(5.3), Inches(0.4),
         "difference < 1e-4  (float32 floor)",
         size=12, color=SLATE, italic=True)
add_rect(s, Inches(0.75), Inches(5.40), Inches(5.1), Inches(1.30),
         RGBColor(0xFE, 0xE4, 0xD7))
add_text(s, Inches(0.95), Inches(5.55), Inches(4.7), Inches(0.5),
         "DEC has the HIGHEST NMI  (0.332)",
         size=14, color=NEAR_BLACK, bold=True)
add_text(s, Inches(0.95), Inches(5.95), Inches(4.7), Inches(0.5),
         "and the WORST retrieval",
         size=14, color=NEAR_BLACK, bold=True)
add_text(s, Inches(0.95), Inches(6.30), Inches(4.7), Inches(0.4),
         "genre@5 = 0.557 (vs 0.723 for ae_z32)",
         size=11.5, color=ORANGE, bold=True)

# Right side: mechanism + retrieval table
right = Inches(6.40)
add_text(s, right, Inches(1.65), Inches(6.5), Inches(0.4),
         "Mechanism — angular collapse",
         size=15, color=NEAR_BLACK, bold=True)
add_text(s, right, Inches(2.10), Inches(6.5), Inches(1.6),
         "DEC's clustering loss pulls every film inside a cluster\n"
         "toward the cluster centre. After enough training,\n"
         "neighbours sit on top of each other — cosine = 1.\n"
         "NMI only sees cluster IDs (still good); retrieval\n"
         "needs spread inside the cluster (collapsed).",
         size=12, color=NEAR_BLACK_2)

# Retrieval verdict table
hdr = ["Backbone", "gNMI", "genre@5", "verdict"]
trows = [
    ("ae_z32",      "0.334", "0.723", "deploy",  GREEN),
    ("ae_z64",      "0.328", "0.715", "MVP",     PURPLE_DARK),
    ("ae_z128",     "0.273", "0.722", "wasteful", AMBER),
    ("dec_z64_k21", "0.332", "0.557", "BROKEN",  RED),
]
cw = [Inches(1.85), Inches(1.05), Inches(1.20), Inches(1.45)]
cx = [right]
for w in cw[:-1]:
    cx.append(cx[-1] + w)
y = Inches(4.20)
for x, w, t in zip(cx, cw, hdr):
    add_rect(s, x, y, w, Inches(0.42), PURPLE)
    add_text(s, x + Inches(0.08), y + Inches(0.10), w, Inches(0.3),
             t, size=12, color=WHITE, bold=True)
y += Inches(0.42)
for ri, r in enumerate(trows):
    color_for = [NEAR_BLACK, NEAR_BLACK, NEAR_BLACK, r[-1]]
    bold_for = [True, False, False, True]
    for x, w, t, col, bld in zip(cx, cw, r[:-1], color_for, bold_for):
        add_rect(s, x, y, w, Inches(0.42),
                 CARD_BG if ri % 2 == 0 else WHITE, line=BORDER)
        add_text(s, x + Inches(0.08), y + Inches(0.10), w, Inches(0.3),
                 t, size=12, color=col, bold=bld)
    y += Inches(0.42)

# Punchline — lifted up for footer clearance
add_rect(s, Inches(6.40), Inches(6.15), Inches(6.60), Inches(0.55),
         PURPLE_TINT)
add_text(s, Inches(6.55), Inches(6.25), Inches(6.4), Inches(0.4),
         "When the deliverable changes, RE-AUDIT the selection metric.",
         size=13, color=PURPLE_DARK, bold=True, italic=True)

add_footer(s, 15)


# ── 16. F1 — EMPIRICAL EVIDENCE (HISTOGRAM) ───────────────────────────────
s = new_slide()
page_bg(s)
add_left_stripe(s)
add_title_bar(s, "F1 evidence — top-5 neighbour cosines (400 queries)",
              eyebrow="Empirical evidence for F1")

# Figure lifted upward
add_picture_safe(s, FIG_FINAL / "cosine_collapse_histogram.png",
                 Inches(0.5), Inches(1.45), w=Inches(12.3))

# Bottom annotation (well above footer)
add_rect(s, Inches(0.5), Inches(6.10), Inches(6.0), Inches(0.85),
         WHITE, line=BORDER)
add_rect(s, Inches(0.5), Inches(6.10), Inches(0.06), Inches(0.85), BRAND_BLUE := PURPLE)
add_text(s, Inches(0.7), Inches(6.20), Inches(5.7), Inches(0.4),
         "ae_z32 — healthy geometry",
         size=14, color=PURPLE_DARK, bold=True)
add_text(s, Inches(0.7), Inches(6.55), Inches(5.7), Inches(0.35),
         "mean 0.993  ·  median 0.999  ·  min 0.906  →  broad spread",
         size=12, color=NEAR_BLACK_2, font="Consolas")

add_rect(s, Inches(7.0), Inches(6.10), Inches(6.0), Inches(0.85),
         WHITE, line=BORDER)
add_rect(s, Inches(7.0), Inches(6.10), Inches(0.06), Inches(0.85), ORANGE)
add_text(s, Inches(7.2), Inches(6.20), Inches(5.7), Inches(0.4),
         "dec_z64_k21 — angular collapse",
         size=14, color=ORANGE, bold=True)
add_text(s, Inches(7.2), Inches(6.55), Inches(5.7), Inches(0.35),
         "mean 1.000  ·  median 1.000  ·  min 0.998  →  saturated",
         size=12, color=NEAR_BLACK_2, font="Consolas")

add_footer(s, 16)


# ── 17. F2 — z = 32 SWEET SPOT ────────────────────────────────────────────
s = new_slide()
page_bg(s)
add_left_stripe(s)
add_title_bar(s, "F2 — z = 32 is the right capacity (U-curve)",
              eyebrow="Methodological finding 2")

# Figure
add_picture_safe(s, FIG_FINAL / "zsweep_ucurve.png",
                 Inches(0.5), Inches(1.55), w=Inches(7.0))

# Right side
right = Inches(7.85); rw = Inches(5.20)
add_text(s, right, Inches(1.65), rw, Inches(0.5),
         "Smaller and bigger both lose — z = 32 wins",
         size=17, color=NEAR_BLACK, bold=True)
# Mini z-sweep summary
mini = [
    ("z = 32", "0.334", "0.723", "0.117", GREEN),
    ("z = 64", "0.328", "0.715", "0.062", PURPLE),
    ("z = 128","0.273", "0.722", "0.025", ORANGE),
]
add_text(s, right, Inches(2.15), rw, Inches(0.3),
         "        gNMI    genre@5   dim_std_min",
         size=10, color=SLATE, font="Consolas")
y = Inches(2.40)
for label, g, gat5, ds, col in mini:
    add_rect(s, right, y, rw, Inches(0.40), CARD_BG, line=BORDER)
    add_rect(s, right, y, Inches(0.06), Inches(0.40), col)
    add_text(s, right + Inches(0.18), y + Inches(0.08), Inches(1.0), Inches(0.3),
             label, size=12, color=col, bold=True, font="Consolas")
    add_text(s, right + Inches(1.30), y + Inches(0.08), Inches(0.9), Inches(0.3),
             g, size=12, color=NEAR_BLACK, font="Consolas",
             bold=(label == "z = 32"))
    add_text(s, right + Inches(2.20), y + Inches(0.08), Inches(1.1), Inches(0.3),
             gat5, size=12, color=NEAR_BLACK, font="Consolas")
    add_text(s, right + Inches(3.30), y + Inches(0.08), Inches(1.5), Inches(0.3),
             ds, size=12, color=NEAR_BLACK, font="Consolas",
             bold=(label == "z = 128"))
    y += Inches(0.42)

# Five signals card
add_rect(s, right, Inches(3.95), rw, Inches(1.85), WHITE, line=BORDER)
add_rect(s, right, Inches(3.95), Inches(0.06), Inches(1.85), GREEN)
add_text(s, right + Inches(0.20), Inches(4.05), rw - Inches(0.3), Inches(0.4),
         "Five signals favour z = 32",
         size=13, color=GREEN, bold=True)
sigs = [
    "gNMI peak  ·  dim_std_min healthy",
    "pair_cos_std broad  ·  val_loss lowest",
    "Occam — smallest, fastest, 42 MB index",
]
add_text(s, right + Inches(0.20), Inches(4.45),
         rw - Inches(0.3), Inches(1.3),
         "\n".join(sigs), size=11.5, color=NEAR_BLACK_2)

# Punchline
add_rect(s, Inches(0.5), Inches(6.20), Inches(12.5), Inches(0.75),
         PURPLE_TINT)
add_text(s, Inches(0.7), Inches(6.30), Inches(12.1), Inches(0.35),
         "Tight latent forces the encoder to spend its capacity on the "
         "information-rich modalities (text, director) and compress the rest.",
         size=12, color=PURPLE_DARK)
add_text(s, Inches(0.7), Inches(6.60), Inches(12.1), Inches(0.3),
         "Decision: demo backbone locked at ae_z32.",
         size=11.5, color=PURPLE_DARK, bold=True, italic=True)

add_footer(s, 17)


# ── 18. F2 — DIM-STD EVIDENCE ─────────────────────────────────────────────
s = new_slide()
page_bg(s)
add_left_stripe(s)
add_title_bar(s, "F2 evidence — z = 128 has near-dead latent dimensions",
              eyebrow="Per-dimension activation spread")

# Figure lifted
add_picture_safe(s, FIG_FINAL / "dim_std_per_backbone.png",
                 Inches(0.5), Inches(1.45), w=Inches(12.3))

# 3 stat chips below
chips_18 = [
    ("z = 32",  "dim_std_min  =  0.117", "healthy",   GREEN),
    ("z = 64",  "dim_std_min  =  0.062", "marginal",  PURPLE),
    ("z = 128", "dim_std_min  =  0.025", "near-dead", ORANGE),
]
y = Inches(5.95)
for i, (label, val, verdict, col) in enumerate(chips_18):
    x = Inches(0.5 + i * 4.18)
    add_rect(s, x, y, Inches(4.06), Inches(0.95), WHITE, line=BORDER)
    add_rect(s, x, y, Inches(0.06), Inches(0.95), col)
    add_text(s, x + Inches(0.20), y + Inches(0.10),
             Inches(2.0), Inches(0.4),
             label, size=14, color=col, bold=True, font="Consolas")
    add_text(s, x + Inches(0.20), y + Inches(0.50),
             Inches(3.7), Inches(0.4),
             val, size=12, color=NEAR_BLACK, font="Consolas")
    add_text(s, x + Inches(2.7), y + Inches(0.13),
             Inches(1.3), Inches(0.4),
             verdict, size=11, color=col, bold=True, align="right")

add_footer(s, 18)


# ── 19. ROUND 2 TABLE ─────────────────────────────────────────────────────
s = new_slide()
page_bg(s)
add_left_stripe(s)
add_title_bar(s, "Round 2 · AE z-sweep (final selection)",
              eyebrow="Results · Round 2")

cols = ["z", "gNMI", "decade NMI", "lang NMI", "geo NMI",
        "genre@5", "dim_std_min", "val_loss", "epochs"]
data = [
    ("32",  "0.334", "0.295", "0.216", "0.277", "0.723", "0.117", "0.0204", "100", True),
    ("64",  "0.328", "0.341", "0.264", "0.309", "0.715", "0.062", "0.0208", "69",  False),
    ("128", "0.273", "0.275", "0.272", "0.274", "0.722", "0.025", "0.0237", "53",  False),
]
col_w = [Inches(0.85), Inches(1.10), Inches(1.45), Inches(1.20),
         Inches(1.20), Inches(1.15), Inches(1.55), Inches(1.30),
         Inches(1.20)]
col_x = [Inches(0.5)]
for w in col_w[:-1]:
    col_x.append(col_x[-1] + w)
y = Inches(1.65)
for x, w, c in zip(col_x, col_w, cols):
    add_rect(s, x, y, w, Inches(0.50), PURPLE)
    add_text(s, x + Inches(0.08), y + Inches(0.14), w, Inches(0.3),
             c, size=12, color=WHITE, bold=True)
y = Inches(2.15)
for ri, row in enumerate(data):
    is_w = row[-1]
    for x, w, c in zip(col_x, col_w, row[:-1]):
        add_rect(s, x, y, w, Inches(0.55),
                 PURPLE_TINT if is_w else (CARD_BG if ri % 2 == 0 else WHITE),
                 line=BORDER)
        col = PURPLE_DARK if is_w else NEAR_BLACK
        add_text(s, x + Inches(0.08), y + Inches(0.16), w, Inches(0.3),
                 c, size=13, color=col, bold=is_w)
    y += Inches(0.55)

# Demo backbone lock callout
add_rect(s, Inches(0.5), Inches(4.30), Inches(12.5), Inches(0.65),
         GREEN_TINT)
add_text(s, Inches(0.7), Inches(4.42), Inches(12), Inches(0.4),
         "DEMO BACKBONE LOCKED  →  ae_z32  ·  gNMI 0.334  ·  genre@5 0.723  "
         "·  42 MB index  ·  < 5 ms cosine query",
         size=14, color=GREEN, bold=True)

# 4 why-z32 KPI cards (uniform format)
why = [
    ("gNMI Δ",        "+0.061",  "vs z = 128"),
    ("dim_std_min Δ", "+0.092",  "vs z = 128"),
    ("Index size",    "÷ 4",     "vs z = 128"),
    ("Inference",     "× 2",     "faster"),
]
y = Inches(5.30)
for i, (k, big, label) in enumerate(why):
    x = Inches(0.5 + i * 3.16)
    add_rect(s, x, y, Inches(3.02), Inches(1.55), WHITE, line=BORDER)
    add_rect(s, x, y, Inches(0.06), Inches(1.55), GREEN)
    add_text(s, x + Inches(0.18), y + Inches(0.12),
             Inches(2.7), Inches(0.3),
             k.upper(), size=10.5, color=GREEN, bold=True)
    add_text(s, x + Inches(0.18), y + Inches(0.42),
             Inches(2.7), Inches(0.7),
             big, size=24, color=NEAR_BLACK, bold=True)
    add_text(s, x + Inches(0.18), y + Inches(1.05),
             Inches(2.7), Inches(0.4),
             label, size=11, color=SLATE)

add_footer(s, 19)


# ── 20. SYSTEM ARCHITECTURE (figure embed) ────────────────────────────────
s = new_slide()
page_bg(s)
add_left_stripe(s)
add_title_bar(s, "System architecture — how the pieces fit",
              eyebrow="System")

# Embed the rendered architecture PNG, full-bleed within slide content area.
# Slide is 13.333 wide. Title bar uses y=0.30-1.30. Footer at y=7.10+.
# Available figure area: y=1.40 → 6.20 (height 4.80 in). Width 0.5 → 12.83 (12.33 in).
add_picture_safe(s, FIG_FINAL / "system_architecture.png",
                 Inches(0.5), Inches(1.40),
                 w=Inches(12.33), h=Inches(4.80))

# Bottom KPI strip — kept as compact validation chips
kpis = [
    ("CATALOGUE", "329,044"),
    ("LATENT",    "32-d"),
    ("LATENCY",   "< 5 ms"),
    ("TESTS",     "107"),
    ("CLUSTERS",  "21 named"),
]
y = Inches(6.32)
for i, (lbl, val) in enumerate(kpis):
    x = Inches(0.5 + i * 2.48)
    add_rect(s, x, y, Inches(2.36), Inches(0.72), CARD_BG, line=BORDER)
    add_text(s, x + Inches(0.18), y + Inches(0.08),
             Inches(2.0), Inches(0.24),
             lbl, size=10, color=PURPLE, bold=True)
    add_text(s, x + Inches(0.18), y + Inches(0.30),
             Inches(2.0), Inches(0.4),
             val, size=18, color=NEAR_BLACK, bold=True)

add_footer(s, 20)


# ── 21. EXAMPLE RECOMMENDATIONS ───────────────────────────────────────────
s = new_slide()
page_bg(s)
add_left_stripe(s)
add_title_bar(s, "Example recommendations · demo backbone ae_z32",
              eyebrow="Qualitative evaluation")

queries = [
    ("Inception",
     [("Interstellar",                       "0.991"),
      ("Avengers: Age of Ultron",            "0.989"),
      ("The Avengers",                       "0.985"),
      ("The Dark Knight Rises",              "0.984"),
      ("Dunkirk",                            "0.983")]),
    ("Spirited Away",
     [("Princess Mononoke",                  "0.993"),
      ("Nausicaä of the Valley of the Wind", "0.991"),
      ("Pom Poko",                           "0.989"),
      ("Kiki's Delivery Service",            "0.987"),
      ("Castle in the Sky",                  "0.985")]),
    ("Pulp Fiction",
     [("Kill Bill: Vol. 2",                  "0.987"),
      ("Reservoir Dogs",                     "0.985"),
      ("Jackie Brown",                       "0.982"),
      ("Kill Bill: Vol. 1",                  "0.981"),
      ("Inglourious Basterds",               "0.978")]),
]
cx0 = Inches(0.5); cy = Inches(1.55); cw = Inches(4.10); ch = Inches(4.85)
for i, (q, items) in enumerate(queries):
    x = cx0 + Inches(i * 4.18)
    add_rect(s, x, cy, cw, ch, WHITE, line=BORDER)
    add_rect(s, x, cy, cw, Inches(0.55), PURPLE_DARK)
    add_text(s, x + Inches(0.22), cy + Inches(0.13),
             cw - Inches(0.3), Inches(0.4),
             q, size=15, color=WHITE, bold=True, italic=True)
    yy = cy + Inches(0.85)
    for j, (name, cos) in enumerate(items):
        add_text(s, x + Inches(0.20), yy, Inches(0.45), Inches(0.4),
                 f"{j+1}.", size=12, color=PURPLE, bold=True)
        add_text(s, x + Inches(0.62), yy, cw - Inches(1.6), Inches(0.4),
                 name, size=12, color=NEAR_BLACK)
        add_text(s, x + cw - Inches(0.95), yy, Inches(0.85), Inches(0.4),
                 cos, size=12, color=GREEN, bold=True, align="right",
                 font="Consolas")
        yy += Inches(0.78)

add_rect(s, Inches(0.5), Inches(6.55), Inches(12.5), Inches(0.55),
         PURPLE_TINT)
add_text(s, Inches(0.7), Inches(6.65), Inches(12), Inches(0.4),
         "Director signatures (Nolan, Miyazaki, Tarantino) recovered "
         "without any explicit director label.",
         size=13, color=PURPLE_DARK, italic=True, bold=True)

add_footer(s, 21)


# ── 22. DISCUSSION + LIMITATIONS ──────────────────────────────────────────
s = new_slide()
page_bg(s)
add_left_stripe(s)
add_title_bar(s, "Discussion · what worked, what didn't, what's left",
              eyebrow="Reflection")

# Left column — What worked
lx = Inches(0.5); ly = Inches(1.55); lw = Inches(6.05); lh = Inches(5.30)
add_rect(s, lx, ly, lw, lh, WHITE, line=BORDER)
add_rect(s, lx, ly, lw, Inches(0.55), GREEN)
add_text(s, lx + Inches(0.22), ly + Inches(0.13), lw, Inches(0.4),
         "What worked", size=14, color=WHITE, bold=True)
add_bullets(s, lx + Inches(0.22), ly + Inches(0.75),
            lw - Inches(0.44), Inches(4.5), [
    "Multi-modal projection + W2 weighting — complementary choices.",
    "Three-axis NMI / ARI / AMI surfaced the Pareto trade-off.",
    "Retrieval sanity check caught the F1 angular collapse pre-deploy.",
    "Two-round strategy — 80 % compute saving vs 21-run matrix.",
    "Reproducibility: 107 tests · pinned seed · MD5-checked features.",
], size=13, line_gap=Inches(0.78))

# Right column — Limitations
rx = Inches(6.80)
add_rect(s, rx, ly, lw, lh, WHITE, line=BORDER)
add_rect(s, rx, ly, lw, Inches(0.55), AMBER)
add_text(s, rx + Inches(0.22), ly + Inches(0.13), lw, Inches(0.4),
         "Limitations / future work",
         size=14, color=WHITE, bold=True)
add_bullets(s, rx + Inches(0.22), ly + Inches(0.75),
            lw - Inches(0.44), Inches(4.5), [
    "Modality-dropout failed — target-preserving augmentations next.",
    "VAE posterior collapse not falsified — log per-epoch recon vs KL.",
    "Single-seed numbers — multi-seed bands would tighten claims.",
    "No collaborative signal — two-tower extension natural next.",
    "No user study — genre@5 is a content proxy, not user-judged.",
], size=13, line_gap=Inches(0.78))

add_footer(s, 22)


# ── 23. REFERENCES ────────────────────────────────────────────────────────
s = new_slide()
page_bg(s)
add_left_stripe(s)
add_title_bar(s, "References — core literature",
              eyebrow="References")

refs = [
    ("Xie, Girshick & Farhadi", "2016",
     "Unsupervised Deep Embedding for Clustering Analysis",
     "ICML — DEC method, target distribution P from Q²/f_j."),
    ("Wang, Bao, Huang et al.", "2020",
     "MiniLM: Deep Self-Attention Distillation for Pre-Trained Transformers",
     "NeurIPS — sentence-transformers/all-MiniLM-L12-v2 (384-d)."),
    ("van den Oord, Li & Vinyals", "2018",
     "Representation Learning with Contrastive Predictive Coding",
     "arXiv:1807.03748 — InfoNCE objective."),
    ("Kingma & Welling", "2013",
     "Auto-Encoding Variational Bayes",
     "ICLR — VAE; ELBO = recon + KL(q‖p)."),
    ("Vinh, Epps & Bailey", "2010",
     "Information Theoretic Measures for Clusterings Comparison",
     "JMLR — adjusted NMI / AMI definitions."),
    ("Strehl & Ghosh", "2002",
     "Cluster Ensembles — Knowledge Reuse Framework",
     "JMLR — original NMI definition."),
    ("McInnes, Healy & Melville", "2018",
     "UMAP: Uniform Manifold Approximation and Projection",
     "arXiv:1802.03426 — 2-D topology visualisation."),
    ("Pedregosa, Varoquaux et al.", "2011",
     "Scikit-learn: Machine Learning in Python",
     "JMLR — MiniBatchKMeans, PCA, clustering metrics."),
]

# 2 × 4 grid of compact citation cards — tightened so TOOLS strip clears.
gx0 = Inches(0.5); gy0 = Inches(1.55)
cw = Inches(6.16); ch = Inches(1.05); col_gap = Inches(0.20); row_gap = Inches(0.08)
for i, (authors, year, title, note) in enumerate(refs):
    col = i % 2; row = i // 2
    x = gx0 + (cw + col_gap) * col
    y = gy0 + (ch + row_gap) * row
    add_rect(s, x, y, cw, ch, WHITE, line=BORDER)
    add_rect(s, x, y, Inches(0.06), ch, PURPLE)
    # Authors + year
    add_text(s, x + Inches(0.18), y + Inches(0.06),
             cw - Inches(0.3), Inches(0.28),
             f"{authors} ({year})",
             size=12, color=PURPLE_DARK, bold=True)
    # Title
    add_text(s, x + Inches(0.18), y + Inches(0.34),
             cw - Inches(0.3), Inches(0.34),
             title, size=11.5, color=NEAR_BLACK, italic=True)
    # Note
    add_text(s, x + Inches(0.18), y + Inches(0.70),
             cw - Inches(0.3), Inches(0.28),
             note, size=10, color=SLATE)

# Grid ends at 1.55 + 4*1.05 + 3*0.08 = 5.99. Strip below it with margin.
add_rect(s, Inches(0.5), Inches(6.18), Inches(12.36), Inches(0.75),
         PURPLE_TINT)
add_text(s, Inches(0.7), Inches(6.27), Inches(11.9), Inches(0.28),
         "TOOLS & DATA",
         size=10, color=PURPLE, bold=True)
add_text(s, Inches(0.7), Inches(6.55), Inches(11.9), Inches(0.32),
         "TMDb API (themoviedb.org)  ·  PyTorch  ·  Weights & Biases  ·  "
         "FastAPI  ·  Next.js  ·  pandoc + xelatex",
         size=11, color=NEAR_BLACK, font="Consolas")

add_notes(s, "Q: Why these papers and not others?\n"
          "A: One ref per core technique we use. DEC for clustering, "
          "MiniLM for text, InfoNCE for contrastive, VAE for posterior collapse "
          "discussion, NMI/AMI for evaluation, UMAP for visualisation, "
          "scikit-learn for non-deep baselines.\n\n"
          "Q: No collaborative filtering refs?\n"
          "A: Deliberately — we have zero user signal in the TMDb dump. "
          "Two-tower / matrix factorisation refs would be future work.")
add_footer(s, 23)


# ── 24. CONCLUSION ────────────────────────────────────────────────────────
s = new_slide()
page_bg(s, NEAR_BLACK)
add_dotgrid_band(s, Inches(10.5), Inches(0), Inches(2.83), SLIDE_H, PURPLE)

add_text(s, Inches(0.7), Inches(0.55), Inches(11), Inches(0.4),
         "CONCLUSION", size=14, color=PURPLE_TINT, bold=True)

add_text(s, Inches(0.7), Inches(1.05), Inches(9.5), Inches(2.0),
         "CineEmbed ships a working\nmulti-modal unsupervised film recommender.",
         size=34, color=WHITE, bold=True)

add_text(s, Inches(0.7), Inches(2.95), Inches(9.5), Inches(0.5),
         "All three pre-registered hypotheses PASS (H1/H2/H3).",
         size=15, color=PURPLE_TINT)
add_text(s, Inches(0.7), Inches(3.30), Inches(9.5), Inches(0.5),
         "Two methodological findings beyond the system itself:",
         size=15, color=PURPLE_TINT)

# F1 / F2 callout cards
add_rect(s, Inches(0.7), Inches(4.00), Inches(4.6), Inches(1.5),
         RGBColor(0x29, 0x21, 0x57), line=PURPLE)
add_text(s, Inches(0.9), Inches(4.12), Inches(4.4), Inches(0.4),
         "F1", size=14, color=PURPLE_TINT, bold=True)
add_text(s, Inches(0.9), Inches(4.42), Inches(4.4), Inches(0.5),
         "NMI ≠ retrieval", size=22, color=WHITE, bold=True)
add_text(s, Inches(0.9), Inches(4.92), Inches(4.4), Inches(0.5),
         "DEC angular collapse:",
         size=11, color=PURPLE_TINT)
add_text(s, Inches(0.9), Inches(5.20), Inches(4.4), Inches(0.4),
         "top-5 cosine ≈ 1.000",
         size=12, color=WHITE, bold=True, font="Consolas")

add_rect(s, Inches(5.6), Inches(4.00), Inches(4.6), Inches(1.5),
         RGBColor(0x29, 0x21, 0x57), line=PURPLE)
add_text(s, Inches(5.8), Inches(4.12), Inches(4.4), Inches(0.4),
         "F2", size=14, color=PURPLE_TINT, bold=True)
add_text(s, Inches(5.8), Inches(4.42), Inches(4.4), Inches(0.5),
         "z = 32 wins", size=22, color=WHITE, bold=True)
add_text(s, Inches(5.8), Inches(4.92), Inches(4.4), Inches(0.5),
         "Tight latent beats z=64 and z=128",
         size=11, color=PURPLE_TINT)
add_text(s, Inches(5.8), Inches(5.20), Inches(4.4), Inches(0.4),
         "gNMI 0.334  ·  genre@5 0.723",
         size=12, color=WHITE, bold=True, font="Consolas")

# Best config as 4 chips
add_text(s, Inches(0.7), Inches(5.75), Inches(9.5), Inches(0.3),
         "BEST CONFIGURATION",
         size=11, color=PURPLE_TINT, bold=True)
best_chips = [
    ("BACKBONE", "ae_z32"),
    ("gNMI",     "0.334"),
    ("genre@5",  "0.723"),
    ("INDEX",    "42 MB"),
]
y = Inches(6.10)
for i, (lbl, val) in enumerate(best_chips):
    x = Inches(0.7 + i * 2.40)
    add_rect(s, x, y, Inches(2.30), Inches(0.70),
             RGBColor(0x29, 0x21, 0x57), line=PURPLE)
    add_text(s, x + Inches(0.18), y + Inches(0.08),
             Inches(2.0), Inches(0.25),
             lbl, size=9, color=PURPLE_TINT, bold=True)
    add_text(s, x + Inches(0.18), y + Inches(0.32),
             Inches(2.0), Inches(0.40),
             val, size=18, color=WHITE, bold=True,
             font="Consolas" if i in {0, 3} else FONT)

# URL + team
add_text(s, Inches(0.7), Inches(6.95), Inches(9.5), Inches(0.3),
         "Code:  github.com/barandincoguz/CineEmbed-",
         size=12, color=WHITE)
add_text(s, Inches(0.7), Inches(7.25), Inches(11), Inches(0.25),
         "Baran Dinçoğuz  ·  Arda Arvas  ·  Kaan Kaya  ·  SENG 474 — Spring 2026  ·  TED University",
         size=11, color=SLATE_LIGHT)


# ── Speaker-defense notes (presenter view) ────────────────────────────────
# Indexed 0..N-1. Each note is a self-contained Q&A block to brief the
# presenter on likely instructor questions ("why X? why not Y?").
SPEAKER_NOTES = {
    0: (
        "TEAM ROLES (split as relevant during Q&A):\n"
        "  · Baran — pipeline, training, evaluation\n"
        "  · Arda — backend (FastAPI), API tests\n"
        "  · Kaan — frontend (Next.js), UX\n\n"
        "If asked 'why this title?' — CineEmbed = Cinema + Embedding."
    ),
    1: (  # s02 Why this problem?
        "Q: Why TMDb, not MovieLens or Netflix Prize?\n"
        "A: TMDb has rich ITEM metadata (overview text, director, awards) "
        "with a free API. MovieLens / Netflix are user-rating-centric — wrong "
        "fit for content-based learning.\n\n"
        "Q: Is 329k films enough?\n"
        "A: Yes — covers ~95 % of post-1980 commercial releases. The bottleneck "
        "is feature richness per film, not row count."
    ),
    2: (  # s03 Why unsupervised?
        "Q: Why not just label some films and train supervised?\n"
        "A: Hand-labelling 329k films is unrealistic, and the genre/decade/"
        "language axes ARE the labels — using them as supervision would invalidate "
        "the evaluation. We deliberately keep them OUT of the loss.\n\n"
        "Q: Why three label axes and not one?\n"
        "A: Single-axis NMI hides modality-specific failures. Three orthogonal "
        "axes expose the Pareto trade-off (slide 11)."
    ),
    3: (  # s04 Data
        "Q: Why MiniLM-L12-v2 for text (not BERT-large or GPT embeddings)?\n"
        "A: 384-d is the right size for 329k rows — bigger LMs add latency without "
        "downstream gain. Deterministic, free, runs offline on CPU.\n\n"
        "Q: Director bio coverage is only 3.18 % — why include it?\n"
        "A: Where present, director identity is the strongest single signal for "
        "style similarity (see Nolan/Miyazaki/Tarantino on slide 21). Masking "
        "(G2 loss) keeps the missing-bio rows from poisoning the loss."
    ),
    4: (  # s05 Pipeline
        "Q: Why seed = 42 everywhere?\n"
        "A: Single seed across the pipeline guarantees that the same EDA dump "
        "produces the same model produces the same index. Re-running the 107 "
        "pytest suite from a clean clone reproduces the demo bit-for-bit.\n\n"
        "Q: Why MiniBatchKMeans, not full KMeans?\n"
        "A: 329k × 32 fits in memory but MiniBatchKMeans is 10× faster and "
        "the centroids are indistinguishable at k = 21."
    ),
    5: (  # s06 Architecture
        "Q: Why per-block projection instead of concat-then-encode?\n"
        "A: Modalities have wildly different dimensionalities (text 384-d, "
        "decade 2-d). Without per-block projection, the loss is dominated by "
        "whichever block has the highest variance — that's exactly the W1 "
        "failure on slide 13.\n\n"
        "Q: Why under 500k parameters?\n"
        "A: Forces the model to compress, not memorise. Also test-pinned so "
        "future code changes can't accidentally inflate the model."
    ),
    6: (  # s07 Loss functions
        "Q: Why is the DEC loss weight 0.1 on reconstruction?\n"
        "A: Standard DEC schedule (Xie 2016). Too high → recon dominates and "
        "clusters don't sharpen. Too low → encoder drifts away from useful features.\n\n"
        "Q: Why τ = 0.1 for InfoNCE?\n"
        "A: Default contrastive temperature. We did not tune τ — the InfoNCE "
        "pretext failed for a different reason (target augmentation breaks the "
        "label; see ND-1 on slide 14)."
    ),
    7: (  # s08 Methodology
        "Q: Why genre@5, not genre@10 or @20?\n"
        "A: top-5 is what the demo UI shows. Aligning the metric with the "
        "deliverable was a deliberate ADR (D08).\n\n"
        "Q: Why is dim_std a useful diagnostic?\n"
        "A: A latent dimension with std ≈ 0 carries no information — wasted "
        "capacity. The dim_std_min on slide 18 is what gave us F2."
    ),
    8: (  # s09 H2 result
        "Q: Why a +10 % threshold in H2?\n"
        "A: Pre-registered in the proposal — set BEFORE we trained anything. "
        "We over-shot at +205 %, which is reported relative to the BEST non-deep "
        "baseline (kmeans_raw), not a strawman."
    ),
    9: (  # s10 Phase 0 MVP
        "Q: Why z = 64 for the MVP and not the final z = 32?\n"
        "A: Phase 0 was the architecture-discovery sweep — we hadn't run the "
        "z-sweep yet. MVP was 'is this approach viable?' (yes). Round 2 (slide 19) "
        "is where we picked z = 32.\n\n"
        "Q: Why W1 only as an ablation and not the default?\n"
        "A: We knew variance imbalance would hurt — W1 was the falsification "
        "experiment that confirmed W2's contribution."
    ),
    10: (  # s11 Cross-cuts
        "Q: How did you pick these nine findings?\n"
        "A: Each one maps to a different research-question dimension (modality, "
        "weighting, architecture, evaluation). Nothing was retro-fitted — these "
        "are the cells of the results matrix that yielded a clear answer."
    ),
    11: (  # s12 UMAP
        "Q: Why 15k subsample for UMAP, not all 329k?\n"
        "A: Full UMAP at 329k takes 4+ hours and the manifold is stable above "
        "10k — we verified with a 30k re-run. 15k is a reproducibility sweet spot.\n\n"
        "Q: Are the 'islands' real or UMAP artifacts?\n"
        "A: Confirmed by genre@5 (slide 19) and the cluster-coherence numbers — "
        "the islands match named clusters in artifacts/clusters/."
    ),
    12: (  # s13 Ablations
        "Q: Why does W1 still win on decade?\n"
        "A: Decade is 2-d — StandardScaler already gives it per-feature variance "
        "≈ 1, so W1 doesn't hurt it. Text (384-d) and language (31-d) are where "
        "W1 collapses.\n\n"
        "Q: Missing-release-date films are 7.4 % — should you have dropped them?\n"
        "A: No — they form a coherent sub-manifold (slide 13 right). Dropping "
        "them would have removed legitimate signal about older/incomplete entries."
    ),
    13: (  # s14 Negative results
        "Q: Why present negative results at all?\n"
        "A: Honesty + the lessons drive the methodology. ND-1 surfaced the "
        "augmentation-vs-target principle. ND-2 isolated the contrastive "
        "encoder as the broken link, not DEC. ND-3 is in the future-work queue.\n\n"
        "Q: Why didn't you log per-epoch recon vs KL for the VAE?\n"
        "A: Oversight — we logged total loss only. Adding the split is task #1 "
        "in the future-work list."
    ),
    14: (  # s15 F1
        "Q: Is this a known result in the clustering literature?\n"
        "A: Cluster-quality vs retrieval-quality divergence is known in general, "
        "but DEC-specific angular collapse (top-5 cosine ≈ 1.000) is not "
        "highlighted in Xie 2016 or follow-ups. That's what we contribute.\n\n"
        "Q: Could you fix DEC by reducing the KL weight?\n"
        "A: Probably — but for our deliverable (retrieval), AE-only already "
        "wins. No reason to chase a fix when the simpler model is better."
    ),
    15: (  # s16 F1 evidence
        "Q: Why 400 queries for the histogram?\n"
        "A: 316 popular queries (full deploy eval set) + 84 random films "
        "spanning rare genres. Matches our deploy gate on slide 8."
    ),
    16: (  # s17 F2
        "Q: Why 100 epochs (and not 200, 500)?\n"
        "A: Early-stop patience = 10. z = 64 and z = 128 hit early-stop before "
        "100 (epoch 69 and 53). z = 32 used the full 100-epoch budget because "
        "val_loss was still improving — capacity is tight, so it learns longer.\n\n"
        "Q: Why not z = 16 or z = 8?\n"
        "A: Outside our pre-registered grid {32, 64, 128}. Adding smaller z is "
        "the obvious next sweep — listed as future work.\n\n"
        "Q: Five signals — isn't that p-hacking?\n"
        "A: All five (gNMI, dim_std, pair_cos_std, val_loss, simplicity) were "
        "decided BEFORE the sweep. We didn't pick metrics post-hoc."
    ),
    17: (  # s18 dim_std
        "Q: Why is dim_std = 0.025 'near-dead'?\n"
        "A: That dimension's output is essentially constant — it carries no "
        "per-film information. ~25 % of z = 128 dimensions are in that regime, "
        "which is why doubling capacity from 64 didn't help."
    ),
    18: (  # s19 Round 2
        "Q: Why only three z values? Why not a finer sweep?\n"
        "A: Log-spaced grid {32, 64, 128} — standard practice for capacity "
        "sweeps. The U-curve is monotone enough that a finer grid wouldn't "
        "change the verdict.\n\n"
        "Q: Why pick gNMI as the primary axis?\n"
        "A: Composite over the three orthogonal axes — single-axis would have "
        "biased toward whichever was easiest (decade)."
    ),
    19: (  # s20 Architecture
        "Q: Why FastAPI instead of Flask or Django?\n"
        "A: Native async, pydantic schemas, automatic OpenAPI docs — fits a "
        "small high-throughput recommendation API.\n\n"
        "Q: Why mmap the embeddings?\n"
        "A: 42 MB is small but mmap gives constant memory at boot, lets the OS "
        "page-cache, and survives uvicorn restarts without re-loading.\n\n"
        "Q: Why Next.js 16 and not plain React?\n"
        "A: Server Components let us cache TMDb poster lookups on the edge. "
        "App Router is the future-proof React 19 stack.\n\n"
        "Q: Where is the database?\n"
        "A: No DB — embeddings + lookup tables are static artifacts. Single "
        "Docker image, no infra. Adding a DB is a future feature, not core."
    ),
    20: (  # s21 Qualitative
        "Q: Cherry-picked queries?\n"
        "A: The 10 canonical queries were chosen BEFORE the final model trained "
        "(pre-registered in artifacts/eval/canonical_queries.json). The director "
        "signatures emerging unsupervised is the strongest qualitative claim.\n\n"
        "Q: Why are scores all 0.97+?\n"
        "A: Cosine on L2-normalised vectors saturates near 1 for tight neighbours. "
        "The ORDERING is what matters, not the absolute number."
    ),
    21: (  # s22 Reflection
        "Q: Biggest threat to validity?\n"
        "A: Single seed. Multi-seed bands (3–5 seeds) would tighten every "
        "confidence interval and is the top robustness task.\n\n"
        "Q: Why no user study?\n"
        "A: Scope. genre@5 is a content proxy, not a relevance score. A 5-rater "
        "user study on 50 queries is the natural validation step."
    ),
    22: (  # s23 References — set inline by add_notes above
        ""
    ),
    23: (  # s24 Conclusion
        "Q: One-line takeaway?\n"
        "A: Deep multi-modal unsupervised learning beats every non-deep baseline "
        "by 3-5× on TMDb metadata — and the smallest latent (z = 32) wins.\n\n"
        "Q: If you had one more semester?\n"
        "A: Multi-seed bands, log per-epoch VAE recon vs KL (close ND-3), and "
        "a 5-rater user study on top-5 relevance."
    ),
}

for idx, note in SPEAKER_NOTES.items():
    if not note:
        continue
    if idx >= len(prs.slides):
        continue
    slide = prs.slides[idx]
    slide.notes_slide.notes_text_frame.text = note


# ── save ──────────────────────────────────────────────────────────────────
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
prs.save(OUT_PATH)
print(f"saved {OUT_PATH}")
print(f"slides: {len(prs.slides)}")

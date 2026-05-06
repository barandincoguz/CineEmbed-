"""Centralized theme: colors, fonts, sizes, layout helpers.

All numeric layout constants are in EMU (English Metric Units) via Inches/Pt.
The slide canvas is 13.333" x 7.5" (16:9 widescreen, PowerPoint default).
"""
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor


# ----- Slide canvas -----
SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)


# ----- Brand palette (matches LaTeX report) -----
class Colors:
    PRIMARY     = RGBColor(0xC2, 0x41, 0x0C)  # orange — section headings, headline numbers
    SECONDARY   = RGBColor(0x25, 0x63, 0xEB)  # blue — links, planned status
    ACCENT      = RGBColor(0x15, 0x80, 0x3D)  # green — complete status
    AMBER       = RGBColor(0xB4, 0x53, 0x09)  # in-progress status
    SLATE       = RGBColor(0x64, 0x74, 0x8B)  # body de-emphasis, deferred status
    NEAR_BLACK  = RGBColor(0x1E, 0x29, 0x3B)  # body text
    ROW_ALT     = RGBColor(0xF8, 0xFA, 0xFC)  # alternating row shading
    HEADER_FILL = RGBColor(0xF1, 0xF5, 0xF9)  # table header fill
    WHITE       = RGBColor(0xFF, 0xFF, 0xFF)


# ----- Typography -----
class Fonts:
    HEADING = "Calibri Light"
    BODY    = "Calibri"


# ----- Type scale (in points) -----
class Sizes:
    TITLE        = Pt(36)
    SUBTITLE     = Pt(20)
    SECTION_LBL  = Pt(14)
    BODY         = Pt(18)
    BODY_SMALL   = Pt(14)
    CAPTION      = Pt(12)
    PILL         = Pt(11)
    HEADLINE_BIG = Pt(180)
    FOOTER       = Pt(10)


# ----- Layout regions (positions / sizes) -----
class Layout:
    # Color bar at the top of every content slide
    BAR_LEFT   = Emu(0)
    BAR_TOP    = Emu(0)
    BAR_WIDTH  = SLIDE_W
    BAR_HEIGHT = Inches(0.083)

    # Slide title bounds
    TITLE_LEFT   = Inches(0.5)
    TITLE_TOP    = Inches(0.30)
    TITLE_WIDTH  = Inches(12.333)
    TITLE_HEIGHT = Inches(0.75)

    # Subtitle (under title, on content slides)
    SUBTITLE_LEFT   = Inches(0.5)
    SUBTITLE_TOP    = Inches(1.0)
    SUBTITLE_WIDTH  = Inches(12.333)
    SUBTITLE_HEIGHT = Inches(0.4)

    # Body content region
    BODY_LEFT   = Inches(0.5)
    BODY_TOP    = Inches(1.55)
    BODY_WIDTH  = Inches(12.333)
    BODY_HEIGHT = Inches(5.5)

    # Footer
    FOOTER_LEFT   = Inches(0.5)
    FOOTER_TOP    = Inches(7.15)
    FOOTER_WIDTH  = Inches(12.333)
    FOOTER_HEIGHT = Inches(0.25)


# ----- Project repo paths (relative to docs/presentation/) -----
REPO_ROOT          = "../../"
FIG_UMAP_DIR       = REPO_ROOT + "artifacts/figures/umap/"
FIG_EDA_DIR        = REPO_ROOT + "artifacts/figures/"
FIG_DIAGRAM_DIR    = REPO_ROOT + "figures/"

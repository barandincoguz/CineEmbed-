"""One builder function per slide. Each builder accepts a `prs` (Presentation)
and adds a fully-built slide. Phase 4 ships stubs; Phase 5 fills them in.
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

from . import theme, components as C

TOTAL = 12


def _new_blank_slide(prs):
    """Add a blank-layout slide (layout index 6 in default master)."""
    blank_layout = prs.slide_layouts[6]
    return prs.slides.add_slide(blank_layout)


def _content_slide(prs, idx: int, title: str, subtitle: str = ""):
    """Standard content slide: top bar, title, optional subtitle, footer."""
    s = _new_blank_slide(prs)
    C.add_top_bar(s)
    C.add_title(s, title)
    if subtitle:
        C.add_subtitle(s, subtitle)
    C.add_footer(s, idx, TOTAL)
    return s


# Stub builders — replaced in Phase 5
def slide_01_title(prs):       _content_slide(prs, 1, "Slide 1 — title (stub)")
def slide_02_status(prs):      _content_slide(prs, 2, "Slide 2 — status (stub)")
def slide_03_goal(prs):        _content_slide(prs, 3, "Slide 3 — goal (stub)")
def slide_04_schedule(prs):    _content_slide(prs, 4, "Slide 4 — schedule (stub)")
def slide_05_data(prs):        _content_slide(prs, 5, "Slide 5 — data (stub)")
def slide_06_arch(prs):        _content_slide(prs, 6, "Slide 6 — architecture (stub)")
def slide_07_mvp_table(prs):   _content_slide(prs, 7, "Slide 7 — MVP table (stub)")
def slide_08_headline(prs):    _content_slide(prs, 8, "Slide 8 — headline (stub)")
def slide_09_topology(prs):    _content_slide(prs, 9, "Slide 9 — topology (stub)")
def slide_10_bonus(prs):       _content_slide(prs, 10, "Slide 10 — bonus (stub)")
def slide_11_plan(prs):        _content_slide(prs, 11, "Slide 11 — plan (stub)")
def slide_12_close(prs):       _content_slide(prs, 12, "Slide 12 — close (stub)")


BUILDERS = [
    slide_01_title, slide_02_status, slide_03_goal, slide_04_schedule,
    slide_05_data, slide_06_arch, slide_07_mvp_table, slide_08_headline,
    slide_09_topology, slide_10_bonus, slide_11_plan, slide_12_close,
]

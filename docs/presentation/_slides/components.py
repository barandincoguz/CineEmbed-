"""Reusable PowerPoint shape primitives.

All functions take a `slide` and return the shape they added (so callers can
tweak position if needed). Keep this module purely cosmetic — no business
content lives here.
"""
from typing import Sequence
from pptx.util import Inches, Pt, Emu
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

from . import theme


# ---------- Slide chrome ----------

def add_top_bar(slide):
    """Brand-primary color bar across the top of the slide."""
    bar = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        theme.Layout.BAR_LEFT, theme.Layout.BAR_TOP,
        theme.Layout.BAR_WIDTH, theme.Layout.BAR_HEIGHT,
    )
    bar.line.fill.background()
    bar.fill.solid()
    bar.fill.fore_color.rgb = theme.Colors.PRIMARY
    return bar


def add_title(slide, text: str):
    tb = slide.shapes.add_textbox(
        theme.Layout.TITLE_LEFT, theme.Layout.TITLE_TOP,
        theme.Layout.TITLE_WIDTH, theme.Layout.TITLE_HEIGHT,
    )
    tf = tb.text_frame
    tf.margin_left = tf.margin_right = Emu(0)
    tf.margin_top = tf.margin_bottom = Emu(0)
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    run = p.add_run()
    run.text = text
    run.font.name = theme.Fonts.HEADING
    run.font.size = theme.Sizes.TITLE
    run.font.bold = False
    run.font.color.rgb = theme.Colors.PRIMARY
    return tb


def add_subtitle(slide, text: str):
    tb = slide.shapes.add_textbox(
        theme.Layout.SUBTITLE_LEFT, theme.Layout.SUBTITLE_TOP,
        theme.Layout.SUBTITLE_WIDTH, theme.Layout.SUBTITLE_HEIGHT,
    )
    tf = tb.text_frame
    tf.margin_left = tf.margin_right = Emu(0)
    tf.margin_top = tf.margin_bottom = Emu(0)
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    run = p.add_run()
    run.text = text
    run.font.name = theme.Fonts.BODY
    run.font.size = theme.Sizes.SUBTITLE
    run.font.color.rgb = theme.Colors.SLATE
    return tb


def add_footer(slide, page_num: int, total_pages: int):
    tb = slide.shapes.add_textbox(
        theme.Layout.FOOTER_LEFT, theme.Layout.FOOTER_TOP,
        theme.Layout.FOOTER_WIDTH, theme.Layout.FOOTER_HEIGHT,
    )
    tf = tb.text_frame
    tf.margin_left = tf.margin_right = Emu(0)
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    run = p.add_run()
    run.text = f"SENG 474  ·  CineEmbed  ·  Slide {page_num} / {total_pages}"
    run.font.name = theme.Fonts.BODY
    run.font.size = theme.Sizes.FOOTER
    run.font.color.rgb = theme.Colors.SLATE
    return tb


# ---------- Status pills ----------

_STATUS_COLORS = {
    "complete":   theme.Colors.ACCENT,
    "inprogress": theme.Colors.AMBER,
    "planned":    theme.Colors.SECONDARY,
    "deferred":   theme.Colors.SLATE,
}
_STATUS_LABELS = {
    "complete":   "COMPLETE",
    "inprogress": "IN PROGRESS",
    "planned":    "PLANNED",
    "deferred":   "DEFERRED",
}


def add_status_pill(slide, status: str, left, top, width=Inches(1.4), height=Inches(0.32)):
    """Rounded-rectangle status pill. `status` ∈ {complete, inprogress, planned, deferred}."""
    if status not in _STATUS_COLORS:
        raise ValueError(f"unknown status: {status!r}")
    pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    pill.adjustments[0] = 0.5
    pill.line.fill.background()
    pill.fill.solid()
    pill.fill.fore_color.rgb = _STATUS_COLORS[status]
    tf = pill.text_frame
    tf.margin_left = tf.margin_right = Inches(0.1)
    tf.margin_top = tf.margin_bottom = Emu(0)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = _STATUS_LABELS[status]
    run.font.name = theme.Fonts.BODY
    run.font.size = theme.Sizes.PILL
    run.font.bold = True
    run.font.color.rgb = theme.Colors.WHITE
    return pill


# ---------- Headline number ----------

def add_headline_number(slide, big_text: str, caption_text: str,
                        left=Inches(0.5), top=Inches(2.0),
                        width=Inches(12.333), height=Inches(3.5)):
    """Big primary-color number with smaller slate caption underneath."""
    big = slide.shapes.add_textbox(left, top, width, Inches(2.6))
    tf = big.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = Emu(0)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = big_text
    run.font.name = theme.Fonts.HEADING
    run.font.size = theme.Sizes.HEADLINE_BIG
    run.font.bold = False
    run.font.color.rgb = theme.Colors.PRIMARY

    cap = slide.shapes.add_textbox(left, top + Inches(2.7), width, Inches(0.8))
    tfc = cap.text_frame
    tfc.margin_left = tfc.margin_right = Emu(0)
    tfc.margin_top = tfc.margin_bottom = Emu(0)
    tfc.word_wrap = True
    pc = tfc.paragraphs[0]
    pc.alignment = PP_ALIGN.CENTER
    runc = pc.add_run()
    runc.text = caption_text
    runc.font.name = theme.Fonts.BODY
    runc.font.size = theme.Sizes.BODY
    runc.font.color.rgb = theme.Colors.SLATE
    return big, cap


# ---------- Bullets ----------

def add_bullets(slide, items: Sequence[str],
                left=Inches(0.5), top=Inches(1.7),
                width=Inches(12.333), height=Inches(5.0),
                font_size=None, color=None):
    """Bullet textbox. Bullet marker rendered as literal `•` for portable rendering."""
    font_size = font_size or theme.Sizes.BODY
    color = color or theme.Colors.NEAR_BLACK
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Emu(0)
    tf.margin_top = tf.margin_bottom = Emu(0)
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.space_after = Pt(6)
        run = p.add_run()
        run.text = f"•  {item}"
        run.font.name = theme.Fonts.BODY
        run.font.size = font_size
        run.font.color.rgb = color
    return tb


# ---------- Table renderer ----------

def add_table(slide, header: Sequence[str], rows: Sequence[Sequence[str]],
              left, top, width, height,
              header_fill=None, alt_row_fill=None,
              col_aligns: Sequence[str] = None):
    """Booktabs-style table: header fill + alternating row shading, no internal grid look."""
    header_fill = header_fill or theme.Colors.HEADER_FILL
    alt_row_fill = alt_row_fill or theme.Colors.ROW_ALT
    n_rows = len(rows) + 1
    n_cols = len(header)
    tbl_shape = slide.shapes.add_table(n_rows, n_cols, left, top, width, height)
    tbl = tbl_shape.table

    for j, h in enumerate(header):
        cell = tbl.cell(0, j)
        cell.fill.solid()
        cell.fill.fore_color.rgb = header_fill
        cell.text_frame.text = ""
        p = cell.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT if (col_aligns is None or col_aligns[j] == "l") else PP_ALIGN.RIGHT
        run = p.add_run()
        run.text = h
        run.font.name = theme.Fonts.BODY
        run.font.size = Pt(13)
        run.font.bold = True
        run.font.color.rgb = theme.Colors.NEAR_BLACK

    for i, row in enumerate(rows, start=1):
        is_alt = (i % 2 == 0)
        for j, val in enumerate(row):
            cell = tbl.cell(i, j)
            cell.fill.solid()
            cell.fill.fore_color.rgb = alt_row_fill if is_alt else theme.Colors.WHITE
            cell.text_frame.text = ""
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT if (col_aligns is None or col_aligns[j] == "l") else PP_ALIGN.RIGHT
            run = p.add_run()
            run.text = str(val)
            run.font.name = theme.Fonts.BODY
            run.font.size = Pt(12)
            run.font.color.rgb = theme.Colors.NEAR_BLACK
    return tbl_shape


# ---------- Image ----------

def add_image(slide, path: str, left, top, width=None, height=None):
    """Insert an image from disk. If only width or only height given, aspect is preserved."""
    return slide.shapes.add_picture(path, left, top, width=width, height=height)

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


def slide_01_title(prs):
    s = _new_blank_slide(prs)
    # Orange ribbon at top of slide (full width, ~2 inch tall)
    accent = s.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Emu(0), Emu(0), theme.SLIDE_W, Inches(2.0),
    )
    accent.line.fill.background()
    accent.fill.solid()
    accent.fill.fore_color.rgb = theme.Colors.PRIMARY

    # Title — large, white-on-orange, in the ribbon
    tb = s.shapes.add_textbox(Inches(0.5), Inches(0.55), Inches(12.333), Inches(1.0))
    tf = tb.text_frame
    tf.margin_left = tf.margin_right = Emu(0)
    tf.margin_top = tf.margin_bottom = Emu(0)
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    run = p.add_run()
    run.text = "CineEmbed"
    run.font.name = theme.Fonts.HEADING
    run.font.size = Pt(60)
    run.font.color.rgb = theme.Colors.WHITE

    # Subtitle inside the ribbon
    sub = s.shapes.add_textbox(Inches(0.5), Inches(1.4), Inches(12.333), Inches(0.5))
    tfs = sub.text_frame
    tfs.margin_left = tfs.margin_right = Emu(0)
    ps = tfs.paragraphs[0]
    runs = ps.add_run()
    runs.text = "Multi-Modal Unsupervised Embedding of 329,044 Films"
    runs.font.name = theme.Fonts.BODY
    runs.font.size = Pt(20)
    runs.font.color.rgb = theme.Colors.WHITE

    # Document label below ribbon
    label = s.shapes.add_textbox(Inches(0.5), Inches(2.6), Inches(12.333), Inches(0.5))
    tfl = label.text_frame
    tfl.margin_left = tfl.margin_right = Emu(0)
    pl = tfl.paragraphs[0]
    runl = pl.add_run()
    runl.text = "Intermediate Progress Report  ·  v1.0"
    runl.font.name = theme.Fonts.BODY
    runl.font.size = Pt(20)
    runl.font.color.rgb = theme.Colors.SECONDARY

    # Authors
    auth = s.shapes.add_textbox(Inches(0.5), Inches(4.2), Inches(12.333), Inches(0.6))
    tfa = auth.text_frame
    tfa.margin_left = tfa.margin_right = Emu(0)
    pa = tfa.paragraphs[0]
    runa = pa.add_run()
    runa.text = "Ahmet Baran Dincoguz   ·   Arda Arvas   ·   Bertan Kaan Kaya"
    runa.font.name = theme.Fonts.BODY
    runa.font.size = Pt(22)
    runa.font.color.rgb = theme.Colors.NEAR_BLACK

    # Course / institution
    course = s.shapes.add_textbox(Inches(0.5), Inches(4.95), Inches(12.333), Inches(0.5))
    tfc = course.text_frame
    pc = tfc.paragraphs[0]
    runc = pc.add_run()
    runc.text = "SENG 474 — Deep Learning · Spring 2026 · TED University · 2026-05-06"
    runc.font.name = theme.Fonts.BODY
    runc.font.size = Pt(16)
    runc.font.color.rgb = theme.Colors.SLATE

    # Repo URL
    repo = s.shapes.add_textbox(Inches(0.5), Inches(6.85), Inches(12.333), Inches(0.4))
    tfr = repo.text_frame
    pr = tfr.paragraphs[0]
    runr = pr.add_run()
    runr.text = "github.com/barandincoguz/CineEmbed-"
    runr.font.name = theme.Fonts.BODY
    runr.font.size = Pt(14)
    runr.font.color.rgb = theme.Colors.SECONDARY


def slide_02_status(prs):
    s = _content_slide(prs, 2, "Project Status: ON TRACK",
                       "Modeling MVP delivered. Hypotheses H1, H2, H3 all PASS.")
    C.add_status_pill(s, "complete", left=Inches(0.5), top=Inches(1.55),
                      width=Inches(2.0), height=Inches(0.45))
    C.add_bullets(s,
        items=[
            "Six runs trained, evaluated against 3 orthogonal label axes (genre · decade · language).",
            "Best deep model dec_z64_k21 reaches genre_NMI = 0.332, +205 % over best non-deep baseline.",
            "Bonus finding: films with missing release date form a coherent latent sub-manifold.",
            "Final-report scope (VAE family, k-sweep, F1/F2 ablations) defined and on schedule.",
        ],
        left=Inches(0.5), top=Inches(2.25), width=Inches(7.0), height=Inches(3.5),
    )
    C.add_headline_number(s, big_text="+205 %",
        caption_text="DEC genre_NMI vs KMeans on raw features (0.332 vs 0.109)",
        left=Inches(7.5), top=Inches(2.20), width=Inches(5.4),
    )


def slide_03_goal(prs):
    s = _content_slide(prs, 3, "Project Goal & Scope",
                       "What we set out to do, on what data.")
    C.add_bullets(s,
        items=[
            "Train unsupervised 64-dim representations of movie metadata.",
            "329,044 films from TMDB + awards records + Wikipedia director bios.",
            "564-dim feature matrix organized into 7 modality blocks.",
            "Recover 3 orthogonal label axes without labels: genre, decade, language.",
            "Evaluate via KMeans clustering of the latent → NMI / ARI.",
        ],
        left=Inches(0.5), top=Inches(1.7), width=Inches(7.5), height=Inches(5.0),
    )
    C.add_table(s,
        header=["Block", "Dim", "Notes"],
        rows=[
            ["numerical", "6",   "popularity, runtime, votes"],
            ["genre",     "22",  "21-way one-hot + flag"],
            ["language",  "31",  "top-30 langs (~99% zero)"],
            ["decade",    "2",   "decade_norm + flag"],
            ["awards",    "6",   "Oscar/BAFTA/Cannes counts"],
            ["text",      "384", "MiniLM-L6-v2 embeddings"],
            ["director",  "113", "bio_pca_64 + lang/country"],
        ],
        left=Inches(8.2), top=Inches(1.65), width=Inches(4.7), height=Inches(3.6),
        col_aligns=["l", "r", "l"],
    )
def slide_04_schedule(prs):
    s = _content_slide(prs, 4, "Schedule & Milestones",
                       "Three phases complete. Final-report phase ahead.")
    C.add_table(s,
        header=["Milestone",                                  "Window",   "Status"],
        rows=[
            ["Feature matrix v1.2 frozen",                    "Apr 2026", "COMPLETE"],
            ["Multi-modal architecture finalized",            "Apr 2026", "COMPLETE"],
            ["Six runs trained and evaluated",                "May 2026", "COMPLETE"],
            ["Pre-registered hypotheses tested",              "May 2026", "COMPLETE"],
            ["UMAP latent analysis",                          "May 2026", "COMPLETE"],
            ["Intermediate progress report",                  "May 2026", "IN PROGRESS"],
            ["VAE family training (z = 32 / 64 / 128)",       "Jun 2026", "PLANNED"],
            ["F1 / F2 modality ablations",                    "Jun 2026", "PLANNED"],
            ["DEC k-sweep (9-cell grid)",                     "Jun 2026", "PLANNED"],
            ["Final report",                                  "Jun 2026", "PLANNED"],
        ],
        left=Inches(0.5), top=Inches(1.65), width=Inches(12.333), height=Inches(5.2),
        col_aligns=["l", "l", "l"],
    )


def slide_05_data(prs):
    s = _content_slide(prs, 5, "Work Completed: Data Engineering",
                       "564-dim feature matrix, 7 modality blocks, frozen v1.2.")
    C.add_status_pill(s, "complete", left=Inches(0.5), top=Inches(1.55),
                      width=Inches(2.0), height=Inches(0.4))
    C.add_bullets(s,
        items=[
            "Three sources merged: TMDB, awards records, Wikipedia director bios.",
            "Sparse modalities preserved as one-hot (interpretable).",
            "Missing release date encoded as binary flag — turned out to be structurally relevant (slide 10).",
            "Director-bio reconstruction loss masked by has_director_bio flag (G2 masking).",
        ],
        left=Inches(0.5), top=Inches(2.25), width=Inches(7.0), height=Inches(4.5),
    )
    C.add_image(s, theme.FIG_EDA_DIR + "multilingual_coverage.png",
                left=Inches(7.7), top=Inches(2.05), width=Inches(5.2))
    cap = s.shapes.add_textbox(Inches(7.7), Inches(6.4), Inches(5.2), Inches(0.4))
    tfc = cap.text_frame
    pc = tfc.paragraphs[0]
    pc.alignment = PP_ALIGN.CENTER
    runc = pc.add_run()
    runc.text = "Multilingual coverage — long tail motivates sparsity-aware design."
    runc.font.name = theme.Fonts.BODY
    runc.font.size = theme.Sizes.CAPTION
    runc.font.italic = True
    runc.font.color.rgb = theme.Colors.SLATE


def slide_06_arch(prs):
    s = _content_slide(prs, 6, "Work Completed: Architecture Design",
                       "Multi-modal backbone, W2 inverse-variance loss, G2 bio masking, DEC head.")
    C.add_status_pill(s, "complete", left=Inches(0.5), top=Inches(1.55),
                      width=Inches(2.0), height=Inches(0.4))
    C.add_image(s, theme.FIG_DIAGRAM_DIR + "architecture_multimodal.png",
                left=Inches(0.6), top=Inches(2.1), width=Inches(8.5))
    C.add_bullets(s,
        items=[
            "7 modality projections → concat (164-dim) → backbone → z=64.",
            "W2: per-block inverse-variance weighting (clipped to [0.1, 10]).",
            "G2: mask bio reconstruction loss by has_director_bio.",
            "DEC head: Student-t soft assignment, k=21, γ=0.1 on KL.",
        ],
        left=Inches(9.4), top=Inches(2.25), width=Inches(3.5), height=Inches(4.5),
        font_size=Pt(15),
    )


def slide_07_mvp_table(prs):
    s = _content_slide(prs, 7, "Work Completed: Modeling MVP — Six Runs",
                       "Three tiers, six metrics, four different column winners.")
    C.add_status_pill(s, "complete", left=Inches(0.5), top=Inches(1.55),
                      width=Inches(2.0), height=Inches(0.4))
    C.add_table(s,
        header=["Run",                "gNMI", "gARI", "dNMI", "dARI", "lNMI", "lARI"],
        rows=[
            ["kmeans_raw_k21",         "0.109","0.063","0.233","0.093","0.075","0.026"],
            ["pca_kmeans_k21",         "0.084","0.061","0.224","0.085","0.094","0.042"],
            ["vanilla_ae_z64",         "0.287","0.247","0.369","0.175","0.095","0.030"],
            ["ae_z64_w1 (W1 ablation)","0.165","0.094","0.367","0.176","0.070","0.026"],
            ["ae_z64",                 "0.328","0.229","0.341","0.211","0.264","0.090"],
            ["dec_z64_k21 (BEST)",     "0.332","0.244","0.342","0.210","0.294","0.090"],
        ],
        left=Inches(0.5), top=Inches(2.25), width=Inches(12.333), height=Inches(4.0),
        col_aligns=["l", "r", "r", "r", "r", "r", "r"],
    )
    cap = s.shapes.add_textbox(Inches(0.5), Inches(6.5), Inches(12.333), Inches(0.4))
    tfc = cap.text_frame
    pc = tfc.paragraphs[0]
    pc.alignment = PP_ALIGN.CENTER
    runc = pc.add_run()
    runc.text = ("z = 64, KMeans k = 21. No model wins all six metrics — "
                 "the principled-trade-off result.")
    runc.font.name = theme.Fonts.BODY
    runc.font.size = theme.Sizes.CAPTION
    runc.font.italic = True
    runc.font.color.rgb = theme.Colors.SLATE
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

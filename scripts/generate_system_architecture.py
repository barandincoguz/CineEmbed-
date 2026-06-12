"""Render the high-level system architecture figure for CineEmbed.

Two horizontal lanes (offline training / online serving) with a central
artifact bundle bridging them, plus two dashed-line external dependencies
(Weights & Biases, TMDb API).

v2 — fixed title/external collision, widened bridge, simplified box text,
arrows realigned so labels stay legible.

Output: docs/final/deliverables/figures/system_architecture.png
"""

from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

ROOT = Path("/Users/barandincoguz/Desktop/deep learning movie project")
OUT_PATH = ROOT / "docs/final/deliverables/figures/system_architecture.png"
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

# ── Brand palette ────────────────────────────────────────────────────────
PURPLE      = "#6E56CF"
PURPLE_DARK = "#4C3AA1"
PURPLE_TINT = "#E7E0FA"
PURPLE_LANE = "#F3F0FB"
SLATE_LANE  = "#F4F7FB"
NEAR_BLACK  = "#0F172A"
NEAR_BLACK2 = "#1E293B"
SLATE       = "#475569"
SLATE_LIGHT = "#94A3B8"
ORANGE      = "#C2410C"
GREEN       = "#15803D"
WHITE       = "#FFFFFF"
BORDER      = "#E5E4EC"
GOLD        = "#B45309"
GOLD_FILL   = "#FEF3C7"

mpl.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 11,
    "axes.linewidth": 0.0,
    "savefig.dpi": 200,
    "savefig.facecolor": WHITE,
})


# ── Drawing helpers ──────────────────────────────────────────────────────

def add_box(ax, x, y, w, h, *, fill=WHITE, edge=BORDER, lw=1.2,
            radius=0.012, ls="solid"):
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0,rounding_size={radius}",
        linewidth=lw, edgecolor=edge, facecolor=fill, linestyle=ls,
    )
    ax.add_patch(box)
    return box


def add_arrow(ax, x1, y1, x2, y2, *, color=PURPLE, lw=1.8,
              ls="solid", mut=14, alpha=1.0, rad=0.0):
    arr = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle="-|>", mutation_scale=mut,
        color=color, lw=lw, linestyle=ls, alpha=alpha,
        shrinkA=3, shrinkB=3,
        connectionstyle=f"arc3,rad={rad}" if rad != 0 else "arc3",
    )
    ax.add_patch(arr)


def add_lane_bg(ax, x, y, w, h, color):
    rect = Rectangle((x, y), w, h, facecolor=color, edgecolor="none",
                     zorder=0)
    ax.add_patch(rect)


def draw_box_label(ax, x, y, w, h, *, title, sub, tech, accent):
    """Box with accent stripe, title, italic body, monospace tech tag.

    Layout off-centre so the box mid-line stays clear for inter-box arrows.
      top 35 %  → title  (y + h*0.78)
      upper-mid → body   (y + h*0.60)
      lower     → tech   (y + h*0.18)
    """
    add_box(ax, x, y, w, h, fill=WHITE, edge=accent, lw=1.6, radius=0.012)
    add_box(ax, x, y, 0.008, h, fill=accent, edge=accent, lw=0, radius=0.0)

    cx = x + w / 2 + 0.004
    # Title (top)
    ax.text(cx, y + h * 0.82, title, ha="center", va="center",
            fontsize=12.5, fontweight="bold", color=NEAR_BLACK)
    # Body (upper mid) — above arrow mid-line so flow arrows don't cross it
    ax.text(cx, y + h * 0.60, sub, ha="center", va="center",
            fontsize=9.5, color=NEAR_BLACK2, style="italic",
            linespacing=1.15)
    # Tech (bottom)
    ax.text(cx, y + h * 0.16, tech, ha="center", va="center",
            fontsize=8.5, color=accent, family="monospace",
            fontweight="bold")


# ── Figure ───────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(13.33, 7.5))
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")

# Lane background bands — leave right margin for external boxes
add_lane_bg(ax, 0.03, 0.66, 0.79, 0.22, PURPLE_LANE)   # offline
add_lane_bg(ax, 0.03, 0.12, 0.79, 0.22, SLATE_LANE)    # online

# Figure title / subtitle are intentionally omitted — slide title bar
# above the embedded figure already names this view.
# Lane labels positioned ABOVE the lane background so they don't collide
# with the first box title.
ax.text(0.04, 0.905, "OFFLINE  ·  TRAINING",
        ha="left", va="center", fontsize=11, fontweight="bold",
        color=PURPLE_DARK, family="monospace")
ax.text(0.04, 0.355, "ONLINE  ·  SERVING",
        ha="left", va="center", fontsize=11, fontweight="bold",
        color=PURPLE_DARK, family="monospace")

# ── OFFLINE LANE — 4 boxes, comfortable gaps ────────────────────────────
ow = 0.16; oh = 0.155
oy = 0.685
# 4 boxes × 0.16 + 3 gaps × 0.026 = 0.64 + 0.078 = 0.718. Start at 0.07.
ox_starts = [0.07, 0.256, 0.442, 0.628]   # centres: 0.15, 0.336, 0.522, 0.708

offline_boxes = [
    ("Data Sources",     "TMDb dump",
     "TMDb · 329K films",              PURPLE),
    ("Feature Pipeline", "7 modality blocks\n→ 564-d matrix",
     "pandas · sklearn",               PURPLE),
    ("Encoder Training", "multi-modal AE",
     "PyTorch · Colab",                PURPLE),
    ("Index Builder",    "encode + KMeans",
     "L2-norm · k=21",                 PURPLE),
]
for x, (t, s, tech, c) in zip(ox_starts, offline_boxes):
    draw_box_label(ax, x, oy, ow, oh, title=t, sub=s, tech=tech, accent=c)

# Arrows between offline boxes — at lower mid-line to clear body text above
for i in range(3):
    x1 = ox_starts[i] + ow
    x2 = ox_starts[i + 1]
    y_arr = oy + oh * 0.38   # below body, above tech
    add_arrow(ax, x1 + 0.003, y_arr, x2 - 0.003, y_arr,
              color=PURPLE_DARK, lw=2.0, mut=14)

# ── BRIDGE — Inference Artifact Bundle (wide band between lanes) ────────
bx = 0.07; bw = 0.72; by = 0.485; bh = 0.115

add_box(ax, bx, by, bw, bh, fill=GOLD_FILL, edge=GOLD, lw=2.0,
        radius=0.012)
# Top ribbon (gold band)
add_box(ax, bx, by + bh - 0.026, bw, 0.026, fill=GOLD, edge=GOLD,
        lw=0, radius=0.0)
# Left-aligned title (leaves right side clear for arrow landings)
ax.text(bx + 0.020, by + bh - 0.013, "INFERENCE ARTIFACT BUNDLE",
        ha="left", va="center", fontsize=11.5, fontweight="bold",
        color=WHITE)
ax.text(bx + 0.020, by + bh / 2,
        "embeddings.npy  ·  cluster labels  ·  films master",
        ha="left", va="center", fontsize=11, color=NEAR_BLACK,
        style="italic")
ax.text(bx + 0.020, by + 0.014,
        "mmap-ready · 42 MB · written by Index Builder, "
        "read at FastAPI startup",
        ha="left", va="center", fontsize=8.8, color=GOLD,
        family="monospace", fontweight="bold")

# Vertical arrows: Index Builder (offline last) drops INTO bridge top.
# Online AI Engine (last) is fed FROM bridge bottom.
idx_cx = ox_starts[3] + ow / 2        # Index Builder centre
add_arrow(ax, idx_cx, oy, idx_cx, by + bh,
          color=GOLD, lw=2.4, mut=18)

# ── ONLINE LANE — 5 boxes, real gaps ────────────────────────────────────
nw = 0.125; nh = 0.155
ny = 0.155
# 5 boxes × 0.125 + 4 gaps × 0.024 = 0.625 + 0.096 = 0.721. Start at 0.07.
# Final centres (each 0.149 apart):
nx_centres = [0.1325, 0.2815, 0.4305, 0.5795, 0.7285]
nx_starts  = [c - nw / 2 for c in nx_centres]

# READ arrow from bridge bottom → AI Engine top (last online box, centre 0.7285)
ai_cx = nx_centres[4]
add_arrow(ax, ai_cx, by, ai_cx, ny + nh,
          color=GOLD, lw=2.4, mut=18)

online_boxes = [
    ("User",             "browser",
     "HTTP",                          SLATE),
    ("Frontend",         "web client",
     "Next.js 16",                    GREEN),
    ("API",              "REST endpoints",
     "FastAPI",                       ORANGE),
    ("Backend",          "search + cache",
     "NumPy BLAS",                    PURPLE),
    ("AI Engine",        "encoder + index",
     "PyTorch",                       PURPLE_DARK),
]
for x, (t, sub, tech, c) in zip(nx_starts, online_boxes):
    draw_box_label(ax, x, ny, nw, nh, title=t, sub=sub, tech=tech, accent=c)

# Arrows between online boxes — at lower mid-line, below body text
for i in range(4):
    x1 = nx_starts[i] + nw
    x2 = nx_starts[i + 1]
    y_arr = ny + nh * 0.38
    add_arrow(ax, x1 + 0.003, y_arr, x2 - 0.003, y_arr,
              color=PURPLE_DARK, lw=2.0, mut=14)

# Return arrow (response: AI Engine → User), curved below row
ret_y = ny - 0.020
arr_back = FancyArrowPatch(
    (nx_centres[4], ret_y),
    (nx_centres[0], ret_y),
    arrowstyle="-|>", mutation_scale=12,
    color=SLATE, lw=1.3, linestyle=(0, (5, 3)),
    connectionstyle="arc3,rad=0.20",
    shrinkA=4, shrinkB=4,
)
ax.add_patch(arr_back)
ax.text(0.45, ret_y - 0.048,
        "top-5 cosine JSON  ·  end-to-end < 5 ms",
        ha="center", va="top", fontsize=9.5, color=SLATE,
        style="italic")

# ── EXTERNALS — positioned OUTSIDE the lane areas so connector arrows
# don't have to cross through intermediate boxes.

# Weights & Biases: top-right corner ABOVE the offline lane background.
wbx = 0.825; wby = 0.895; wbw = 0.160; wbh = 0.085
add_box(ax, wbx, wby, wbw, wbh, fill=WHITE, edge=SLATE, lw=1.3,
        radius=0.010, ls=(0, (4, 3)))
ax.text(wbx + wbw / 2, wby + wbh * 0.68, "Weights & Biases",
        ha="center", va="center", fontsize=10.5, fontweight="bold",
        color=NEAR_BLACK)
ax.text(wbx + wbw / 2, wby + wbh * 0.32,
        "training logs · sweeps",
        ha="center", va="center", fontsize=9, color=SLATE,
        style="italic")
# Arrow drops DOWN-LEFT from W&B left edge to Encoder Training top.
# Both endpoints sit above the offline boxes — line never crosses them.
add_arrow(ax,
          wbx, wby + wbh * 0.5,
          ox_starts[2] + ow * 0.7, oy + oh,
          color=SLATE, lw=1.4, mut=11, ls=(0, (5, 3)), alpha=0.85,
          rad=0.25)

# TMDb API: bottom-right corner BELOW the online lane background.
tmx = 0.825; tmy = 0.020; tmw = 0.160; tmh = 0.085
add_box(ax, tmx, tmy, tmw, tmh, fill=WHITE, edge=SLATE, lw=1.3,
        radius=0.010, ls=(0, (4, 3)))
ax.text(tmx + tmw / 2, tmy + tmh * 0.68, "TMDb API",
        ha="center", va="center", fontsize=10.5, fontweight="bold",
        color=NEAR_BLACK)
ax.text(tmx + tmw / 2, tmy + tmh * 0.32,
        "poster proxy (online)",
        ha="center", va="center", fontsize=9, color=SLATE,
        style="italic")
# Single arrow UP from TMDb to Backend bottom — short, doesn't cross other boxes.
add_arrow(ax,
          tmx, tmy + tmh * 0.5,
          nx_centres[3] + 0.020, ny,
          color=SLATE, lw=1.4, mut=11, ls=(0, (5, 3)), alpha=0.85,
          rad=-0.25)
# Tiny inline note on TMDb's offline role (avoids needing a cross-figure arrow)
ax.text(tmx + tmw / 2, tmy - 0.020,
        "(offline: enrichment of Data Sources)",
        ha="center", va="top", fontsize=7.5, color=SLATE_LIGHT,
        style="italic")

# ── Legend (bottom-left, compact) ───────────────────────────────────────
leg_y = 0.055
# Solid arrow
add_arrow(ax, 0.04, leg_y, 0.075, leg_y,
          color=PURPLE_DARK, lw=2.0, mut=12)
ax.text(0.08, leg_y, "data flow",
        ha="left", va="center", fontsize=9, color=NEAR_BLACK2)
# Dashed
add_arrow(ax, 0.205, leg_y, 0.240, leg_y,
          color=SLATE, lw=1.3, mut=10, ls=(0, (5, 3)))
ax.text(0.245, leg_y, "external dependency",
        ha="left", va="center", fontsize=9, color=NEAR_BLACK2)
# Gold swatch
ax.add_patch(Rectangle((0.46, leg_y - 0.008), 0.020, 0.016,
                       facecolor=GOLD, edgecolor=GOLD, lw=0))
ax.text(0.485, leg_y, "artifact bundle (offline → online bridge)",
        ha="left", va="center", fontsize=9, color=NEAR_BLACK2)

# ── Save ─────────────────────────────────────────────────────────────────
plt.savefig(OUT_PATH, bbox_inches="tight", pad_inches=0.08,
            facecolor=WHITE)
plt.close(fig)
print(f"saved {OUT_PATH}")

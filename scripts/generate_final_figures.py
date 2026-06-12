"""Generate the four critical missing figures for the final report.

Figures produced (in docs/final/deliverables/figures/):
  - zsweep_ucurve.png             Round 2 z-sweep U-curve (TG-1)
  - cosine_collapse_histogram.png AE vs DEC top-5 cosine distributions (TG-2)
  - dim_std_per_backbone.png      Per-dim std bars across z=32/64/128 (TG-3)
  - training_curves.png           ae_z32 vs ae_z128 train/val loss (TG-6)

All data already on-disk. No retraining, no re-inference.

v2 (2026-05-19 PM): larger projector-scale fonts (titles 18pt, axes 14pt,
ticks 12pt, legends 12pt). tight_layout with bbox_inches='tight' for clean
crops. Re-rendered after QA feedback that figures were unreadable at slide
scale.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path("/Users/barandincoguz/Desktop/deep learning movie project")
OUT = ROOT / "docs/final/deliverables/figures"
OUT.mkdir(parents=True, exist_ok=True)

# Projector-friendly defaults (applied to every figure unless overridden)
mpl.rcParams.update({
    "font.size": 13,
    "axes.titlesize": 17,
    "axes.labelsize": 14,
    "xtick.labelsize": 12,
    "ytick.labelsize": 12,
    "legend.fontsize": 12,
    "figure.titlesize": 18,
    "axes.linewidth": 1.0,
    "axes.titleweight": "bold",
    "axes.spines.top": False,
    "axes.spines.right": False,
})

BRAND_ORANGE = "#C2410C"
BRAND_BLUE = "#2563EB"
BRAND_GREEN = "#15803D"
BRAND_AMBER = "#B45309"
BRAND_SLATE = "#64748B"
NEAR_BLACK = "#1E293B"


# ----------------------------------------------------------------------------
# TG-1 — Round 2 z-sweep U-curve (information-bottleneck sweet spot)
# ----------------------------------------------------------------------------

def fig_zsweep_ucurve() -> Path:
    zs = [32, 64, 128]
    gnmi = [0.334, 0.328, 0.273]
    genre5 = [0.723, 0.715, 0.722]
    dim_std_min = [0.117, 0.062, 0.025]

    fig, ax1 = plt.subplots(figsize=(8.0, 4.6))
    ax1.set_xlabel("Latent dimension $z$", fontsize=15)
    ax1.set_ylabel("Quality metric (gNMI, genre@5)", fontsize=14)
    ax1.plot(zs, gnmi, "o-", color=BRAND_ORANGE, lw=2.6, markersize=12,
             label="gNMI (KMeans k=21)")
    ax1.plot(zs, genre5, "s-", color=BRAND_BLUE, lw=2.6, markersize=11,
             label="genre@5 (cosine retrieval)")
    ax1.scatter([32], [0.334], s=320, facecolors="none", edgecolors=BRAND_ORANGE,
                lw=3.0, zorder=4)
    ax1.annotate("winning z", xy=(32, 0.334), xytext=(50, 0.45),
                 arrowprops=dict(arrowstyle="->", color=NEAR_BLACK, lw=1.4),
                 fontsize=13, fontweight="bold", color=NEAR_BLACK)
    ax1.set_xticks(zs)
    ax1.set_xticklabels([f"z={z}\n{42 if z==32 else 84 if z==64 else 168} MB" for z in zs],
                        fontsize=12)
    ax1.set_ylim(0.20, 0.80)
    ax1.legend(loc="upper left", fontsize=12, frameon=True, framealpha=0.95)
    ax1.set_title("Round 2 — U-curve: $z=32$ wins on quality and size", pad=12)
    ax1.grid(alpha=0.30, linestyle="--")

    ax2 = ax1.twinx()
    ax2.plot(zs, dim_std_min, "^--", color=BRAND_SLATE, lw=1.9, markersize=12,
             label="dim_std_min")
    ax2.set_ylabel("dim_std_min (smallest latent-dim std)",
                   color=BRAND_SLATE, fontsize=13)
    ax2.tick_params(axis="y", colors=BRAND_SLATE, labelsize=12)
    ax2.set_ylim(0.0, 0.20)
    ax2.legend(loc="upper right", fontsize=12, frameon=True, framealpha=0.95)
    ax2.spines["top"].set_visible(False)

    ax1.annotate("gNMI collapses\nnear-dead dim",
                 xy=(128, 0.273), xytext=(90, 0.36),
                 arrowprops=dict(arrowstyle="->", color=BRAND_ORANGE, lw=1.3),
                 fontsize=12, color=NEAR_BLACK)

    fig.tight_layout()
    path = OUT / "zsweep_ucurve.png"
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


# ----------------------------------------------------------------------------
# TG-2 — Top-5 neighbour cosine spread: ae_z32 (healthy) vs dec_z64_k21 (collapse)
# ----------------------------------------------------------------------------

def fig_cosine_collapse() -> Path:
    rng = np.random.default_rng(42)
    N_QUERIES = 400
    K = 5

    def sample_topk(emb_path: Path) -> np.ndarray:
        emb = np.load(emb_path).astype(np.float32)
        n = emb.shape[0]
        idxs = rng.choice(n, N_QUERIES, replace=False)
        tops: list[float] = []
        for qi in idxs:
            sims = emb @ emb[qi]
            sims[qi] = -2.0
            top = np.partition(sims, -K)[-K:]
            tops.extend(top.tolist())
        return np.asarray(tops)

    print("[TG-2] sampling ae_z32 top-5 cosines …")
    ae_top = sample_topk(ROOT / "artifacts/inference/ae_z32/embeddings.npy")
    print("[TG-2] sampling dec_z64_k21 top-5 cosines …")
    dec_top = sample_topk(ROOT / "artifacts/inference/dec_z64_k21/embeddings.npy")

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.7), sharey=False)

    axes[0].hist(ae_top, bins=45, range=(0.5, 1.0), color=BRAND_BLUE,
                 alpha=0.88, edgecolor="white", linewidth=0.4)
    axes[0].set_title("ae_z32 — healthy retrieval geometry", fontsize=15)
    axes[0].set_xlabel(f"top-{K} neighbour cosine "
                       f"({N_QUERIES} random queries × {K} neighbours)",
                       fontsize=13)
    axes[0].set_ylabel("count", fontsize=13)
    axes[0].axvline(np.median(ae_top), color=NEAR_BLACK, lw=1.6, ls="--",
                    alpha=0.8,
                    label=f"median = {np.median(ae_top):.3f}")
    axes[0].axvline(np.mean(ae_top), color=BRAND_ORANGE, lw=1.6, ls=":",
                    alpha=0.9,
                    label=f"mean = {np.mean(ae_top):.3f}")
    axes[0].set_xlim(0.5, 1.0)
    axes[0].legend(loc="upper left", fontsize=12)
    axes[0].grid(alpha=0.30, axis="y")

    axes[1].hist(dec_top, bins=45, range=(0.5, 1.0), color=BRAND_ORANGE,
                 alpha=0.88, edgecolor="white", linewidth=0.4)
    axes[1].set_title("dec_z64_k21 — angular collapse", fontsize=15)
    axes[1].set_xlabel(f"top-{K} neighbour cosine "
                       f"({N_QUERIES} random queries × {K} neighbours)",
                       fontsize=13)
    axes[1].axvline(np.median(dec_top), color=NEAR_BLACK, lw=1.6, ls="--",
                    alpha=0.8,
                    label=f"median = {np.median(dec_top):.4f}")
    axes[1].axvline(np.mean(dec_top), color=BRAND_BLUE, lw=1.6, ls=":",
                    alpha=0.9,
                    label=f"mean = {np.mean(dec_top):.4f}")
    axes[1].set_xlim(0.5, 1.0)
    axes[1].legend(loc="upper left", fontsize=12)
    axes[1].grid(alpha=0.30, axis="y")

    fig.suptitle("NMI ≠ retrieval — DEC's top-5 cosines saturate ≈ 1.000",
                 fontsize=17, fontweight="bold", y=1.03)
    fig.tight_layout()
    path = OUT / "cosine_collapse_histogram.png"
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  ae_z32 top-5 cosine:  mean={ae_top.mean():.4f}  "
          f"median={np.median(ae_top):.4f}  min={ae_top.min():.4f}")
    print(f"  dec     top-5 cosine: mean={dec_top.mean():.4f}  "
          f"median={np.median(dec_top):.4f}  min={dec_top.min():.4f}")
    return path


# ----------------------------------------------------------------------------
# TG-3 — Per-dimension standard deviation across z=32 / 64 / 128
# ----------------------------------------------------------------------------

def fig_dim_std_bars() -> Path:
    paths = {
        32: ROOT / "artifacts/inference/ae_z32/embeddings.npy",
        64: ROOT / "artifacts/inference/ae_z64/embeddings.npy",
        128: ROOT / "artifacts/inference/ae_z128/embeddings.npy",
    }
    stds: dict[int, np.ndarray] = {}
    for z, p in paths.items():
        print(f"[TG-3] loading ae_z{z} …")
        emb = np.load(p)
        stds[z] = np.std(emb, axis=0)
        del emb

    colors = {32: BRAND_GREEN, 64: BRAND_BLUE, 128: BRAND_ORANGE}
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.7), sharey=True)
    for ax, (z, s) in zip(axes, stds.items()):
        sorted_s = np.sort(s)[::-1]
        ax.bar(range(z), sorted_s, color=colors[z], width=0.92,
               edgecolor="white", linewidth=0.4)
        ax.axhline(s.min(), color=NEAR_BLACK, ls="--", lw=1.2, alpha=0.7,
                   label=f"dim_std_min = {s.min():.3f}")
        ax.axhline(s.mean(), color=BRAND_AMBER, ls=":", lw=1.2, alpha=0.8,
                   label=f"dim_std_mean = {s.mean():.3f}")
        ax.set_title(f"ae_z{z}", fontsize=15)
        ax.set_xlabel("latent dimension (sorted)", fontsize=13)
        ax.legend(loc="upper right", fontsize=11)
        ax.grid(alpha=0.30, axis="y")

    axes[0].set_ylabel("std across 329,044 films", fontsize=13)
    fig.suptitle("Per-dimension activation spread — z=128 has near-dead dimensions",
                 fontsize=17, fontweight="bold", y=1.03)
    fig.tight_layout()
    path = OUT / "dim_std_per_backbone.png"
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


# ----------------------------------------------------------------------------
# TG-6 — Training curves for ae_z32 vs ae_z128
# ----------------------------------------------------------------------------

def fig_training_curves() -> Path:
    h32 = json.loads((ROOT / "artifacts/models/ae_z32/history.json").read_text())
    h128 = json.loads((ROOT / "artifacts/models/ae_z128/history.json").read_text())

    fig, ax = plt.subplots(figsize=(8.0, 4.7))
    ax.plot(h32["train_loss"], color=BRAND_GREEN, lw=1.3, alpha=0.55,
            label=f"ae_z32 train ({h32['n_epochs_completed']} epochs)")
    ax.plot(h32["val_loss"], color=BRAND_GREEN, lw=2.4,
            label=f"ae_z32 val (final {h32['final_val_loss']:.4f})")
    ax.plot(h128["train_loss"], color=BRAND_ORANGE, lw=1.3, alpha=0.55,
            label=f"ae_z128 train ({h128['n_epochs_completed']} epochs)")
    ax.plot(h128["val_loss"], color=BRAND_ORANGE, lw=2.4,
            label=f"ae_z128 val (final {h128['final_val_loss']:.4f})")
    ax.set_xlabel("epoch", fontsize=14)
    ax.set_ylabel("loss  (W2 weighted MSE)", fontsize=14)
    ax.set_yscale("log")
    ax.set_title("Training curves — both backbones converge cleanly", pad=12)
    ax.legend(loc="upper right", fontsize=12)
    ax.grid(alpha=0.30, which="both")
    fig.tight_layout()
    path = OUT / "training_curves.png"
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


# ----------------------------------------------------------------------------

def main() -> None:
    print("→", fig_zsweep_ucurve())
    print("→", fig_training_curves())
    print("→", fig_dim_std_bars())
    print("→", fig_cosine_collapse())
    print("done.")


if __name__ == "__main__":
    main()

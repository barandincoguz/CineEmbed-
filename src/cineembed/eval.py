"""Evaluation helpers for AE/VAE/DEC runs (spec §8)."""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use('Agg')  # non-interactive backend for headless / Colab
import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score


def cluster_assignments_kmeans(z: np.ndarray, k: int, seed: int = 42) -> np.ndarray:
    """Run KMeans(k) on latent vectors → cluster ids."""
    km = KMeans(n_clusters=k, n_init=20, random_state=seed)  # type: ignore[arg-type]
    return km.fit_predict(z).astype(np.int64)


def cluster_assignments_dec(model, batches: list[dict], device: str = 'cpu') -> np.ndarray:
    """Argmax over DEC soft assignments (q) across all batches."""
    model.eval()
    chunks = []
    with torch.no_grad():
        for batch in batches:
            blocks = {b: t.to(device) for b, t in batch['blocks'].items()}
            _, _, q = model(blocks)
            chunks.append(q.argmax(dim=1).cpu().numpy())
    return np.concatenate(chunks).astype(np.int64)


def evaluate_run(
    cluster_ids: np.ndarray,
    labels: dict[str, np.ndarray],
) -> dict[str, float]:
    """Compute NMI and ARI vs each label axis (spec §8.1)."""
    out = {}
    axis_aliases = {'genre': 'primary_genre', 'decade': 'decade_bin', 'lang': 'lang_top10'}
    for short, full in axis_aliases.items():
        labs = labels[full]
        out[f'{short}_nmi'] = float(normalized_mutual_info_score(labs, cluster_ids))
        out[f'{short}_ari'] = float(adjusted_rand_score(labs, cluster_ids))
    return out


def linear_probe(
    z: np.ndarray,
    labels: np.ndarray,
    *,
    train_idx: np.ndarray,
    val_idx: np.ndarray,
    n_classes: int,
    n_epochs: int = 20,
    lr: float = 1e-3,
    seed: int = 42,
    device: str = 'cpu',
) -> dict[str, float]:
    """Train a linear classifier on frozen z and report val accuracy (spec §8.3.1)."""
    torch.manual_seed(seed)
    z_t = torch.from_numpy(z).float().to(device)
    y_t = torch.from_numpy(np.asarray(labels)).long().to(device)
    model = nn.Linear(z.shape[1], n_classes).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=lr)

    train_idx_t = torch.from_numpy(train_idx).long()
    val_idx_t = torch.from_numpy(val_idx).long()

    for _ in range(n_epochs):
        model.train()
        logits = model(z_t[train_idx_t])
        loss = nn.functional.cross_entropy(logits, y_t[train_idx_t])
        opt.zero_grad()
        loss.backward()
        opt.step()

    model.eval()
    with torch.no_grad():
        val_logits = model(z_t[val_idx_t])
        val_acc = (val_logits.argmax(dim=1) == y_t[val_idx_t]).float().mean().item()
    return {'val_accuracy': val_acc}


def umap_plot(
    z: np.ndarray,
    labels: np.ndarray,
    *,
    title: str,
    savepath: str | Path,
    seed: int = 42,
    n_neighbors: int = 15,
    min_dist: float = 0.1,
) -> None:
    """2D UMAP scatter colored by labels, saved to disk (spec §8.2)."""
    import umap  # type: ignore[import]
    reducer = umap.UMAP(n_neighbors=n_neighbors, min_dist=min_dist,
                        n_components=2, random_state=seed)
    z2d = reducer.fit_transform(z)

    fig, ax = plt.subplots(figsize=(10, 7))
    unique = np.unique(labels)
    cmap = plt.get_cmap('tab20', len(unique))
    for i, cls in enumerate(unique):
        mask = labels == cls
        ax.scatter(z2d[mask, 0], z2d[mask, 1], s=8, alpha=0.55,
                   color=cmap(i), label=f'{cls} ({mask.sum()})')
    ax.set_title(title)
    ax.legend(markerscale=2, fontsize=7, loc='best', ncol=2)
    Path(savepath).parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(savepath, dpi=120, bbox_inches='tight')
    plt.close(fig)

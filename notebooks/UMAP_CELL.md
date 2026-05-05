# UMAP Cell — All Models, All Axes

**Drop-in tek hücre.** Colab'da `06_umap.ipynb` (yeni notebook) açıp setup hücresi (00'daki gibi mount + clone + pip install) sonrasında bu hücreyi çalıştır. Tahmini süre: **~6-8 dk** (4 model × 1 UMAP each + 12 plot kaydı).

Çıktı: `MyDrive/CineEmbed/artifacts/figures/umap/` altında **13 PNG** (4 model × 3 eksen + 1 comparison panel).

---

```python
# ============================================================
# UMAP visualizations for CineEmbed MVP — all 4 models, 3 axes
# ============================================================
import time, json
import numpy as np
import torch
import torch.nn as nn
import matplotlib.pyplot as plt
from pathlib import Path
import umap

from cineembed import data, backbone, heads, train

DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
ARTIFACTS = Path('/content/drive/MyDrive/CineEmbed/artifacts')
MODELS_DIR = ARTIFACTS / 'models'
FIGS_DIR = ARTIFACTS / 'figures' / 'umap'
FIGS_DIR.mkdir(parents=True, exist_ok=True)

# Load full data + labels
print(f"[{time.strftime('%H:%M:%S')}] loading feature matrix + labels...")
X, feature_names = data.load_feature_matrix(ARTIFACTS / 'feature_matrix.npz')
block_slices = data.get_block_indices(feature_names)
labels_full = data.get_labels(ARTIFACTS / 'movies_eda_final.csv')

# has_bio extracted from director block
has_bio = X[:, feature_names.index('has_director_bio')]

# Block dims for model reconstruction
BLOCK_DIMS = {b: slc.stop - slc.start for b, slc in block_slices.items()}
PROJ_DIMS = {'numerical': 6, 'genre': 22, 'language': 16, 'decade': 2,
             'awards': 6, 'text': 96, 'director': 56}

# Subsample for UMAP speed (15K is plenty for visual)
N_VIS = 15000
rng = np.random.default_rng(42)
vis_idx = rng.choice(X.shape[0], size=N_VIS, replace=False)
print(f"[{time.strftime('%H:%M:%S')}] visualizing {N_VIS:,} films (of {X.shape[0]:,})")

# Subsample labels once
labels_vis = {k: v[vis_idx] for k, v in labels_full.items()}

# ============================================================
# Model builders — match notebooks/02_train_ae and 04_train_dec
# ============================================================
def build_ae_model(z_dim, vanilla=False):
    if vanilla:
        bb_fc = nn.Sequential(
            nn.Linear(564, 128), nn.ReLU(), nn.Dropout(0.2), nn.Linear(128, z_dim),
        )
        class _VanillaWrap(nn.Module):
            def __init__(self, fc, z_dim_):
                super().__init__()
                self.fc = fc
                self.latent_dim = z_dim_
                self.block_order = list(BLOCK_DIMS.keys())
            def forward(self, blocks, block_mask=None):
                X_cat = torch.cat([blocks[b] for b in self.block_order], dim=1)
                return self.fc(X_cat)
        bb = _VanillaWrap(bb_fc, z_dim)
    else:
        bb = backbone.MultiModalBackbone(BLOCK_DIMS, PROJ_DIMS, hidden_dim=128, latent_dim=z_dim)
    return heads.AEHead(bb, BLOCK_DIMS, PROJ_DIMS, hidden_dim=128)

def build_dec_model(z_dim, k):
    bb = backbone.MultiModalBackbone(BLOCK_DIMS, PROJ_DIMS, hidden_dim=128, latent_dim=z_dim)
    ae_head = heads.AEHead(bb, BLOCK_DIMS, PROJ_DIMS, hidden_dim=128)
    return heads.DECHead(bb, ae_head.decoder, n_clusters=k, latent_dim=z_dim)

# ============================================================
# Encode helper (subsample)
# ============================================================
def encode_subsample(model, X, has_bio, vis_idx, block_slices, batch_size=2048):
    model.eval()
    X_sub = X[vis_idx]
    has_bio_sub = has_bio[vis_idx]
    z_all = []
    with torch.no_grad():
        for i in range(0, len(vis_idx), batch_size):
            xb = X_sub[i:i+batch_size].to(DEVICE)
            blocks = {b: xb[:, slc] for b, slc in block_slices.items()}
            z = model.backbone(blocks) if hasattr(model, 'backbone') else model.encode(blocks)
            z_all.append(z.cpu().numpy())
    return np.concatenate(z_all, axis=0)

# ============================================================
# Plot helper
# ============================================================
def plot_umap(z2d, labels, title, savepath, top_n=12, figsize=(9, 7)):
    """UMAP scatter colored by `labels`. Caps to top_n categories + 'Other'."""
    labels = np.asarray(labels).astype(str)
    counts = {}
    for v in labels:
        counts[v] = counts.get(v, 0) + 1
    top = sorted(counts, key=counts.get, reverse=True)[:top_n]
    plot_labels = np.where(np.isin(labels, top), labels, 'Other')

    fig, ax = plt.subplots(figsize=figsize)
    cmap = plt.cm.get_cmap('tab20', len(top) + 1)
    palette = {k: cmap(i) for i, k in enumerate(top + ['Other'])}

    # plot 'Other' first (gray), then named on top
    if 'Other' in set(plot_labels):
        m = plot_labels == 'Other'
        ax.scatter(z2d[m, 0], z2d[m, 1], s=2, c=[(0.7, 0.7, 0.7, 0.3)], label=f'Other ({m.sum()})')
    for k in top:
        m = plot_labels == k
        ax.scatter(z2d[m, 0], z2d[m, 1], s=3, color=palette[k], alpha=0.7, label=f'{k} ({m.sum()})')

    ax.set_title(title, fontsize=13)
    ax.set_xlabel('UMAP-1'); ax.set_ylabel('UMAP-2')
    ax.legend(loc='center left', bbox_to_anchor=(1.02, 0.5), fontsize=8, markerscale=3)
    ax.set_xticks([]); ax.set_yticks([])
    plt.tight_layout()
    plt.savefig(savepath, dpi=120, bbox_inches='tight')
    plt.close()
    print(f"  saved: {savepath.name}")

# ============================================================
# Run UMAP for each model
# ============================================================
runs = [
    ('vanilla_ae_z64',  lambda: build_ae_model(64, vanilla=True)),
    ('ae_z64',          lambda: build_ae_model(64, vanilla=False)),
    ('ae_z64_w1',       lambda: build_ae_model(64, vanilla=False)),
    ('dec_z64_k21',     lambda: build_dec_model(64, 21)),
]

z2d_cache = {}  # store 2D projections for the comparison panel

for run_name, model_builder in runs:
    print(f"\n[{time.strftime('%H:%M:%S')}] === {run_name} ===")
    ckpt = MODELS_DIR / f'{run_name}.pt'
    if not ckpt.exists():
        print(f"  SKIP — checkpoint missing: {ckpt}")
        continue

    model = model_builder().to(DEVICE)
    train.load_checkpoint(model, ckpt, device=DEVICE)

    print(f"  encoding {N_VIS:,} films...")
    t0 = time.time()
    z = encode_subsample(model, X, has_bio, vis_idx, block_slices)
    print(f"    encoded in {time.time()-t0:.1f}s, z.shape={z.shape}")

    print(f"  computing UMAP...")
    t0 = time.time()
    reducer = umap.UMAP(n_neighbors=30, min_dist=0.1, metric='cosine', random_state=42)
    z2d = reducer.fit_transform(z)
    print(f"    UMAP done in {time.time()-t0:.1f}s")
    z2d_cache[run_name] = z2d

    # Three plots per model
    for axis_name, label_key in [('genre', 'primary_genre'), ('decade', 'decade_bin'), ('lang', 'lang_top10')]:
        plot_umap(
            z2d, labels_vis[label_key],
            title=f'{run_name} — colored by {axis_name}',
            savepath=FIGS_DIR / f'umap_{run_name}_{axis_name}.png',
        )

# ============================================================
# Comparison panel: vanilla vs multi-modal vs DEC, colored by genre
# ============================================================
print(f"\n[{time.strftime('%H:%M:%S')}] === Comparison panel (genre) ===")
panel_runs = [r for r in ['vanilla_ae_z64', 'ae_z64', 'dec_z64_k21'] if r in z2d_cache]
if len(panel_runs) >= 2:
    fig, axes = plt.subplots(1, len(panel_runs), figsize=(7 * len(panel_runs), 6))
    if len(panel_runs) == 1:
        axes = [axes]
    genre_vis = labels_vis['primary_genre']
    counts = {v: int((genre_vis == v).sum()) for v in np.unique(genre_vis)}
    top = sorted(counts, key=counts.get, reverse=True)[:12]
    cmap = plt.cm.get_cmap('tab20', 13)
    palette = {k: cmap(i) for i, k in enumerate(top + ['Other'])}
    plot_labels = np.where(np.isin(genre_vis, top), genre_vis, 'Other')

    for ax, run_name in zip(axes, panel_runs):
        z2d = z2d_cache[run_name]
        m_other = plot_labels == 'Other'
        ax.scatter(z2d[m_other, 0], z2d[m_other, 1], s=2, c=[(0.7, 0.7, 0.7, 0.3)])
        for k in top:
            m = plot_labels == k
            ax.scatter(z2d[m, 0], z2d[m, 1], s=3, color=palette[k], alpha=0.7, label=k)
        ax.set_title(run_name, fontsize=12)
        ax.set_xticks([]); ax.set_yticks([])

    handles, labels_ = axes[-1].get_legend_handles_labels()
    fig.legend(handles, labels_, loc='center right', bbox_to_anchor=(1.08, 0.5),
               fontsize=9, markerscale=3)
    fig.suptitle('Architecture comparison — UMAP latent, colored by primary_genre', fontsize=14)
    plt.tight_layout()
    panel_path = FIGS_DIR / 'umap_comparison_genre.png'
    plt.savefig(panel_path, dpi=120, bbox_inches='tight')
    plt.close()
    print(f"  saved: {panel_path.name}")

print(f"\n[{time.strftime('%H:%M:%S')}] DONE — figures in {FIGS_DIR}")
print(f"  total files: {len(list(FIGS_DIR.glob('*.png')))}")
```

---

## Çıktı dosyaları

`MyDrive/CineEmbed/artifacts/figures/umap/` altında:

```
umap_vanilla_ae_z64_genre.png
umap_vanilla_ae_z64_decade.png
umap_vanilla_ae_z64_lang.png
umap_ae_z64_genre.png            ← rapor için altın
umap_ae_z64_decade.png
umap_ae_z64_lang.png             ← lang ayrımı net görünür
umap_ae_z64_w1_genre.png         ← W1 collapse görsel kanıtı
umap_ae_z64_w1_decade.png
umap_ae_z64_w1_lang.png
umap_dec_z64_k21_genre.png       ← rapor için altın (en iyi model)
umap_dec_z64_k21_decade.png
umap_dec_z64_k21_lang.png
umap_comparison_genre.png        ← rapor için altın (3-panel hero figure)
```

## Rapor için en faydalı 4 figür

1. **`umap_comparison_genre.png`** — vanilla vs multi-modal vs DEC yan yana (Finding 1+5+6'nın görsel kanıtı)
2. **`umap_dec_z64_k21_genre.png`** — en iyi modelin genre yapısı
3. **`umap_dec_z64_k21_lang.png`** — lang ayrımı (Finding 1: +178%/multi-modal'ın hero kazancı)
4. **`umap_ae_z64_w1_genre.png`** — W1 collapse görsel kanıtı (Finding 2)

## Notlar

- **N_VIS = 15000** → değiştirilebilir (50K denersen ~30 dk, 5K denersen ~2 dk)
- **UMAP `metric='cosine'`** — latent uzay için angular distance daha sağlıklı
- **`top_n=12`** her plot'ta — en yaygın 12 kategori + "Other" (genre 21+, lang 11 var, decade ~12)
- Hata olursa: `pip install umap-learn` cell başında çağırılmalı (Colab'da default değil)

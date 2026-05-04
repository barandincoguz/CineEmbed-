# One-time: Re-evaluate AE checkpoints with fixed decade labels

> **Geçici dosya** — Drive'a sync olunca Colab'da kullan, sonra Mac'te sil.
> Sadece mevcut 3 AE checkpoint'in NMI/ARI'sini düzeltir, retrain yok.

## Adımlar

1. Colab'da `02_train_ae.ipynb` açıkken **yeni boş cell** oluştur
2. Aşağıdaki kod bloğunu kopyala-yapıştır
3. **Run** (~5-10 dk; 3× embed extraction + KMeans)
4. Çıktıdaki `Final AE summary` 3 satırlı tablo görmen lazım — decade_NMI artık 0 değil
5. Bittikten sonra cell'i sil (artık gereksiz)

## Cell

```python
# ─── Re-evaluate AE checkpoints with fixed decade labels (one-time) ───────
import os, sys, json, time
from pathlib import Path

# 1. Pull the data.py fix from GitHub
get_ipython().system('cd /content/cineembed-repo && git pull -q')

# 2. Force-reimport the package to pick up the new data.py
for m in [k for k in list(sys.modules) if k.startswith('cineembed')]:
    del sys.modules[m]
sys.path.insert(0, '/content/cineembed-repo/src')
from cineembed import data, backbone, heads, train, eval as cev
import numpy as np
import torch

ARTIFACTS = Path('/content/drive/MyDrive/CineEmbed/artifacts')
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

# 3. Reload feature matrix + the FIXED labels
X, feature_names = data.load_feature_matrix(ARTIFACTS / 'feature_matrix.npz')
labels = data.get_labels(ARTIFACTS / 'movies_eda_final.csv')
block_slices = data.get_block_indices(feature_names)
has_bio = X[:, block_slices['director'].start + 64].clone()

# Verify the fix worked: decade should now have variety
import pandas as pd
print(f"[{time.strftime('%H:%M:%S')}] Decade label sanity check:")
print(f"   unique decade values: {sorted(set(labels['decade_bin']))[:15]}...")
print(f"   distribution: {pd.Series(labels['decade_bin']).value_counts().head(10).to_dict()}")

# 4. Block dims + projection
BLOCK_DIMS = {b: (slc.stop - slc.start) for b, slc in block_slices.items()}
PROJ_DIMS = backbone.DEFAULT_PROJ_DIMS

# 5. Helper: re-embed + re-evaluate one checkpoint
def reevaluate(run_name, vanilla=False):
    print(f"\n[{time.strftime('%H:%M:%S')}] Re-evaluating {run_name}...")
    ckpt_path = ARTIFACTS / 'models' / f'{run_name}.pt'
    if not ckpt_path.exists():
        print(f"   missing: {ckpt_path}")
        return None

    if vanilla:
        import torch.nn as nn
        bb_fc = nn.Sequential(nn.Linear(564, 128), nn.ReLU(), nn.Dropout(0.2), nn.Linear(128, 64))
        class _VanillaWrap(nn.Module):
            def __init__(self, fc, z_dim_):
                super().__init__()
                self.fc = fc; self.latent_dim = z_dim_
                self.block_order = list(BLOCK_DIMS.keys())
            def forward(self, blocks, block_mask=None):
                X_cat = torch.cat([blocks[b] for b in self.block_order], dim=1)
                return self.fc(X_cat)
        bb = _VanillaWrap(bb_fc, 64)
    else:
        bb = backbone.MultiModalBackbone(BLOCK_DIMS, PROJ_DIMS, hidden_dim=128, latent_dim=64)
    head = heads.AEHead(bb, BLOCK_DIMS, PROJ_DIMS, hidden_dim=128)
    train.load_checkpoint(head, ckpt_path, device=DEVICE)
    head = head.to(DEVICE).eval()

    z_full = []
    full_loader = data.make_dataloader(X, has_bio, batch_size=2048, shuffle=False, block_slices=block_slices)
    with torch.no_grad():
        for batch in full_loader:
            blk = {k: v.to(DEVICE) for k, v in batch['blocks'].items()}
            z_full.append(head.encode(blk).cpu().numpy())
    z_all = np.concatenate(z_full, axis=0)

    c_ids = cev.cluster_assignments_kmeans(z_all, k=21, seed=42)
    metrics = cev.evaluate_run(c_ids, labels)
    print(f"   genre_NMI={metrics['genre_nmi']:.3f}  decade_NMI={metrics['decade_nmi']:.3f}  lang_NMI={metrics['lang_nmi']:.3f}")
    return metrics

# 6. Update results.json — preserve metadata, replace eval metrics
results_path = ARTIFACTS / 'eval' / 'results.json'
results = json.loads(results_path.read_text())

for run, vanilla in [('vanilla_ae_z64', True), ('ae_z64', False), ('ae_z64_w1', False)]:
    new_m = reevaluate(run, vanilla=vanilla)
    if new_m is not None:
        existing = results.get(run, {})
        existing.update({k: v for k, v in new_m.items() if k.endswith(('_nmi', '_ari'))})
        results[run] = existing

results_path.write_text(json.dumps(results, indent=2))
print(f"\n[{time.strftime('%H:%M:%S')}] Updated {results_path}")
print("\nFinal AE summary:")
for run in ['vanilla_ae_z64', 'ae_z64', 'ae_z64_w1']:
    m = results.get(run, {})
    print(f"  {run:25s} | genre={m.get('genre_nmi',0):.3f}  decade={m.get('decade_nmi',0):.3f}  lang={m.get('lang_nmi',0):.3f}")
```

## Bittikten sonra

- Bu cell'i Colab'da sil
- Bu `.md` dosyasını Mac'te sil:
  ```bash
  rm "/Users/barandincoguz/Desktop/deep learning movie project/notebooks/REEVAL_AE_DECADE.md"
  ```
- Sonra **04_train_dec.ipynb** → Run All

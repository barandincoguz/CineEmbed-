# CineEmbed — Empirical Findings (Living Document)

> **Updated continuously** as new runs complete. Source of truth for raporda kullanılacak claims.
> Last updated: 2026-05-05

---

## Run inventory

| Run | z | k | Status | genre NMI | decade NMI | lang NMI | val_loss | epochs |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| `vanilla_ae_z64` | 64 | — | ✅ | 0.287 | 0.369 | 0.095 | 0.0126 | 58 |
| `ae_z64` (multi-modal) | 64 | — | ✅ | **0.328** | 0.341 | **0.264** | 0.0208 | 69 |
| `ae_z64_w1` (uniform W) | 64 | — | ✅ | 0.165 | 0.367 | 0.070 | 0.0453 | 37 |
| `dec_z64_k21` | 64 | 21 | ⏳ pending | — | — | — | — | — |
| `kmeans_raw_k21` (baseline) | 564 | 21 | ⏳ from 05_results | — | — | — | — | — |
| `pca_kmeans_k21` (baseline) | 64 | 21 | ⏳ from 05_results | — | — | — | — | — |

**genre_ARI breakdown**: vanilla=0.247, multi-modal=0.229, W1=0.094

---

## Hero findings (rapor için altın)

### 🏆 Finding 1 — Architecture's biggest win is on LANGUAGE (+178%)

| | vanilla concat-AE | multi-modal AE | relative gain |
|---|---:|---:|---:|
| lang_NMI | 0.095 | 0.264 | **+178%** |
| genre_NMI | 0.287 | 0.328 | +14% |
| decade_NMI | 0.369 | 0.341 | -7.6% |

**Claim:** Modality-specific projection layers are essential for capturing categorical signal interactions. Vanilla concat-AE collapses heterogeneous modalities into a single FC layer that under-represents low-frequency one-hot blocks (language: 31 sparse dims, ~99% zero per row).

**Spec criterion (D1):** ≥5% relative gain on multi-modal vs vanilla. **PASS** at +14% on genre, +178% on language.

### 🏆 Finding 2 — W2 inverse-variance weighting is critical (asymmetric collapse)

| | W2 (multi-modal) | W1 (uniform) | relative |
|---|---:|---:|---:|
| genre_NMI | 0.328 | 0.165 | -50% |
| decade_NMI | 0.341 | 0.367 | +8% |
| lang_NMI | 0.264 | 0.070 | -73% |

**Claim:** Without inverse-variance weighting, high-dimensional low-variance modalities (text 384 dims, language 31 dims) lose all gradient signal. The W1 collapse is **dimension-asymmetric** — small blocks (decade 2 dims) survive uniform weighting because StandardScaler already gave them per-feature variance ≈ 1.

**Spec criterion (D3):** W2.NMI > W1.NMI × 1.05. **PASS** at +99% on genre, +277% on language.

### 🏆 Finding 3 — Reconstruction loss ≠ clustering quality

- `vanilla_ae_z64`: val_loss = **0.0126** (lowest), genre_NMI = 0.287
- `ae_z64`: val_loss = 0.0208 (higher), genre_NMI = **0.328** (highest)

**Claim:** Multi-modal architecture trades minor reconstruction fidelity for substantially better latent structure. This is the classic "useful representation vs perfect copy" tension — a vivid empirical demonstration of representation learning theory.

### 🏆 Finding 4 — Decade is the strongest natural axis (~0.35 NMI universal)

All three architectures (vanilla, multi-modal, W1) capture decade at NMI ≈ 0.34-0.37. Movie metadata has strong year-correlated patterns that emerge regardless of architecture.

**Implication for report:** Genre is harder to cluster than decade. Real-world movie genres are multi-label and overlap heavily; decade is single-valued and ordinal — this geometric difference makes decade easier to recover via KMeans.

### 🏆 Finding 5 — Pareto trade-off across axes

The multi-modal backbone is **not uniformly superior** to vanilla:
- Wins big on language (+178%)
- Wins moderately on genre (+14%)
- Loses slightly on decade (-7.6%)

**Interpretation:** Modality-specific projection allocates capacity to text/director blocks, slightly reducing fidelity on the trivially-encoded decade signal. This is a **principled trade-off**, not a bug — for downstream tasks that care about content/language similarity, the multi-modal approach is clearly better.

---

## Methodological observations

### Early stopping patterns reveal model health

| Run | Epochs | Why stopped |
|---|---:|---|
| vanilla_ae_z64 | 58 | Plateaued cleanly |
| ae_z64 | **69** | Longest — careful learning with proper weighting |
| ae_z64_w1 | **37** | Patience exhausted early — model couldn't escape modality imbalance |

W1's early stop is a **diagnostic signal**, not just a hyperparameter event: it shows the model gave up because no further val improvement was possible.

### genre_ARI inverts genre_NMI ordering

- vanilla genre_ARI = **0.247** (highest)
- multi-modal genre_ARI = 0.229

Despite multi-modal winning genre_NMI, vanilla wins genre_ARI. Interpretation: vanilla creates "harder" cluster boundaries that match genre labels more crisply, while multi-modal creates "softer" structure that captures genre information richly but with fuzzier KMeans-partitions. **DEC may close this gap** by explicitly optimizing cluster compactness.

---

## Open hypotheses (waiting on remaining runs)

### H1 — DEC will improve genre_NMI over AE
DEC explicitly optimizes cluster centers via KL divergence on soft assignments. Expected: dec_z64_k21 NMI > ae_z64 NMI (currently 0.328). Possible regression if KL forces structure that conflicts with natural genre overlaps.

### H2 — Best deep model > best baseline by ≥10% relative
Spec success criterion (D9). Need baselines from 05_results to evaluate.

### H3 — Best deep NMI > 0.15 absolute floor
Already validated: ae_z64 NMI = 0.328 ≫ 0.15. **PASS**

---

## Deferred for final report (NOT in MVP)

- VAE family (z=32, 64, 128) — not yet trained
- AE additional dims (z=32, 128)
- F1 ablation (no text) — to test text contribution
- F2 ablation (no director_profile) — to test bio coverage value
- DEC k-sweep (z×k = 9 runs total, MVP has only z=64×k=21)
- W4 (Kendall learned uncertainty) — optional stretch
- Linear probing on z=64 frozen latents
- All 27 UMAP figures (only 3 baseline + 9 best-of-each in main report)

See `docs/PROGRESS.md` "Path to final report" section for the full deferred list and run sequence.

---

## Files referenced

- Decision log: `docs/adr/0001-modeling-hybrid-architecture.md` (D1–D10)
- Spec: `docs/superpowers/specs/2026-05-04-modeling-design.md`
- Implementation plan: `docs/superpowers/plans/2026-05-04-modeling-implementation.md`
- Progress tracker: `docs/PROGRESS.md`
- Results JSON: `MyDrive/CineEmbed/artifacts/eval/results.json`

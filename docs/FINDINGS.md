# CineEmbed — Empirical Findings (Living Document)

> **Updated continuously** as new runs complete. Source of truth for raporda kullanılacak claims.
> Last updated: 2026-05-05 (MVP complete — 6/6 runs done, all 3 hypotheses validated)

## 🎯 MVP status: COMPLETE ✅

All three pre-registered hypotheses **PASS**:
- **H1** DEC > AE on genre_NMI: 0.332 > 0.328 (marginal NMI, +6.6% ARI)
- **H2** Deep > non-deep baseline ≥10%: **+205% / +295%** (massive)
- **H3** Best deep NMI > 0.15 floor: 0.332 ≫ 0.15

Best model: `dec_z64_k21` — genre_NMI=0.332, lang_NMI=0.294, decade_NMI=0.342.

---

## Run inventory

| Run | z | k | Status | genre NMI | decade NMI | lang NMI | val_loss | epochs |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| `vanilla_ae_z64` | 64 | — | ✅ | 0.287 | 0.369 | 0.095 | 0.0126 | 58 |
| `ae_z64` (multi-modal) | 64 | — | ✅ | **0.328** | 0.341 | **0.264** | 0.0208 | 69 |
| `ae_z64_w1` (uniform W) | 64 | — | ✅ | 0.165 | 0.367 | 0.070 | 0.0453 | 37 |
| `dec_z64_k21` | 64 | 21 | ✅ | **0.332** | 0.342 | **0.294** | 0.127† | 21 |
| `kmeans_raw_k21` (baseline) | 564 | 21 | ✅ | 0.109 | 0.233 | 0.075 | n/a | n/a |
| `pca_kmeans_k21` (baseline) | 64 | 21 | ✅ | 0.084 | 0.224 | 0.094 | n/a | n/a |

† DEC val_loss is KL + reconstruction combined — **not directly comparable** to AE pure-recon val_loss. Use NMI/ARI for cross-model comparison.

**genre_ARI breakdown**: vanilla=0.247, multi-modal=0.229, W1=0.094, **DEC=0.244**, kmeans_raw=0.063, pca_kmeans=0.061

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

### 🏆 Finding 6 — Deep models outperform non-deep baselines by 3–5× (H2 massively PASS)

| | kmeans_raw_k21 (564 dim) | pca_kmeans_k21 (64 dim) | dec_z64_k21 (64 dim) | DEC vs raw / pca |
|---|---:|---:|---:|---:|
| genre_NMI | 0.109 | 0.084 | **0.332** | **+205% / +295%** |
| genre_ARI | 0.063 | 0.061 | **0.244** | **+287% / +300%** |
| decade_NMI | 0.233 | 0.224 | 0.342 | +47% / +53% |
| lang_NMI  | 0.075 | 0.094 | **0.294** | **+292% / +213%** |

**Claim:** Non-deep clustering of the raw 564-dim feature matrix recovers only ~1/3 of the structure that the multi-modal AE → DEC pipeline finds. PCA-64 + KMeans is *worse* than raw-KMeans on genre (PCA discards genre-discriminative variance) but slightly better on language (PCA cleans noise). **Both are dominated by the deep pipeline by a large margin.**

**Spec criterion (D9 / H2):** best_deep > best_non_deep_baseline × 1.10. **PASS** at +205% over kmeans_raw (genre) and +295% over pca_kmeans. The intermediate report's strongest single claim.

**Note on terminology:** Some narrative outputs report `vanilla_ae_z64` as "best baseline" (NMI=0.287). This is methodologically misleading — vanilla_ae is itself a deep model (a simpler concat-AE), and serves as our **architecture ablation baseline**. The true non-deep baselines are KMeans on raw / PCA-reduced features. Use the three-tier framing in the report:

1. **Non-deep baseline** (KMeans variants): NMI ≈ 0.08–0.11
2. **Simple deep model** (vanilla concat-AE): NMI = 0.287 (+170% over baseline)
3. **Multi-modal deep model** (ae_z64, dec_z64_k21): NMI = 0.328–0.332 (+200–300% over baseline, +14–16% over simple deep)

### 🏆 Finding 7 — DEC sharpens cluster boundaries (ARI > NMI improvement pattern)

DEC was initialized from `ae_z64`'s encoder weights and trained for 21 KL+recon epochs:

| | ae_z64 (init) | dec_z64_k21 | gain |
|---|---:|---:|---:|
| genre_NMI | 0.328 | **0.332** | +1.2% |
| genre_ARI | 0.229 | **0.244** | **+6.6%** |
| lang_NMI  | 0.264 | **0.294** | **+11.4%** |
| decade_NMI | 0.341 | 0.342 | flat |

**Claim:** DEC's contribution is **cluster compactness, not new structural information**. KL-divergence on soft assignments tightens decision boundaries that AE has already discovered — the larger ARI gain than NMI gain is the diagnostic signature (information content is similar, but the partition is more crisp).

**Validates earlier prediction:** In the methodological observations we noted that vanilla had higher genre_ARI than multi-modal *despite* lower NMI, and conjectured DEC would close the gap. **It did:** DEC's ARI=0.244 essentially ties vanilla's 0.247, while keeping multi-modal's huge lang_NMI advantage. **DEC = best of both worlds.**

**Cluster health:** `total_reinit = 0` across 21 epochs → all 21 KMeans++ centroids survived KL training without collapse. This is non-trivial — DEC implementations frequently see 1–4 cluster collapses requiring re-init.

**Spec criterion (D8/H1):** DEC.NMI > AE.NMI. **PASS** marginally (+1.2%). The richer story is the +6.6% ARI gain at the same information level.

---

## 🎯 Final hero comparison (rapor için canonical table)

Three-tier model comparison on z=64, k=21 (where applicable):

| Tier | Model | genre NMI | genre ARI | decade NMI | decade ARI | lang NMI | lang ARI |
|---|---|---:|---:|---:|---:|---:|---:|
| **Non-deep baseline** | kmeans_raw_k21 | 0.109 | 0.063 | 0.233 | 0.093 | 0.075 | 0.026 |
| **Non-deep baseline** | pca_kmeans_k21 | 0.084 | 0.061 | 0.224 | 0.085 | 0.094 | 0.042 |
| **Simple deep** | vanilla_ae_z64 | 0.287 | **0.247** | **0.369** | 0.175 | 0.095 | 0.030 |
| Ablation (W1) | ae_z64_w1 | 0.165 | 0.094 | 0.367 | 0.176 | 0.070 | 0.026 |
| **Multi-modal deep** | ae_z64 | 0.328 | 0.229 | 0.341 | **0.211** | 0.264 | 0.090 |
| **Best (deep + DEC)** | **dec_z64_k21** | **0.332** | 0.244 | 0.342 | 0.210 | **0.294** | **0.090** |

**Bold = winner per column.** Note no single model wins all 6 metrics — vanilla wins decade_NMI + genre_ARI, multi-modal wins decade_ARI, DEC wins genre_NMI + lang_NMI + lang_ARI. This non-uniformity is the principled-trade-off story.

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

Despite multi-modal winning genre_NMI, vanilla wins genre_ARI. Interpretation: vanilla creates "harder" cluster boundaries that match genre labels more crisply, while multi-modal creates "softer" structure that captures genre information richly but with fuzzier KMeans-partitions. **DEC closes this gap** (ARI 0.244 vs vanilla's 0.247 — essentially tied) while keeping multi-modal's lang advantage — see Finding 6.

---

## Hypothesis status

### H1 — DEC will improve genre_NMI over AE ✅ (PASS, marginal)
**Result:** dec_z64_k21 NMI=0.332 > ae_z64 NMI=0.328 (+1.2%). The honest interpretation is *NMI essentially flat, ARI +6.6%, lang_NMI +11.4%* — DEC contributes cluster compactness, not new latent structure. See Finding 6.

### H2 — Best deep model > best baseline by ≥10% relative ✅ (PASS, massive)
Spec success criterion (D9). **Result:** dec_z64_k21 genre_NMI=0.332 vs best non-deep baseline (kmeans_raw_k21=0.109) → **+205% relative**, far above the 10% threshold. Same massive gap on lang_NMI (+213% vs pca_kmeans_k21=0.094). See Finding 6.

### H3 — Best deep NMI > 0.15 absolute floor ✅ (PASS)
ae_z64 NMI = 0.328 ≫ 0.15. dec_z64_k21 NMI = 0.332 ≫ 0.15.

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

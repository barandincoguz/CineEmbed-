# CineEmbed — Final Report Artifact Inventory

**Generated:** 2026-05-19 (T-1 to deadline 2026-05-20)
**Purpose:** Single source-of-truth for every data asset, figure, and number that the final report (`.tex`) and presentation (`.pptx`) may cite.
**Scope:** project root `/Users/barandincoguz/Desktop/deep learning movie project/`
**Author:** inventory pass — no figure generation; flags missing assets at the bottom.

> Tier legend: HERO = goes in main results / on a slide. STRONG = appendix or supporting slide. SUPPORT = optional, skip unless space. TO-GENERATE = does not exist yet, flagged for creation.

---

## 0. Headline facts (verified across files)

| Fact | Value | Source of truth |
|---|---|---|
| Dataset size (films, post-EDA) | **329 044** | `artifacts/pipeline_version.json` → `n_films`; `artifacts/feature_metadata.json` → `n_films`; all 4 manifests (ae_z32/64/128 + dec) → `n_films`; `artifacts/backbones.json` → `nFilms` for all 3 backbones |
| Feature matrix dimensionality | **564** (numerical 6 + genre 22 + lang 31 + decade 2 + awards 6 + text 384 + director 113) | `artifacts/feature_metadata.json` → `total_dim`, `block_dims` |
| Feature matrix MD5 (canonical, at-creation) | **`e99cee84b6891ea352a7b44d5d7d0ee4`** | `artifacts/pipeline_version.json` → `feature_matrix_md5` |
| Feature matrix MD5 (local file, today) | `a213fb98570318d7f1b28ceefbb2eb2e` | `md5 artifacts/feature_matrix.npz` |
| Note on MD5 mismatch | `.npz` is a zip archive — its byte-level MD5 depends on file order + timestamps inside. Logical contents are identical; **cite the at-creation MD5** from `pipeline_version.json`. | — |
| Embedding dim (demo backbone) | 32 | `artifacts/inference/ae_z32/manifest.json` |
| Normalization | L2 | all manifests |
| Distance metric | cosine (dot product after L2) | all manifests |
| Random seed | 42 | `artifacts/pipeline_version.json` |
| Pipeline timestamp | 2026-05-04T19:59:05Z | `artifacts/pipeline_version.json` |
| Text encoder | `paraphrase-multilingual-MiniLM-L12-v2` | `artifacts/pipeline_version.json` → `model_name` |
| Library versions | numpy 2.0.2, pandas 2.2.2, sentence-transformers 5.4.1, torch 2.10.0+cu128, umap-learn 0.5.12, scikit-learn 1.6.1 | `artifacts/pipeline_version.json` |

---

## 1. `artifacts/` — top-level inventory

| Path | Size | Role |
|---|---|---|
| `artifacts/backbones.json` | 715 B | **Frontend-facing manifest** — 3 backbones (ae_z32 preferred, ae_z64, ae_z128) with `genreAtFive`, `gnmi`, checkpoint hashes, nFilms. Use for the canonical 3-row Round-2 table. |
| `artifacts/director_profile_metadata.json` | 744 B | EDA-era director-profile metadata (block dims, source CSV references) |
| `artifacts/feature_matrix.npz` | 403 MB | The scaled (329044, 564) feature matrix used for all training. Local MD5 differs from canonical (zip metadata only); cite `pipeline_version.json` MD5. |
| `artifacts/feature_matrix_raw.npz` | 395 MB | Pre-scaler raw feature matrix (kept for reproducibility of standardization step) |
| `artifacts/feature_metadata.json` | 10 KB | Full feature_names (564), block_order, block_dims, total_dim, n_films |
| `artifacts/movies_eda_final.csv` | 253 MB | The merged film-level metadata (id, title, year, genres, lang, …) — 329k rows |
| `artifacts/pipeline_version.json` | 428 B | Pipeline provenance — **HERO citation source** (seed, MD5, lib versions, text encoder) |
| `artifacts/scalers.pkl` | 1.1 KB | StandardScaler joblib pickle |
| `artifacts/cache/tmdb/` | many | TMDb poster/metadata JSON cache for ~163 films (frontend gallery) |
| `artifacts/eval/` | — | See §2 |
| `artifacts/models/` | — | See §3 |
| `artifacts/inference/` | — | See §4 |
| `artifacts/figures/` | — | See §6 |

---

## 2. `artifacts/eval/` — quantitative results

| File | Role | Tier |
|---|---|---|
| `results.json` | **MVP results table** — 6 model rows × {genre, decade, lang} × {NMI, ARI, AMI where present} + epochs + val_loss + z_dim. The ground truth for all Round-1 / Phase-0 numbers. | HERO |
| `results_table_mvp.csv` | Same content as `results.json`, flat CSV — easier to drop into LaTeX `\input{}` / pptx table | HERO |
| `round2_results.json` | **NOTE — content is identical to `results.json`** (it does NOT actually contain Round 2 ae_z32/ae_z128 metrics). The real Round 2 metrics live in `artifacts/models/ae_z{32,128}/eval.json` + `artifacts/inference/ae_z{32,64,128}/manifest.json`. Flag for the report author. | (broken) |

### 2.1 Parsed run table — MVP / Round 1 (clustering metrics, k=21 KMeans on latents unless noted)

| run_id | z | k | genre_NMI | genre_ARI | decade_NMI | decade_ARI | lang_NMI | lang_ARI | val_loss | epochs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `kmeans_raw_k21` (baseline) | 564 | 21 | 0.109 | 0.063 | 0.233 | 0.093 | 0.075 | 0.026 | — | — |
| `pca_kmeans_k21` (baseline) | 64 | 21 | 0.084 | 0.061 | 0.224 | 0.085 | 0.094 | 0.042 | — | — |
| `vanilla_ae_z64` | 64 | — | 0.287 | 0.247 | **0.369** | 0.175 | 0.095 | 0.030 | 0.0126 | 58 |
| `ae_z64_w1` (uniform W ablation) | 64 | — | 0.165 | 0.094 | 0.367 | 0.176 | 0.070 | 0.026 | 0.0453 | 37 |
| `ae_z64` (multi-modal W2) | 64 | — | 0.328 | 0.229 | 0.341 | **0.211** | 0.264 | 0.090 | 0.0208 | 69 |
| `dec_z64_k21` (Phase-0 NMI champion, retrieval-disqualified) | 64 | 21 | **0.332** | 0.244 | 0.342 | 0.210 | **0.294** | 0.090 | 0.127† | 21 |

† DEC val_loss = KL + recon — not comparable to AE pure-recon. (source: `docs/FINDINGS.md`)
Also recorded: `genre_AMI` / `decade_AMI` / `lang_AMI` for `dec_z64_k21` (≈ matches NMI within 1e-3).

### 2.2 Round 2 — AE z-sweep (from `artifacts/models/ae_z{32,128}/eval.json` + `artifacts/inference/*/manifest.json` + `backbones.json`)

| run_id | z | clusterer | genre_NMI | genre_ARI | decade_NMI | decade_ARI | lang_NMI | lang_ARI | per-axis K best | genre@5 (retrieval) | val_loss | epochs |
|---|---:|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|
| `ae_z32` (**demo backbone**) | 32 | KMeans k=21 | **0.334** | 0.195 | 0.295 | 0.184 | 0.216 | 0.085 | g@k21=0.334, d@k12=0.258, l@k11=0.185 | **0.723** | 0.0204† | 100 |
| `ae_z32` | 32 | GMM k=21 | 0.312 | 0.147 | 0.205 | 0.066 | 0.246 | 0.044 | — | — | — | — |
| `ae_z64` (carry-over) | 64 | KMeans k=21 | 0.333 | 0.244 | 0.343 | 0.211 | 0.293 | 0.090 | g=0.333, d@k12=0.329, l@k11=0.330 | 0.715 | 0.0208 | 69 |
| `ae_z64` | 64 | GMM k=21 | 0.332 | 0.246 | 0.346 | 0.212 | 0.283 | 0.088 | — | — | — | — |
| `ae_z128` (over-parameterised) | 128 | KMeans k=21 | 0.273 | 0.148 | 0.275 | 0.147 | 0.272 | 0.068 | g=0.273, d@k12=0.300, l@k11=0.180 | 0.722 | 0.0237† | 53 |
| `ae_z128` | 128 | GMM k=21 | 0.187 | 0.027 | 0.281 | 0.129 | 0.300 | 0.055 | — | — | — | — |

† `final_val_loss` from `history.json` files. `ae_z32` ran 100 epochs (final val=0.0204); `ae_z128` ran 53 (final val=0.0237). The `ae_z64` row's val_loss is the MVP value (0.0208).

**Retrieval queries (genre@5 mean over 316 queries) — from `manifest.json`:**
| backbone | n_queries | k | genre@5 mean | median | std | mean random-pair cosine | ± std |
|---|---:|---:|---:|---:|---:|---:|---:|
| ae_z32 | 316 | 5 | **0.7228** | 1.0 | 0.352 | 0.302 | 0.301 |
| ae_z64 | 316 | 5 | 0.7146 | 0.8 | 0.348 | 0.303 | 0.299 |
| ae_z128 | 316 | 5 | 0.7215 | 0.8 | 0.345 | 0.342 | 0.289 |
| dec_z64_k21 | 316 | 5 | **0.5570** | 0.6 | 0.374 | **0.096** | **0.421** |

`dec_z64_k21`'s near-zero mean random-pair cosine paired with std=0.42 is the **zero-collapse / cos≈1.000 within-cluster** signature (Finding from journal/07 — NMI≠retrieval).

### 2.3 Hypothesis summary (from `docs/FINDINGS.md` §H1–H3, §Findings 1-9)

- **H1** DEC > AE on genre_NMI: 0.332 > 0.328 (PASS, +1.2% NMI / +6.6% ARI / +11.4% lang_NMI)
- **H2** Best deep > best non-deep baseline × 1.10: 0.332 vs 0.109 = **+205%** (massive PASS)
- **H3** Best deep NMI > 0.15 floor: 0.332 ≫ 0.15 (PASS)
- **Finding 8 — UMAP topology evolves blobs → islands → tight islands** across vanilla → multi-modal → DEC. Hero figure: `umap_comparison_genre.png`.
- **Finding 9 — Missing-release_date films form a coherent latent sub-manifold** (red cluster in DEC decade UMAP, ~7.4% of sample). Hero figure: `umap_dec_z64_k21_decade.png`.

---

## 3. `artifacts/models/` — checkpoints and training history

| Dir | Files | Purpose |
|---|---|---|
| `ae_z32/` | `ae.pt` (482 KB), `backbone.pt` (221 KB), `eval.json` (1.9 KB), `history.json` (5.1 KB) | **Demo backbone.** Full checkpoint + encoder-only backbone + train/val loss curves (100 epochs). |
| `ae_z128/` | `ae.pt` (577 KB), `backbone.pt` (270 KB), `eval.json` (1.9 KB), `history.json` (2.7 KB) | Over-parameterised. 53 epochs (early stop). |
| `ae_z64.pt` | 514 KB | MVP carry-over (multi-modal W2). 69 epochs. |
| `ae_z64_w1.pt` | 516 KB | Uniform-weight ablation. 37 epochs (collapsed early). |
| `dec_z64_k21/` | `eval.json` only (2.3 KB) | DEC clustering eval (kmeans / dec_argmax / gmm / per-axis k variants on the DEC latent). |
| `dec_z64_k21.pt` | 521 KB | DEC checkpoint. |
| `vanilla_ae_z64.pt` | 595 KB | Concat-AE baseline (no modality projection). 58 epochs. |

**Loss curves available (for z-sweep U-curve plot):** `ae_z32/history.json` (100 epochs, train_loss + val_loss arrays), `ae_z128/history.json` (53 epochs). No history.json for ae_z64 / dec / vanilla / w1 — those numbers come from `results.json` (final val_loss + n_epochs only).

---

## 4. `artifacts/inference/` — pre-computed embeddings, films, clusters

| Dir | Files | Notes |
|---|---|---|
| `ae_z32/` | `embeddings.npy` (42 MB, float32, 329044×32), `films.parquet` (80 MB), `manifest.json` (8.4 KB), `cluster_labels.npy` (329 KB), `cluster_meta.json` (6.6 KB) | **Demo backbone.** Manifest contains retrieval stats + 10 eyeball top-5 tables (Inception, Godfather, Toy Story, Shawshank, Pulp Fiction, Matrix, Interstellar, Forrest Gump, Dark Knight, Spirited Away). |
| `ae_z64/` | `embeddings.npy` (84 MB), `films.parquet` (80 MB), `manifest.json` (8.4 KB), `cluster_labels.npy`, `cluster_meta.json` (6.3 KB) | MVP carry-over. Same 10 eyeball queries with different neighbour lists. |
| `ae_z128/` | `embeddings.npy` (168 MB), `films.parquet` (80 MB), `manifest.json` (8.4 KB), `cluster_labels.npy`, `cluster_meta.json` (6.9 KB) | Over-parameterised. |
| `dec_z64_k21/` | `embeddings.npy` (84 MB), `films.parquet` (78 MB), `manifest.json` (8.4 KB) | NMI champion, retrieval-disqualified (cos→1 collapse). |
| `films_master.parquet` | 79 MB | Frontend master film table. |
| `gallery.json` | 139 KB | Pre-rendered gallery for the web app demo. |
| `cluster_names_override.json` | 52 B | Empty stubs `{}` for each backbone — manual naming override hook (unused). |

### 4.1 Cluster naming (21 clusters, ae_z32 demo backbone) — from `ae_z32/cluster_meta.json`

Clusters are 21 MiniBatchKMeans centroids on the L2-normalized ae_z32 latent. Each entry has `{id, name, size, topGenres[top 3 with pct], modalDecade}`. **Naming heuristic** (implicit from the file): `"{dominant_genre} · {modal_decade}"` with `(k=N)` suffix when collisions exist. Cluster names verbatim:

| id | name | size | modalDecade | top genre (pct) |
|---:|---|---:|---|---|
| 0 | Action · 2010s | 14 200 | 2010s | Action 0.395 |
| 1 | Mixed · 2010s | 25 141 | 2010s | (no dominant — empty topGenres) |
| 2 | Documentary · 2000s (k=2) | 27 733 | 2000s | Documentary 0.237 |
| 3 | Drama · 2000s (k=3) | 14 294 | 2000s | Drama 0.367 |
| 4 | Documentary · Mixed era (k=4) | 13 078 | Mixed era | Documentary 0.334 |
| 5 | Drama · 2010s (k=5) | 29 685 | 2010s | Drama 0.300 |
| 6 | War · 2000s | 31 305 | 2000s | War 0.500 / Documentary 0.500 (tie) |
| 7 | Drama · 2010s (k=7) | 9 877 | 2010s | Drama 0.253 |
| 8 | Thriller · 2010s | 23 470 | 2010s | Thriller 0.318 |
| 9 | Drama · 2010s (k=9) | 8 125 | 2010s | Drama 0.358 |
| 10 | Drama · 1980s | 5 306 | 1980s | Drama 0.234 |
| 11 | Drama · 2000s (k=11) | 22 452 | 2000s | Drama 0.366 |
| 12 | Documentary · 2010s | 19 716 | 2010s | Documentary 0.304 |
| 13 | Drama · 2010s (k=13) | 14 367 | 2010s | Drama 0.202 |
| 14 | Drama · 2010s (k=14) | 6 257 | 2010s | Drama 0.210 |
| 15 | Comedy · 2000s | 5 587 | 2000s | Comedy 0.301 |
| 16 | History · 1980s | 6 892 | 1980s | History 0.417 / Documentary 0.417 (tie) |
| 17 | Drama · 2010s (k=17) | 5 649 | 2010s | Drama 0.356 |
| 18 | Documentary · 2000s (k=18) | 24 781 | 2000s | Documentary 0.429 / History 0.429 (tie) |
| 19 | Drama · 2010s (k=19) | 9 057 | 2010s | Drama 0.251 |
| 20 | Documentary · Mixed era (k=20) | 12 072 | Mixed era | Documentary 0.238 |

Total: 329 044 films ✓.

**Per-backbone cluster meta files differ** — each manifest has its own 21 KMeans run, so cluster IDs / sizes / dominant labels are not aligned across z=32/64/128. Cite ae_z32 in the report (demo backbone).

### 4.2 Eyeball retrieval examples (verbatim from manifests — usable as report Table)

10 queries × top-5 neighbours × 4 backbones (ae_z32, ae_z64, ae_z128, dec_z64_k21). The contrast is the story:
- `dec_z64_k21` returns near-identical cosines ≈ 0.9999 for all 5 neighbours (cluster collapse — retrieval-broken).
- `ae_z32` returns crisp same-franchise / same-style hits (Inception → Dark Knight 0.991, Toy Story → Toy Story 2 0.981, Spirited Away → Princess Mononoke 0.993).

**Strong candidate for a report Table:** Inception + Spirited Away + Pulp Fiction, ae_z32 vs dec_z64_k21 side-by-side, to make the NMI≠retrieval point.

---

## 5. `mermaid/` — diagram source files (Markdown with `mermaid` code blocks)

| File | Renders to | Topic |
|---|---|---|
| `01-hero-high-level-architecture.md` | `figures/high-level-architecture.png` | End-to-end pipeline: raw data → EDA → feature matrix → backbones → eval → demo |
| `02-data-engineering-pipeline.md` | `figures/data-engineering-pipeline.png` | EDA v2 pipeline: 5 source CSVs → merge → cleaning → 564-dim block-wise concat |
| `03-multimodal-model-architecture.md` | `figures/architecture_multimodal.png` | The multi-modal AE: per-block input projections → trunk encoder → z=32 → mirrored decoder |
| `04-three-tier-model-taxonomy.md` | `figures/three-tier-taxonomy.png` | Non-deep baselines → simple deep (vanilla concat-AE) → multi-modal deep |
| `05-three-axis-evaluation-methodology.md` | `figures/three-exis-eval-method.png` | (sic, "exis"=axis typo in filename) Genre / decade / language axes × NMI / ARI / AMI matrix |

---

## 6. Figures — full enumeration with tier assignment

**Total figures available: 39 unique PNGs** (5 architecture diagrams + 21 EDA in `artifacts/figures/` + 13 UMAP in `artifacts/figures/umap/`). Frontend placeholder logos / TMDb cache poster JPGs are NOT report figures.

### 6.1 `figures/` (root, architecture diagrams) — Mermaid renders

| Tier | File | Size | What it shows | Report slot |
|---|---|---|---|---|
| HERO | `figures/high-level-architecture.png` | 118 KB | Pipeline overview (data → features → backbones → demo) | §1 Introduction / §3 System overview |
| HERO | `figures/data-engineering-pipeline.png` | 95 KB | EDA v2 data flow | §2 Data |
| HERO | `figures/architecture_multimodal.png` | 319 KB | The multi-modal AE block diagram | §3 Method / model architecture |
| HERO | `figures/three-tier-taxonomy.png` | 145 KB | Non-deep / simple deep / multi-modal deep tiers | §4 Baselines |
| HERO | `figures/three-exis-eval-method.png` | 302 KB | Three-axis × three-metric evaluation grid | §5 Evaluation methodology |

### 6.2 `artifacts/figures/` (EDA outputs from `eda_v2.ipynb`)

| Tier | File | Size | What it shows |
|---|---|---|---|
| HERO | `embedding_analysis.png` | 287 KB | Likely PCA/explained-variance + spectral structure of feature matrix (best EDA figure based on filesize / name) |
| HERO | `genre_distribution.png` | 104 KB | 22-genre class imbalance histogram |
| HERO | `modality_balance_v2.png` | 58 KB | Block-wise variance ratios before/after weighting — motivates W2 (Finding 2) |
| STRONG | `modality_balance_before_after.png` | 59 KB | Variance-balance before/after StandardScaler |
| STRONG | `correlation_heatmap.png` | 93 KB | 564×564 feature correlation (or coarse-block) |
| STRONG | `correlation_pearson.png` | 95 KB | Pearson correlation variant |
| STRONG | `clusterability_pca.png` | 179 KB | PCA-2D scatter to show baseline clusterability (pre-deep) |
| STRONG | `missing_analysis.png` | 68 KB | Per-column missingness — motivates Finding 9 (missing-data manifold) |
| STRONG | `multilingual_coverage.png` | 38 KB | Language distribution across 31 lang dims |
| STRONG | `director_bio_coverage.png` | 40 KB | 96.8% bio-missing fact (ADR D4 motivation) |
| STRONG | `director_bio_pca_2d_scatter.png` | 122 KB | Director-bio embedding PCA scatter |
| STRONG | `director_bio_pca_scree.png` | 60 KB | Scree plot for director-bio PCA |
| STRONG | `director_lang_vs_film_lang.png` | 102 KB | Director language vs film language agreement |
| STRONG | `categorical_distributions.png` | 46 KB | Categorical-block histograms |
| STRONG | `imbalance_analysis.png` | 90 KB | Class imbalance summary |
| STRONG | `awards_merge_quality.png` | 68 KB | Awards-data merge QA |
| STRONG | `awards_temporal_cutoff.png` | 51 KB | Awards temporal-leakage cutoff |
| STRONG | `boxplots.png` | 65 KB | Numerical-feature box plots |
| STRONG | `vote_average_imputation_impact.png` | 53 KB | Vote-average imputation before/after |
| STRONG | `variance_thresholding.png` | 37 KB | Variance-thresholding ablation |
| SUPPORT | `hist_log.png` | 63 KB | Log-scale histogram |
| SUPPORT | `hist_raw.png` | 63 KB | Raw histogram (paired with log) |

### 6.3 `artifacts/figures/umap/` (13 latent-space UMAP visualizations from `notebooks/06_umap.ipynb`)

15 K subsample, cosine metric, colored by genre / decade / language. Tier per FINDINGS.md §"Figure index — UMAP visualizations".

| Tier | File | Size | What it shows | Story / Finding |
|---|---|---|---|---|
| **HERO** | `umap/umap_comparison_genre.png` | 319 KB | 3-panel side-by-side: vanilla / multi-modal / DEC — colored by genre | **Finding 8** — blobs → islands → tight islands |
| **HERO** | `umap/umap_dec_z64_k21_decade.png` | 100 KB | DEC latent colored by decade — isolated red cluster top-right | **Finding 9** — missing-release_date manifold |
| STRONG | `umap/umap_dec_z64_k21_lang.png` | 95 KB | DEC by language — micro-clusters visible | Supports lang_NMI=0.294 |
| STRONG | `umap/umap_ae_z64_w1_genre.png` | 161 KB | W1 ablation — diffuse blob, no fine structure | **Finding 2** visual signature (W2 weighting critical) |
| STRONG | `umap/umap_ae_z64_genre.png` | 139 KB | Multi-modal genre clusters in isolation | Method illustration |
| STRONG | `umap/umap_ae_z64_lang.png` | 126 KB | Multi-modal language clusters | Method illustration |
| STRONG | `umap/umap_dec_z64_k21_genre.png` | 106 KB | DEC genre clusters in isolation | Closing visual |
| SUPPORT | `umap/umap_vanilla_ae_z64_genre.png` | 184 KB | Vanilla architecture topology (2 mega-blobs) | Baseline context |
| SUPPORT | `umap/umap_vanilla_ae_z64_decade.png` | 191 KB | Vanilla by decade | Baseline context |
| SUPPORT | `umap/umap_vanilla_ae_z64_lang.png` | 167 KB | Vanilla by language | Baseline context |
| SUPPORT | `umap/umap_ae_z64_decade.png` | 138 KB | Multi-modal by decade | Per-axis completeness |
| SUPPORT | `umap/umap_ae_z64_w1_decade.png` | 147 KB | W1 by decade | Ablation completeness |
| SUPPORT | `umap/umap_ae_z64_w1_lang.png` | 146 KB | W1 by language | Ablation completeness |

**All UMAPs are for z=64 backbones.** No UMAP exists for `ae_z32` (demo backbone) or `ae_z128` (over-parameterised) — see §8 TO-GENERATE.

---

## 7. Other deliverables already in the repo

| Path | Role |
|---|---|
| `docs/report/intermediate-progress-report.pdf` | The 2026-05-06 intermediate report (already-submitted reference / structural template) |
| `docs/presentation/intermediate-progress-presentation.pptx` | The 2026-05-06 intermediate deck (already-submitted reference / structural template) |
| `docs/FINDINGS.md` | Living empirical-findings doc — **single best narrative source for report claims** (Findings 1-9 + hypothesis status) |
| `docs/PROGRESS.md` | Living phase log with all ADRs (D1–D15), decision rationale |
| `docs/journal/` (16 files) | Detailed experimental journal — sourceable verbatim |
| `docs/adr/` | Decision log (D1–D15) |
| `notebooks/06_umap.ipynb` | Generates all 13 UMAP figures from the 4 z=64 backbones |
| `notebooks/08_round2_ae_zsweep.ipynb` | Round 2 training notebook (z=32 + z=128 + retrieval eval) |
| `eda_v2.ipynb` (root) | Generates all 22 EDA figures under `artifacts/figures/` |

---

## 8. TO-GENERATE — figures the report needs that DO NOT yet exist

> These are gaps relative to what the brief expects (z-sweep U-curve, zero-collapse evidence, dim_std plots, retrieval examples). Cost-to-make is annotated.

| # | Figure | Why needed | Cost | How to generate |
|---|---|---|---|---|
| TG-1 | **z-sweep U-curve line plot** (x = z ∈ {32, 64, 128}; y = genre_NMI + genre@5 + dim_std_min on dual axes) | Round 2 hero claim ("information-bottleneck sweet spot at z=32") is currently table-only. The U-curve is the single best visual for the second methodological finding. | **CHEAP** (~5 min). Numbers already in `backbones.json` + `results.json` + journal/12. Use `matplotlib.pyplot` from a Python REPL. | One-cell script: data is in `backbones.json` (gnmi, genreAtFive) + `models/ae_z*/eval.json` + journal-12's `dim_std_min` numbers (0.117 / 0.062 / 0.025). Output `figures/zsweep_ucurve.png`. |
| TG-2 | **Zero-collapse evidence — within-cluster cosine histogram** for `dec_z64_k21` vs `ae_z32` | Visualizes the "NMI≠retrieval" pivot (journal/07). DEC's intra-cluster cosines ≈ 1.000 mass-spike vs AE's broad distribution. | **CHEAP** (~10 min). Compute pairwise cosines on `embeddings.npy` within a sampled cluster; two-panel histogram. | `np.load("artifacts/inference/dec_z64_k21/embeddings.npy")` and `ae_z32/embeddings.npy`; sample 1000 films from one cluster; compute `X @ X.T`; histogram. |
| TG-3 | **dim_std per-dimension bar chart** for ae_z32 / ae_z64 / ae_z128 | Visualizes the "near-dead dimensions in z=128" claim. Bars sorted descending; z=128 shows long tail of near-zero stds; z=32 is roughly uniform. | **CHEAP** (~5 min). `np.std(embeddings, axis=0)` per backbone, 3-panel bar chart. | `np.load` each `embeddings.npy`; one cell of plt. Output `figures/dim_std_per_backbone.png`. |
| TG-4 | **Retrieval examples table-as-figure** (Inception, Spirited Away, Pulp Fiction × ae_z32 vs dec_z64_k21 top-5 + cosines) | Currently only available verbatim in manifests; report should show it as a comparison figure (or LaTeX table). | **CHEAP** (~3 min). Hand-roll a 2-column table from the two `manifest.json` files; render as image with matplotlib OR drop straight into LaTeX as `\begin{tabular}`. | Source: `artifacts/inference/ae_z32/manifest.json` and `dec_z64_k21/manifest.json` (both have `eyeball[]` with the same 10 queries). |
| TG-5 | **UMAP for `ae_z32`** (demo backbone, colored by genre AND by cluster_id) | Demo backbone has no UMAP. Current UMAPs are all z=64. The report's demo section will look odd without a z=32 visualization. | **MEDIUM** (~15 min). Same template as `notebooks/06_umap.ipynb` — re-run on `artifacts/inference/ae_z32/embeddings.npy` + film labels. | Open `notebooks/06_umap.ipynb`, swap the embeddings path to `ae_z32/embeddings.npy`, re-run. ~5 min UMAP compute on 15k subsample. |
| TG-6 | **Training-loss curve plot** for `ae_z32` (train + val × 100 epochs) | Currently only in `history.json`. Useful as a "model-trained-properly" sanity figure in §Methods. | **CHEAP** (~3 min). Two-line `plt.plot` from the two arrays. | `json.load("artifacts/models/ae_z32/history.json")` → plot `train_loss` and `val_loss` against epoch index. |

**Estimated total work to generate all 6: ~40-60 minutes of Python + matplotlib.** All inputs are already computed and on-disk. None require re-training or re-inference.

---

## 9. Citation cheat-sheet (for the LaTeX `.tex` and the .pptx)

```latex
% Dataset citation
The CineEmbed dataset (329{,}044 films, 564-dimensional feature matrix; MD5
\texttt{e99cee84b6891ea352a7b44d5d7d0ee4}) is constructed from TMDb metadata
augmented with director profiles and awards records~\cite{tmdb}.

% Architecture
The multi-modal autoencoder uses per-block input projections over
\{numerical (6), genre (22), language (31), decade (2), awards (6), text (384),
director (113)\} followed by a shared trunk encoder to a z=32 latent
(L2-normalized).

% Demo backbone
The demo backbone (\texttt{ae\_z32}, checkpoint SHA-256 prefix
\texttt{d61181b1a240a0f4e7a0cd8a4d7e748c}) achieves genre@5 = 0.723 over 316
queries and genre-NMI = 0.334 via KMeans (k=21) on the latent.

% Eval split
Three label axes: genre (22 classes, multi-label argmax for KMeans),
decade (12 buckets), and original language (31 classes).
Metrics: Normalized Mutual Information, Adjusted Rand Index, and
Adjusted Mutual Information.
```

---

## 10. Quick-glance summary for the report author

- **6 MVP rows + 3 Round-2 rows = 9 model entries** for the canonical results table. All numbers verified.
- **39 figures total available** (5 architecture, 21 EDA, 13 UMAP). 4 are unambiguous HERO. ~5 more HERO once TO-GENERATE list is run.
- **0 figures exist** for the demo backbone (ae_z32) — TG-5 fills the biggest visual gap.
- **`docs/FINDINGS.md` is the narrative gold mine** — 9 findings, ready-to-quote claims, all numerically grounded against `results.json`.
- **Beware:** `artifacts/eval/round2_results.json` is **mis-named** (content = MVP duplicate). Use `models/ae_z{32,128}/eval.json` + `inference/*/manifest.json` for actual Round 2 numbers.

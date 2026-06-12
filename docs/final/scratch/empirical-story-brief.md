# CineEmbed — Empirical Story Brief for Final Report

> Source-verified synthesis from FINDINGS.md, the 13-file journal,
> ADR 0001 (D1–D15), the intermediate report (2026-05-06), the
> overnight UI-polish report (2026-05-19), and demo materials.
> Every number is traced to a file with line / section anchor.
> **Do not fabricate. If a number is missing here it was not in the source.**

---

## 0. Headline storyline (one paragraph)

CineEmbed is a multi-modal unsupervised film recommender over 329 044
TMDb films and a 564-dimensional feature matrix organised into seven
modality blocks. The project ran three empirical phases: an MVP that
validated all three pre-registered hypotheses (H1/H2/H3 PASS;
`dec_z64_k21` at `gNMI = 0.332`, +205% over the strongest non-deep
baseline); a clustering-improvements sprint whose contrastive-pretext
hero direction underperformed cold-start MVP baselines at every step
(Phase 1 and Round 1, both negative); and a Round 2 z-sweep that flipped
the deployed backbone from `dec_z64_k21` to `ae_z32` after two
methodological discoveries — first that NMI does not predict cosine
retrieval quality because DEC induces intra-cluster angular collapse
(top-5 cosines ≈ 1.000, journal/07), and second that the
information-bottleneck sweet spot for this matrix is z = 32, not z = 64,
producing a U-curve across z ∈ {32, 64, 128} (journal/12).
The deployed demo runs cosine retrieval over an L2-normalised
329 044 × 32 embedding matrix (~42 MB) with FastAPI + Next.js 16, and
the final report's strongest empirical claims are the +205% over the
non-deep baseline, the +178% language-NMI lift from modality-specific
projection, and the two methodological findings (F1: NMI ≠ retrieval,
F2: z = 32 sweet spot).

---

## 1. Five-act storyline (each 2-4 sentences)

### Act 1 — EDA & 564-dim feature matrix
The EDA v2 pipeline (2026-05-03/04) produced
`artifacts/feature_matrix.npz` of shape **(329 044, 564) float32**,
MD5 `e99cee84b6891ea352a7b44d5d7d0ee4`, with seven block-contiguous
modalities: `numerical` (6), `genre` (22), `language` (31), `decade`
(2), `awards` (6), `text` (384, `all-MiniLM-L6-v2`), and `director`
(113 = bio_pca_64 + has_director_bio + dir_lang_30 + dir_country_18 +
has_director_lang). The central data problem identified up front was
**modality variance imbalance ratio 0.046** between text/bio_pca and
the rest, which became the entire architectural motivation
(ADR 0001 Context section). Coverage notes: `has_director_bio` = 3.2%
(96.8% films lack a Wikipedia bio), `has_release_date` = 92.4%,
`has_genre` = 63.1%; awards merge rate ≈ 22%.

### Act 2 — MVP & three pre-registered hypotheses
Six pre-registered models trained at z = 64 on Colab T4 (~4 h
wallclock total), all single-seed = 42, 90/10 split, batch 1024,
patience 10 (intermediate report §3.3 / journal/01 §2). Result: H1
PASS marginal (DEC `gNMI = 0.332` > AE `gNMI = 0.328`, +1.2%),
H2 PASS by an order of magnitude (DEC vs `kmeans_raw_k21` 0.109,
**+205%** relative — the headline number in the intermediate report's
callout box), H3 PASS (0.332 ≫ 0.15 floor). DEC also won the marginal
NMI race but at a far larger gap on ARI (+6.6%) and lang_NMI (+11.4%) —
the diagnostic signature that DEC's contribution is **cluster
compactness, not new structural information**
(FINDINGS Finding 7).

### Act 3 — Phase 1 negative result (contrastive pretext)
Three SimCLR-style modality-dropout pretext configs (τ ∈ {0.1, 0.5},
`drop_prob` ∈ {0.3, 0.4}; wandb group `phase-1-sweep`; journal/04).
All three landed **below** the MVP `ae_z64` baseline on `geo_NMI`:
0.260 / 0.221 / 0.190 vs MVP `ae_z64` 0.309. Best Phase 1 by gNMI was
0.216 vs MVP 0.328, a **−34% gap** (journal/06 §2.2 / journal/04 §6).
Root cause (ND-1): modality-dropout augmentation forces the encoder
into block-invariance, and because the **genre block is itself one of
the dropped modalities**, the contrastive objective explicitly rewards
genre-invariance — the opposite of what `primary_genre` clustering
needs (journal/06 §2.3).

### Act 4 — Round 1 negative result + retrieval pivot
Round 1 added three configs at z = 64 (wandb `round-1`): `vae_z64`,
and two `dec_z64_k21_from_contrastive_t{0p1,0p5}` HERO candidates.
All three underperformed MVP carry-overs: `geo_NMI` 0.181 / 0.127 /
0.107 vs MVP `dec_z64_k21` 0.323 (journal/05 §4, journal/10
"Round 1" table). The DEC-vs-KMeans-on-AE-latent diagnostic (delta
≤ 0.005) proved the encoder, not the DEC step, was broken — the
contrastive pretext poisoned the encoder and AE/DEC fine-tune could
not recover (journal/05 §5, journal/06 §3.3). VAE z = 64 early-stopped
at epoch 12 with best_val_loss = 0.2727, consistent with posterior
collapse but **not falsified** because per-epoch KL/recon split was
not logged (ND-3, journal/06 §4.3). When the demo backbone selection
hit a near-tie on `geo_NMI` between `dec_z64_k21` (0.323) and `ae_z64`
(0.309), a retrieval sanity check (`scripts/build_index.py` →
`_retrieval_eval`, `_eyeball_top5`) revealed `dec_z64_k21`'s
intra-cluster cosines all saturate at 1.000 (top-5 cosines for
Inception: 0.99992, 0.99989, 0.99986, 0.99986, 0.99986;
journal/07 §3, journal/06 §5). **NMI ≠ retrieval. First
methodological finding locked.** Demo backbone first swapped to
`ae_z64` (genre@5 = 0.714 vs `dec_z64_k21`'s 0.557).

### Act 5 — Round 2 z-sweep & demo lock at `ae_z32`
Round 2 retargeted from DEC to AE family (per the journal/07 pivot;
wandb `round-2` offline). Cold-start AE at z ∈ {32, 64, 128}, same
recipe everywhere except `latent_dim` (journal/12 §2 / Round 2 table).
Result was a **U-curve in z, not "smaller is better"**: `ae_z32`
gNMI = 0.334, genre@5 = **0.723**; `ae_z64` gNMI = 0.328, genre@5 =
0.715; `ae_z128` gNMI = 0.273 (6-point collapse), genre@5 = 0.722
(ties z = 32 within noise but `dim_std_min = 0.025` shows a near-dead
dim and `pair_cos_std` narrows — angular-collapse precursor; journal/12
§9). Five independent signals favour z = 32 over z = 128 on the
tie-break: gNMI clearly, `dim_std_min` (0.117 vs 0.025), `pair_cos_std`
(0.301 vs 0.289), reconstruction loss (0.0223 vs 0.0237), and Occam
(smaller, faster inference, ~42 MB embeddings vs 168 MB for z = 128).
**Demo backbone locked at `artifacts/models/ae_z32/ae.pt`** (ADR D15,
2026-05-17 PM). **Second methodological finding locked: z = 32 is the
information-bottleneck sweet spot.**

---

## 2. The nine hero findings (verified against journal)

Each row reports the claim, the numeric evidence, and the supporting
figure path. All numbers cross-checked with FINDINGS.md, journal/01,
and the intermediate report.

### Finding 1 — Architecture's biggest win is on language (+178%)
- Multi-modal `ae_z64` lang_NMI = 0.264 vs vanilla concat-AE 0.095 →
  **+178% relative**. genre_NMI +14% (0.328 vs 0.287), decade_NMI
  −7.6% (0.341 vs 0.369).
- **Mechanism:** vanilla concat-AE's single FC encoder under-represents
  low-frequency one-hot blocks; language is 31 sparse dims with ~99%
  zero per row.
- **Spec criterion D1:** ≥ 5% gain — PASS at +14% (genre), +178%
  (language).
- **Figure:** `artifacts/figures/umap/umap_ae_z64_lang.png` (distinct
  language micro-clusters visible). Cited as `fig:umap-ae-lang` in the
  intermediate report.
- **Source:** FINDINGS.md L55–66, intermediate report §3.3
  "Architecture-level evidence", journal/01 §3.

### Finding 2 — W2 inverse-variance weighting is critical (asymmetric collapse)
- W2 vs W1 (uniform): gNMI 0.328 → 0.165 (**−50%**), lang_NMI 0.264 →
  0.070 (**−73%**); decade_NMI 0.341 → 0.367 (+8%, unaffected).
- **Asymmetric collapse:** small blocks (decade, 2 dims) survive uniform
  weighting because StandardScaler already gave per-feature var ≈ 1;
  large high-dim blocks (text 384, lang 31) lose all gradient signal.
- Model-health signal: W1 early-stopped at **epoch 37** (patience
  exhausted), W2 ran 69 epochs.
- **Spec criterion D3:** W2.NMI > W1.NMI × 1.05 — PASS at +99% (genre),
  +277% (lang).
- **Figure:** `artifacts/figures/umap/umap_ae_z64_w1_genre.png` (diffuse
  blobs vs W2's micro-clusters).
- **Source:** FINDINGS.md L67–78, intermediate report §3.3
  ("Inverse-variance weighting is critical"), journal/01 §2.5 §3.

### Finding 3 — Reconstruction loss ≠ clustering quality
- `vanilla_ae_z64`: val_loss = **0.0126** (lowest), gNMI = 0.287.
  `ae_z64`: val_loss = 0.0208 (higher), gNMI = **0.328** (highest).
- **Claim:** multi-modal trades minor reconstruction fidelity for
  substantially better latent structure — the classic "useful
  representation vs perfect copy" tension.
- **Source:** FINDINGS.md L79–84.

### Finding 4 — Decade is the strongest natural axis (~0.35 NMI universal)
- All three architectures (vanilla, multi-modal, W1) hit decade_NMI ≈
  **0.34–0.37** regardless of architecture.
- **Implication:** decade is single-valued and ordinal — KMeans gets
  it for free. Genre (multi-label, overlapping) is harder.
- **Source:** FINDINGS.md L86–91, journal/01 §3 ("decade is the easy
  axis"), ADR Lessons-learned bullet 1.

### Finding 5 — Pareto trade-off across axes (no architecture wins all six metrics)
- Vanilla wins decade_NMI (0.369) + genre_ARI (0.247); multi-modal
  wins decade_ARI (0.211); DEC wins genre_NMI (0.332), lang_NMI
  (0.294), lang_ARI (0.090).
- **Claim:** modality-specific projection allocates capacity to
  text/director blocks, slightly reducing fidelity on the
  trivially-encoded decade signal. **Principled trade-off, not a bug.**
- This Pareto pattern is the motivation for the `geo_NMI` composite
  metric introduced in ADR D13 (W&B integration 2026-05-09).
- **Source:** FINDINGS.md L92–100, intermediate report Table 1
  (the bolded winners), journal/01 §3.

### Finding 6 — Deep models outperform non-deep baselines by 3–5× (H2 massively PASS)
- DEC vs `kmeans_raw_k21`: genre_NMI **+205%** (0.332 vs 0.109);
  genre_ARI **+287%** (0.244 vs 0.063); lang_NMI **+292%** (0.294 vs
  0.075). DEC vs `pca_kmeans_k21`: gNMI +295% (0.332 vs 0.084).
- **Three-tier framing** (FINDINGS.md L114–118): non-deep baseline
  ≈ 0.08–0.11 → simple deep `vanilla_ae` 0.287 → multi-modal deep
  0.328–0.332. PCA-64+KMeans is **worse than raw-KMeans on genre**
  because PCA discards genre-discriminative variance.
- **Spec criterion D9 / H2:** best_deep > best_non_deep × 1.10 —
  PASS at +205%. The intermediate report's strongest single claim
  (headline box on page 1, executive summary).
- **Source:** FINDINGS.md L101–119, intermediate report Executive
  Summary callout.

### Finding 7 — DEC sharpens cluster boundaries (ARI > NMI improvement pattern)
- DEC (k=21, init from `ae_z64` encoder, 21 KL+recon epochs):
  gNMI +1.2% (0.328 → 0.332), gARI **+6.6%** (0.229 → 0.244),
  lang_NMI **+11.4%** (0.264 → 0.294), decade flat.
- **Claim:** DEC contributes compactness, not new structural
  information. ARI gain > NMI gain is the diagnostic signature —
  partition is more crisp at the same information level.
- **Cluster health:** `total_reinit = 0` across 21 DEC epochs — all
  21 KMeans++ centroids survived KL training without collapse
  (non-trivial; DEC implementations frequently see 1–4 collapses).
- **Source:** FINDINGS.md L120–138, intermediate report §3.3 ("DEC
  sharpens cluster boundaries"), journal/01 §2.6.

### Finding 8 — Latent topology evolves: blobs → islands → tight islands
- Visual signature across the architecture progression
  (UMAP, 15K subsample, cosine metric):
  - `vanilla_ae_z64` — **2 mega-blobs** dominated by an "Unknown-genre"
    blue mass.
  - `ae_z64` multi-modal W2 — **dozens of small genre-coherent
    islands**.
  - `dec_z64_k21` — **even more atomized, tighter islands** with
    sharper inter-cluster gaps.
  - `ae_z64_w1` — mid-sized blobs, **no fine genre structure**.
- **Hero figure:** `artifacts/figures/umap/umap_comparison_genre.png`
  — the 3-panel side-by-side.
- **Source:** FINDINGS.md L139–156, intermediate report
  `fig:umap-comparison`.

### Finding 9 — Films with missing release_date form a coherent sub-manifold
- ~7.4% of films have `decade_bin = 0` (~1112 of 15 000 subsample,
  red). They form a clearly isolated cluster in the upper-right
  across all four architectures; **DEC compresses them most
  explicitly**. The model was not forced to encode missingness —
  `has_release_date` is one of 564 inputs — but the latent geometry
  surfaces it anyway.
- **Post-hoc discovery**, not predicted by H1–H3.
- **Hero figure:**
  `artifacts/figures/umap/umap_dec_z64_k21_decade.png`.
- **Source:** FINDINGS.md L157–168, intermediate report §3.3
  ("Bonus finding"), journal/01 §3 bullet 5.

---

## 3. Negative results (ND-1, ND-2, ND-3) with concrete numbers

Source for all three: `docs/journal/06-negative-results.md` (the
"Negative Findings and Limitations" primary source).

### ND-1 — Phase 1 contrastive pretext underperformed spec's +5–12% lift
- **Claim from spec:** clustering-improvement spec §2.1 promised
  +5–12% NMI lift after 30–60 epochs of pretext, citing TCSS / SCAN
  family / sgSDC 2024–2025 deep-clustering literature.
- **Observed (Phase 1, 3 configs, journal/06 §2.2):**
  | Run | tau | drop_prob | gNMI | dNMI | lNMI | geo_NMI |
  |---|---:|---:|---:|---:|---:|---:|
  | `contrastive_tau0p5_drop0p3` | 0.5 | 0.3 | 0.216 | 0.218 | 0.374 | 0.260 |
  | `contrastive_tau0p1_drop0p3` | 0.1 | 0.3 | 0.216 | 0.286 | 0.174 | 0.221 |
  | `contrastive_tau0p1_drop0p4` | 0.1 | 0.4 | 0.150 | 0.243 | 0.189 | 0.190 |
  | MVP `ae_z64` baseline | — | — | 0.328 | 0.341 | 0.264 | **0.309** |
- **Gap:** best Phase 1 by gNMI (0.216) is **−34%** below MVP `ae_z64`
  (0.328); best Phase 1 by `geo_NMI` (0.260) is −16% below.
- **Root cause:** modality-dropout augmentation makes the encoder
  invariant to dropped block content; **the genre block is itself one
  of the dropped modalities**, so InfoNCE explicitly trains the
  encoder to be genre-invariant — opposite of the downstream
  clustering objective on `primary_genre`. Image-domain SimCLR
  augmentations (crop, jitter) do not strip the target class; modality
  dropout on tabular data does. (journal/06 §2.3)
- **Falsifying evidence (cross-confirmation):** Round 1 HERO RUNs
  cannot recover the signal, confirming the encoder-level cause
  (ND-2 below).
- **Secondary observation:** τ = 0.5 had higher lNMI (0.374) than
  τ = 0.1 (0.174); plausibly "lazy" encoder grabs the easy 31-dim
  language one-hot signal under looser contrast. **Single data
  point; not over-claimed** (journal/06 §2.4).

### ND-2 — Round 1 AE→DEC fine-tune from contrastive backbones underperformed MVP DEC
- **Claim:** each HERO RUN should beat MVP `dec_z64_k21` (gNMI = 0.332,
  geo_NMI = 0.323) by 5–12% NMI.
- **Observed (journal/06 §3.2):**
  | Run | gNMI | dNMI | lNMI | geo_NMI | KMeans-on-AE-latent gNMI | DEC-vs-KMeans delta |
  |---|---:|---:|---:|---:|---:|---:|
  | `dec_z64_k21_from_contrastive_t0p5` | 0.098 | 0.487 | 0.125 | 0.181 | 0.098 | 0.000 |
  | `dec_z64_k21_from_contrastive_t0p1` | 0.120 | 0.641 | 0.016 | 0.107 | 0.119 | +0.001 |
  | MVP `dec_z64_k21` | 0.332 | 0.342 | 0.294 | **0.323** | — | — |
- **Gap:** HERO RUNs land **−44% to −67% below baseline** on
  `geo_NMI`; **−63% to −70%** on gNMI.
- **Diagnostic that proved the encoder, not the DEC step, was broken:**
  DEC-vs-KMeans-on-AE-latent delta is **≤ 0.001** for both fine-tunes
  — DEC was doing exactly what it should; the contrastive pretext
  had already destroyed the genre signal before DEC saw a batch
  (journal/05 §5, journal/06 §3.3).
- **Why fine-tune couldn't recover:** the early SGD trajectory is
  dominated by the genre-invariant contrastive features. W2
  reconstruction MSE on a near-zero target (multi-label 21-dim genre
  block) does not strongly penalise zero predictions, and W2 clips
  weights at [0.1, 10.0] — the genre block contributes at most ~10×
  the per-dim weight of baseline. Without an explicit genre-aware
  fine-tune signal, the encoder stays in the contrastive basin.
- **Three remediation directions** (journal/06 §3.5): augmentations
  that do not touch the target modality (e.g. Gaussian noise on
  numerical only); two-objective pretext (contrastive + supervised
  genre classification); or a different augmentation primitive
  (TabClusterNet / MMCMAE) — all out of scope.

### ND-3 — VAE z = 64 likely posterior collapse (strong but not falsified)
- **Observed:** `vae_z64` early-stopped at **epoch 12** with
  best_val_loss = **0.2727**. gNMI = 0.103, dNMI = 0.358, lNMI =
  0.056, geo_NMI = **0.127** — below every MVP baseline including
  non-deep ones. Decade is the only axis with signal — the easy
  continuous decade-norm feature punches through (journal/06 §4.1,
  journal/05 §4).
- **Config:** β_max = 0.1 with 10-epoch linear warmup, lr = 1e-3,
  z = 64. Patience = 10, exhausted at epoch 12 (val curve flat after
  ~epoch 2) — the model spent only ~2 epochs at full β before patience
  ran out.
- **Hypothesis:** posterior collapse (Bowman 2015, Razavi 2019). KL
  term in ELBO drives `q(z|x) → N(0,I)`, latent encodes nothing.
  W2 inverse-variance scheme clips block weights at [0.1, 10.0]
  which limits how strongly any block can override KL.
- **Caveat (journal/06 §4.3):** per-epoch recon vs KL split was
  **not logged** — diagnostic absent. Status: strong but
  **not falsified**. Alternative explanations not ruled out:
  too-aggressive lr (VAE often needs 1e-4 or 5e-4), schedule mismatch
  with patience counter, decoder under-capacity given 154-dim concat
  target.
- **Consequence:** the original two-round spec ("if VAE wins, do
  z = 32 / 128 in Round 2") was triggered as a no-op. VAE z-sweep
  explicitly skipped (journal/08 §2.A "VAE z-sweep cut").

---

## 4. The two methodological findings (unique to this project)

### F1 — NMI ≠ retrieval quality (the angular-collapse story)
- **Locked:** 2026-05-17 AM. Source: `docs/journal/07-retrieval-vs-nmi-discovery.md`
  (full long-form narrative) + `docs/journal/06-negative-results.md` §5
  (failure-mode angle, ND-4).
- **Discovery:** `dec_z64_k21` has the **highest** geo_NMI of any model
  (0.323) and the **lowest** cosine retrieval quality
  (`genre@5 = 0.557`) among demo-candidate backbones — a 22-point gap
  below `ae_z64` (0.714). Caught accidentally by the `_retrieval_eval`
  function added to `scripts/build_index.py:236` as a deploy sanity
  check.
- **Concrete evidence — top-5 cosines saturated at ≈ 1.000**
  (`artifacts/inference/dec_z64_k21/manifest.json`):
  | Query | Top-5 cosines |
  |---|---|
  | Inception | 0.99992, 0.99989, 0.99986, 0.99986, 0.99986 |
  | The Godfather | 0.99994, 0.99993, 0.99992, 0.99991, 0.99990 |
  | The Shawshank Redemption | 0.99999, 0.99999, 0.99998, 0.99998, 0.99998 |
  | The Matrix | 0.99999, 0.99999, 0.99999, 0.99999, 0.99999 |

  Difference between top-1 and top-5 ≤ 1e-4 — the **floating-point
  precision floor at fp32**. The cluster (~15–17k films) is
  effectively a single point in cosine space.
- **By contrast, `ae_z64`** top-5 cosines span 0.93–0.99
  (Inception: 0.969 / 0.966 / 0.961 / 0.952 / 0.951 — Interstellar,
  Avengers AoU, Avengers, Dark Knight Rises, Dunkirk). Eyeball
  comparison especially decisive on Spirited Away: ae_z64 gives
  4/5 Studio Ghibli (Mononoke, Nausicaä, Pom Poko, Kiki's); DEC gives
  Cowboy Bebop / Ghost in the Shell / Big Nothing — wrong cluster.
- **Mechanism (journal/07 §5):** DEC objective is
  `L = KL(P‖Q) + λ_recon · L_recon` with `λ_recon = 0.1` and Student-t
  kernel `q_ij ∝ (1+||z_i - μ_j||²)^(-1)`. KL pulls intra-cluster
  vectors toward the cluster centroid; through the Student-t kernel
  this manifests as cosine-1 alignment within a cluster. NMI is
  **blind to intra-cluster geometry** (only sees cluster-ID agreement);
  cosine retrieval depends **entirely** on intra-cluster geometry.
- **The paradox (journal/07 §3):** DEC has wider random-pair cosine
  spread (`random_pair_cos_std` = 0.421 vs ae_z64 0.299) — looks
  *healthier* at pair-level — but within any single cluster the
  vectors are angularly identical. **Collapse is cluster-local, not
  global**, so the random-pair sanity stat *under*-detects the
  failure. The eyeball test was decisive.
- **Process lesson (journal/07 §8):** when the project's deliverable
  changed (web-app pivot 2026-05-16), the inherited NMI selection
  metric should have been re-audited. It wasn't, and we **nearly
  deployed the wrong backbone**.

### F2 — Information-bottleneck sweet spot at z = 32 (U-curve)
- **Locked:** 2026-05-17 PM. Source:
  `docs/journal/12-z-sweep-ae-z32-discovery.md` (full long-form) +
  ADR D15. First written down in journal/12 §1 and §9.
- **Setup:** Round 2 cold-start AE at z ∈ {32, 64, 128}, **identical
  recipe everywhere except `latent_dim`** (hidden_dim = 128 held
  constant, batch 512, lr 1e-3 AdamW, seed 42, patience 10, max 100
  epochs — journal/12 §2). The §9 forecast predicted z = 32 vs
  z = 128 outcomes; reality landed between Outcomes 2 and 3.
- **Three-way sweep table (raw):**
  | z | gNMI | dNMI | lNMI | geo_NMI | genre@5 mean | genre@5 median | pair_cos_std | dim_std_mean | dim_std_min | best_val_loss |
  |---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
  | **32** | **0.334** | 0.295 | 0.216 | 0.277 | **0.723** | 1.000 | 0.301 | 0.146 | 0.117 | 0.0223 |
  | 64 | 0.328 | 0.341 | 0.264 | **0.309** | 0.715 | 0.800 | 0.299 | 0.101 | 0.062 | ~0.024 |
  | 128 | 0.273 | 0.275 | 0.272 | 0.274 | 0.722 | 0.800 | 0.289 | 0.069 | **0.025** | 0.0237 |
- **U-curve evidence (journal/12 §9):** gNMI peaks at z = 32 (0.334),
  drops slightly at z = 64 (0.328), then **collapses 6 points at
  z = 128 (0.273)**. `dim_std_min = 0.025` at z = 128 = near-dead
  latent dim; `pair_cos_std` narrows (early angular-collapse warning,
  same family of pathology as F1).
- **z = 128 ties z = 32 on `genre@5` within noise (0.722 vs 0.723)** —
  re-confirming the F1 finding that NMI does not predict retrieval.
  Tiebreak by Occam (smaller model wins) → z = 32.
- **Interpretation (journal/12 §5 §9):** halving the latent forces
  the encoder to **concentrate capacity on high-entropy modalities**
  (384-d text overview, 113-d director PCA) and **demote redundant
  ones** (decade 2-d, language 31-d) — which the decoder can already
  recover from the input. z = 128 sits past the sweet spot in the
  other direction — no compression pressure, dim allocation diffuses,
  gNMI collapses. Connects to information-bottleneck theory: optimal
  representation dim is task-dependent and matches the
  intrinsic-information rate of the labels, not the raw input dim.
- **Concrete eyeball lift over `ae_z64` (journal/12 §4):**
  Inception → Dark Knight at top-1 cos 0.991 (vs ae_z64's
  Interstellar at 0.969); Spirited Away → 4/5 Studio Ghibli at top-1
  cos 0.993 (ae_z64 had Battle Royale outlier); Shawshank → Cool Hand
  Luke + Midnight Express (prison sub-theme); Pulp Fiction →
  Kill Bill 2 (Tarantino signature recovered). Trade-off
  (journal/12 §6): dNMI drops 13% relative, lNMI drops 18% relative
  — composite `geo_NMI` lower at z = 32 (0.277 vs z = 64's 0.309),
  but the demo task is genre/retrieval, where z = 32 wins.

---

## 5. ADR D1–D15 condensed (one sentence each)

Source: `docs/adr/0001-modeling-hybrid-architecture.md`.

| ID | Date | Decision (one line) |
|---|---|---|
| **D1** | 2026-05-04 | Hybrid C-structure × D-architecture — three model heads (AE, VAE, DEC) share a multi-modal projection backbone — chosen because the 0.046 modality variance ratio is THE central data problem and hybrid addresses it architecturally while giving a controlled comparison framework. |
| **D2** | 2026-05-04 | Latent dim ablation grid z ∈ {32, 64, 128} — 22 genre classes × ~3 dim/class → 64 is the sweet spot a priori; sweep validates. |
| **D3** | 2026-05-04 | Loss weighting: W2 inverse-variance with clipping [0.1, 10.0] as main, W1 uniform as ablation, W4 Kendall as optional stretch — addresses heterogeneous block variances. |
| **D4** | 2026-05-04 | G2 director-bio masking — bio_pca reconstruction loss masked by `has_director_bio` because 96.8% of films lack a bio; otherwise gradient is wasted on constant-zero targets. |
| **D5** | 2026-05-04 | Per-model notebooks + shared `src/cineembed/` package — enables 3-person team parallelism and DRY backbone. |
| **D6** | 2026-05-04 | Tier-2 evaluation suite — per-block recon MSE, total weighted MSE, three-axis NMI/ARI, UMAP × 3 colorings; linear probing + F1/F2 modality ablations as Tier-2 add-ons. |
| **D7** | 2026-05-04 | L4 ground truth — three orthogonal axes (primary_genre, decade, lang_top10) rather than single-axis genre, because single axis loses latent-structure story. |
| **D8** | 2026-05-04 | DEC k-sweep {10, 21, 30} — single k is a lucky-guess risk; sweep distinguishes encoder quality from k-sensitivity (later collapsed to k = 21 only in MVP). |
| **D9** | 2026-05-04 | Peer-review pass 1 — added 3 vanilla baselines (kmeans_raw, pca_kmeans, vanilla_ae_z64), relative + absolute-floor success criteria, W2 weight clipping, β warmup for VAE; without controls the multi-modal claim is unfalsifiable. |
| **D10** | 2026-05-04 | Peer-review pass 2 — canonical `weighted_recon_loss` (no double-count), 90/10 split for early-stop, batch-wise DEC P target (~10× speedup, no quality regression), Colab install path fix. |
| **D11** | 2026-05-06 | Clustering-improvement sprint — five techniques landed in commit `8097685`: InfoNCE pretext, per-axis-k eval, GMM/spectral/HDBSCAN, AMI keys, multi-label macro-NMI; 68/68 tests pass. |
| **D12** | 2026-05-16 | Per-row block masking (not per-batch scalar) + InfoNCE default τ 0.5 → 0.1 — per-row prevents batch co-adaptation; lower τ sharpens contrastive objective on denser tabular signal. |
| **D13** | 2026-05-16 | Two-round modeling strategy supersedes the 21–22 run exhaustive ablation — Round 1 architecture comparison @ z = 64 (9 rows) + Round 2 z-sweep on Round-1 winner (3 rows); selection metric `geo_NMI = (gNMI·dNMI·lNMI)^(1/3)`; ~80% compute saving. |
| **D14** | 2026-05-16 | Final deliverable pivots to web app demo (FastAPI + static frontend over L2-normalised cosine on the deployed backbone), not a pure report — re-prioritises remaining work order to models → inference → API → frontend → polish. |
| **D15** | 2026-05-17 | Demo backbone locked at `artifacts/models/ae_z32/ae.pt` after Round 2 z-sweep revealed a U-curve (not monotonic); five independent signals (gNMI, dim_std_min, pair_cos_std, recon loss, Occam) all favour z = 32; second methodological finding of the project. |

---

## 6. Round 2 z-sweep raw table

z ∈ {32, 64, 128} × {gNMI, genre@5 mean, dim_std_min}. Plus full
companion columns for the report.

| z | gNMI | dNMI | lNMI | geo_NMI | genre@5 mean | genre@5 median | pair_cos_std | dim_std_mean | dim_std_min | best_val_loss |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **32** | **0.334** | 0.295 | 0.216 | 0.277 | **0.723** | 1.000 | 0.301 | 0.146 | 0.117 | 0.0223 |
| 64 | 0.328 | 0.341 | 0.264 | **0.309** | 0.715 | 0.800 | 0.299 | 0.101 | 0.062 | ~0.024 |
| 128 | 0.273 | 0.275 | 0.272 | 0.274 | 0.722 | 0.800 | 0.289 | 0.069 | **0.025** | 0.0237 |

Three-axis reading:
- **gNMI** peaks at z = 32 (0.334), drops slightly at z = 64 (0.328),
  collapses 6 pts at z = 128 (0.273) — U-curve / sweet spot at z = 32.
- **genre@5** essentially flat across z = 32 (0.723) and z = 128
  (0.722); z = 64 slightly lower (0.715). Genre@5 measures local
  neighbourhood, not global geometry — re-confirms NMI ≠ retrieval.
- **dim_std_min** monotonically decreasing 0.117 → 0.062 → 0.025 —
  z = 128 has near-dead dimensions; latent capacity is wasted.

Source: `docs/journal/10-results-table.md` Round 2 section, journal/12 §9.

---

## 7. Writing style / voice notes (from the intermediate report)

The intermediate report (`docs/report/intermediate-progress-report.tex`,
2026-05-06) sets the established voice; the final report should
extend, not break, this tone.

### Academic tier
- Self-described as **"half-academic"** — between a bare demo writeup
  and a full ablation paper (D14 web-app pivot moved scope from
  "research paper" to "demo + grounded report").
- Posture is **project status report**, not research paper
  (verbatim from `docs/archive/specs/2026-05-06-intermediate-progress-report-design.md`
  §3): "Past tense for completed phases ... present-progressive for
  in-progress work ... future tense for planned work. Third-person
  where natural ('the team verified', 'evaluation produced') rather
  than first-person plural ('we discovered'). The empirical results
  from the modeling MVP appear as evidence of work completed, not as
  research findings."
- For the final report, the F1/F2 methodological findings will likely
  push the tone toward "research findings" register in the analysis
  section while the rest stays project-status. Pre-state the
  two-family metric framing (clustering + retrieval) in the
  methodology so the eventual disagreement isn't a surprise
  (journal/11 §9 recommendation).

### Paragraph length
- Short, single-claim paragraphs (typically 2–6 sentences). Every
  paragraph either makes a claim or provides evidence for one.
- Heavy use of `\noindent\textbf{Bold lead-in.}` for sub-claims inside
  a section, e.g. `\noindent\textbf{Modality projection wins on
  language ($+178\%$).}` followed by 2–3 sentences of evidence.
- Numbers in claims always anchored to the supporting table or figure
  (e.g. `+178\% ... \cref{fig:umap-ae-lang}`).
- `\noindent\evidence{...}` macro is used to tag the source artifacts
  at the bottom of each subsection.

### Subsection conventions
- Three-level structure: `\section{...}` (Roman section,
  brandPrimary orange), `\subsection{...}` (subsection, brandSecondary
  blue), `\subsubsection*{...}` (unnumbered, e.g. "Main results",
  "Headline result --- H2", "Architecture-level evidence",
  "Latent-topology evolution", "Bonus finding").
- Numbered sections used in TOC; `\subsubsection*` always starred
  (unnumbered) — keeps the navigation tree clean.
- Custom callout boxes (`tcolorbox`):
  - `headlinebox` — orange `\bignumber{+205\%}` on the left with
    a `\raggedleft` minipage on the right. Used for the single
    biggest claim of the report (executive summary callout).
  - `riskbox` — amber-bordered, titled risk callouts.
- `\status{complete|inprogress|planned|deferred}` macro renders
  colour-coded badges; used throughout the milestone tables and
  deliverables list.

### Citation style
- `biblatex` with `style=numeric, sorting=none` (citation order
  preserved as encountered). `[1]`–`[7]` numeric superscript
  citations.
- All citations live in `references.bib`; resolved bibliography in
  `intermediate-progress-report.bbl`.
- Bibliography heading is just **"References"** (`\printbibliography
  [heading=bibintoc, title={References}]`); appears in TOC.

### Section structure (intermediate report, for reuse)
The intermediate report has 7 sections + 2 appendices (and the
final report should mirror this with the new sections folded into
3 and a new analysis section for F1 + F2):
1. Project Overview (goal, scope, team)
2. Schedule and Milestones (Gantt + milestone status table)
3. Work Completed to Date (data engineering / architecture design /
   modeling MVP — each with `\status{complete}` and `\evidence{...}`)
4. Work In Progress (this document + UMAP writeup at the time)
5. Plan to Final Report (deferred-work table with owners and dates)
6. Risks and Mitigation (3 risk boxes)
7. Deliverables Status (artifacts and locations)
   + Appendix A — Per-Run Numerical Results
   + Appendix B — Decision Log Summary (D1–D10 originally; final
     report should extend to D15)

### Colour palette (brand consistency)
- `brandPrimary` = `#C2410C` (orange) — section headings, big
  numbers, primary tables.
- `brandSecondary` = `#2563EB` (blue) — subsection headings,
  hyperlinks, "PLANNED" status badge.
- `brandAccent` = `#15803D` (green) — "COMPLETE" badge, Gantt
  milestones.
- `brandAmber` = `#B45309` — risk callouts, "IN PROGRESS" badge.
- `brandSlate` = `#64748B` — DEFERRED badge, footer text, evidence
  prefix.
- `rowAlt` = `#F8FAFC`, `nearBlack` = `#1E293B`.

The final report should reuse these macros and styles; the LaTeX
preamble at the top of `intermediate-progress-report.tex` is the
canonical starting point.

---

## 8. Reference list (verified from `.bib` and `.bbl`)

Seven citations in the intermediate report's `references.bib`. All
verified against the resolved `intermediate-progress-report.bbl`
(`% biblatex bbl format version 3.3`). None look suspicious; none
are self-cited.

| # | Cite key | Title | Authors | Venue | Year | Notes |
|---|---|---|---|---|---|---|
| 1 | `reimers2019sbert` | Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks | Reimers, Gurevych | EMNLP | 2019 | Used for `all-MiniLM-L6-v2` overview embeddings and director-bio embeddings. |
| 2 | `gorishniy2021tabular` | Revisiting Deep Learning Models for Tabular Data | Gorishniy, Rubachev, Khrulkov, Babenko | NeurIPS 34 | 2021 | Justification for modality-specific projection layers. |
| 3 | `xie2016dec` | Unsupervised Deep Embedding for Clustering Analysis | Xie, Girshick, Farhadi | ICML 33 (pp. 478–487) | 2016 | DEC objective (KL(P‖Q) + soft Student-t assignment). |
| 4 | `guo2017idec` | Improved Deep Embedded Clustering with Local Structure Preservation | Guo, Gao, Liu, Yin | IJCAI 26 (pp. 1753–1759) | 2017 | DEC + reconstruction grounding (the `λ_recon · L_recon` term). |
| 5 | `paszke2019pytorch` | PyTorch: An Imperative Style, High-Performance Deep Learning Library | Paszke, Gross, Massa, Lerer, Bradbury, Chanan, Killeen, Lin, Gimelshein, Antiga, *et al.* | NeurIPS 32 | 2019 | Framework citation. |
| 6 | `pedregosa2011sklearn` | Scikit-learn: Machine Learning in Python | Pedregosa, Varoquaux, Gramfort, Michel, Thirion, Grisel, Blondel, Prettenhofer, Weiss, Dubourg, Vanderplas, Passos, Cournapeau, Brucher, Perrot, Duchesnay | JMLR 12 (pp. 2825–2830) | 2011 | KMeans / NMI / ARI / AMI implementations. |
| 7 | `mcinnes2018umap` | UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction | McInnes, Healy, Melville | arXiv preprint arXiv:1802.03426 | 2018 | UMAP projection for the latent-topology figures. |

**Flagged for the final report (citations needed but not yet in
`references.bib`):**
- **Chen et al. 2020** ("A Simple Framework for Contrastive Learning
  of Visual Representations" — SimCLR) — needed for the Phase 1
  InfoNCE pretext discussion and the ND-1 root-cause argument
  (cited inline in journal/04 and journal/06 but not yet in `.bib`).
- **Vinh et al. JMLR 2010** ("Information Theoretic Measures for
  Clusterings Comparison" — AMI bias correction) — needed for the
  AMI rationale in journal/02 §2.4 and journal/11 §2; flagged in
  journal/11 §9 as a citation to add.
- **Bowman et al. 2015** ("Generating Sentences from a Continuous
  Space") and **Razavi et al. 2019** ("Preventing Posterior Collapse
  with delta-VAEs") — referenced in the ND-3 posterior-collapse
  discussion (journal/06 §4.2) but not yet in `.bib`.
- **Kendall and Gal 2018** ("Multi-Task Learning Using Uncertainty to
  Weigh Losses ...") — referenced in ADR D3 / W4 stretch goal
  rationale; cite if W4 ablation is mentioned in the final report.
- **Tishby et al.** — information-bottleneck — referenced in
  journal/12 §7 as the theoretical framing for F2. Should be cited
  if the report leans on the "compression as regularisation" reading.

No fabricated or suspicious citations were found in the existing
`.bib`; all seven resolve to legitimate, well-known publications
in the deep-learning / clustering / tabular-data literatures.

---

## 9. Cross-reference index for the report writer

If the final report needs to verify any single claim, the source
hierarchy is:

1. **`docs/FINDINGS.md`** — short-form claims, all 9 hero findings.
2. **`docs/adr/0001-modeling-hybrid-architecture.md`** — D1–D15
   decision rationale.
3. **`docs/journal/10-results-table.md`** — every run × every metric
   in one place (master comparison + Phase 0/1, Round 1/2,
   retrieval-eval blocks).
4. **`docs/journal/00-context-and-goals.md`** — definitions and
   timeline.
5. **`docs/journal/01-mvp-modeling-phase.md`** — MVP runs detail.
6. **`docs/journal/04-phase1-contrastive-sweep.md`** — Phase 1
   negative.
7. **`docs/journal/05-round1-architecture-comparison.md`** — Round 1
   negative + diagnostic that pinpointed encoder failure.
8. **`docs/journal/06-negative-results.md`** — ND-1 to ND-4 with
   root causes.
9. **`docs/journal/07-retrieval-vs-nmi-discovery.md`** — F1 long-form.
10. **`docs/journal/11-metrics-deep-dive.md`** — every metric chosen
    and why.
11. **`docs/journal/12-z-sweep-ae-z32-discovery.md`** — F2 long-form.
12. **`docs/report/intermediate-progress-report.tex`** — voice / style
    reference.
13. **`artifacts/inference/{ae_z32,ae_z64,ae_z128,dec_z64_k21}/manifest.json`**
    — ground truth for `genre@5` and the eyeball comparisons.

Last verified: 2026-05-19 14:10 GMT+3.

# CineEmbed — Project Progress Log

> **Living document.** Updated after each task completes. Source of truth for "where are we".
> If this document and TaskList disagree, trust the git log.

**Last updated:** 2026-05-04
**Current phase:** Modeling MVP (intermediate report)
**Course:** SENG 474 — Spring 2026 · TED University
**Team:** Baran Dinçoğuz, Arda Arvas, Kaan Kaya

---

## High-level project state

| Phase | Status | Artifacts | Notes |
|---|---|---|---|
| EDA v1 (original notebook) | ✅ Complete | `Deep_Learning_EDA_*.ipynb` | Untouched, slides reference it |
| **EDA v2** (production pipeline) | ✅ Complete | `eda_v2.ipynb` (75 cells, 27 commits) | MD5 `e99cee84b6891ea352a7b44d5d7d0ee4` |
| EDA v2 extension (director profile) | ✅ Complete | folded into `eda_v2.ipynb` | (329044, 564) feature matrix |
| **Modeling MVP** (intermediate report) | 🔄 In progress | T1-T12p (see below) | This is what we're doing now |
| Modeling Full (final report) | ⏸ Deferred | T9 full + T10 + T11 full + T12 full + T13 | After intermediate |
| Final report writing | ⏸ Pending | LaTeX/Word doc | Drives from `artifacts/eval/results.json` |
| Slides + presentation | ⏸ Pending | `.pptx` | Last step |

---

## Modeling MVP scope (intermediate report deliverable)

The full implementation plan has 13 tasks producing 21-22 model runs. The MVP scope cuts this to **~10 tasks producing 5 runs**, sufficient for an intermediate report with preliminary results.

### Active MVP tasks

| # | Task | Description | Effort | Status |
|---:|---|---|---|---|
| 1 | T1 | Package skeleton + pyproject.toml + test_import | ~15 min | ✅ Done (`44309ee`) |
| 2 | T2 | `data.py` — load + block indices + labels + dataloader | ~30 min | ✅ Done (`22a8abf`) |
| 3 | T3 | `losses.py` — W2 + G2 + ELBO + DEC KL + W4 | ~30 min | ✅ Done (`ed8c71d`) |
| 4 | T4 | `backbone.py` — MultiModalBackbone + block_mask | ~20 min | ✅ Done (`2c4e6f6`) |
| 5 | T5 | `heads.py` — AEHead, VAEHead, DECHead with re-init | ~30 min | ✅ Done (`da021c2`) |
| 6 | T6 | `train.py` — generic loop with epoch-aware loss_fn | ~20 min | ✅ Done (`152c462`) |
| 7 | T7 | `eval.py` — KMeans/DEC assignments, NMI/ARI L4, probing, UMAP | ~30 min | ✅ Done (`4e67a42`) |
| 8 | T8 | `01_smoke_test.ipynb` — package validation | ~10 min | ✅ Done (`faebe1f`) |
| 9 | **T9p** | **Partial AE: vanilla_ae_z64 + ae_z64 + ae_z64_w1** (3 runs) | ~45 min Colab | ✅ Written (`58563cf`); awaits Colab run |
| 10 | **T11p** | **Partial DEC: dec_z64_k21** (1 run) | ~10 min Colab | ✅ Written (`8f7b8f2`); awaits Colab |
| 11 | **T12p** | **Partial results: KMeans baselines + comparison table** | ~20 min | ✅ Written (`928c3d4`); awaits 02+04 |

**MVP estimated total:** ~3 saat dev (T1-T8) + ~1 saat Colab compute (T9p+T11p) + ~30 min results (T12p) = **~4-5 hours wall-clock**.

**MVP-only run count:** 5 model runs:
- KMeans on raw 564-dim (instant)
- PCA(64)+KMeans (instant)
- vanilla concat-AE z=64 (~15 min)
- multi-modal AE z=64 (~15 min)
- AE z=64 with W1 uniform weighting ablation (~15 min)
- DEC z=64 k=21 (~10 min)

That's enough for a 3×3 preliminary results table (3 baselines + 3 deep models × 3 axes).

---

## Deferred to "Modeling Full" (post-intermediate, final report)

What gets cut from the MVP and added back for the final:

### T9 deferred parts
- `ae_z32`, `ae_z128` (the 32-dim and 128-dim AE runs)
- `ae_z64_no_text` (F1 ablation — text modality removed)
- `ae_z64_no_director` (F2 ablation — director modality removed)
- `ae_z64_w4` (optional W4 Kendall stretch)

### T10 entirely deferred
- `vae_z32`, `vae_z64`, `vae_z128` (3 VAE runs with β warmup)

### T11 deferred parts
- `dec_z32_k10`, `dec_z32_k21`, `dec_z32_k30`
- `dec_z64_k10`, `dec_z64_k30`
- `dec_z128_k10`, `dec_z128_k21`, `dec_z128_k30`
- (8 of 9 DEC runs deferred; only k=21 z=64 done in MVP)

### T12 deferred parts
- 27 UMAP figures (all main runs × all axes)
- Linear probing for VAE / all DEC runs
- Ablation deltas across all F1/F2/W4 runs
- Full 30-cell results table

### T13 entirely deferred
- Reproducibility verification (two-run MD5 check)
- Tag `modeling-v1` after final integration

**Total deferred work for final:** 16 additional model runs + extended evaluation. Estimated ~4-5 hours additional Colab compute + ~3-4 hours dev for results notebook polish + report writing.

---

## Path to final report

Once MVP is delivered (intermediate report submitted):

1. **Run remaining 16 model trainings on Colab** (~4-5 hours):
   - 2 AE × {z=32, z=128}
   - 2 ablations: F1 (no_text), F2 (no_director)
   - 3 VAE × {z=32, z=64, z=128}
   - 8 DEC remaining (z={32, 128} × k={10, 21, 30}, z=64 × k={10, 30})
   - Optional W4 Kendall stretch (1 run)

2. **Extend `05_results.ipynb`** (~1-2 hours):
   - Generate all 27 UMAP figures
   - Linear probing on all z=64 models
   - Compute all ablation deltas
   - Build the full 3×3×3 + ablation results table

3. **Reproducibility audit** (~30 min):
   - Re-run any 1 training cell with same seed → check NMI ± 0.02
   - Tag `modeling-v1`

4. **Final report writing** (~1-2 days):
   - Methodology section: spec §4-§8 + ADR D1-D10
   - Results section: full table + best-of-each UMAPs (12 main figures)
   - Discussion: which hypotheses validated/falsified
   - Limitations: ablation findings

5. **Slide deck** (~1 day):
   - 12 slides max
   - Hero figure: results table or best UMAP
   - Architecture diagram (from spec §4)

---

## Key decisions and references

| Question | Answer | Source |
|---|---|---|
| Why this architecture? | Multi-modal backbone solves modality-imbalance (variance ratio 0.046) at architectural level | ADR D1 |
| Why these 3 latent dims? | 22 genres × 3 dim/class capacity → z=64 sweet spot, sweep validates | ADR D2 |
| Why W2 weighting? | Without it, text/bio dims get no gradient signal | ADR D3 |
| Why bio masking? | 96.8% bio missing → without mask, loss dominated by zero-vector reconstruction | ADR D4 |
| Why per-model notebooks? | Team parallelism (Baran→AE, Arda→VAE, Kaan→DEC), DRY backbone | ADR D5 |
| Why three eval axes? | Single axis (genre) leaves ambiguity about decade/lang structure | ADR D7 |
| Why k-sweep? | Single k = lucky guess; sweep distinguishes encoder quality from k-sensitivity | ADR D8 |
| Why baselines? | Multi-modal claim is unfalsifiable without controls (peer review D9) | ADR D9 |
| Why batch-wise DEC P? | Standard pragmatic approximation (peer review D10) | ADR D10 |

**Where to look for context:**
- Implementation contract: `docs/superpowers/specs/2026-05-04-modeling-design.md`
- Decision log: `docs/adr/0001-modeling-hybrid-architecture.md`
- Implementation plan: `docs/superpowers/plans/2026-05-04-modeling-implementation.md`
- EDA spec: `docs/superpowers/specs/2026-05-03-eda-v2-design.md`
- This progress doc: `docs/PROGRESS.md` (always start here)

---

## Session log (append-only)

### 2026-05-04 — MVP scope kickoff
- Spec finalized (676 lines, ADR D1-D10)
- Implementation plan written (3171 lines after 5 peer-review patches)
- MVP scope decided after second peer review: 11 tasks, 5 model runs
- Subagent-driven execution chosen (sonnet model)
- Starting T1 next

### 2026-05-04 — T1 complete
- Package skeleton built: `pyproject.toml`, `src/cineembed/__init__.py`, `tests/conftest.py` (6 fixtures), `tests/test_import.py`
- `.venv` set up with Python 3.13.3, `pip install -e ".[dev]"` succeeded
- pytest: 1 passed (test_import)
- Pyright unused-import diagnostic on `pd` fixed in amend
- Commit: `44309ee`
- Next: T2 (data.py)

### 2026-05-04 — Migrated to GitHub + git-clone Colab pattern
- Repo pushed to https://github.com/barandincoguz/CineEmbed-
- Notebooks refactored: code via `git clone` in Colab, artifacts only in Drive
- `00_drive_setup.ipynb` → `00_colab_setup.ipynb` (renamed)
- `MyDrive/cineembed_artifacts/` (flat, no repo/ subfolder)
- Setup cell now: `git clone` if missing, `git pull` if exists, then `pip install -e`
- All 4 notebooks parse cleanly, pushed to GitHub
- Commit: `1086e0a`

### 2026-05-04 — Drive-direct workflow refactor
- User feedback: drag-drop / zip-unzip dance is painful for repeated Colab sessions
- New layout: `MyDrive/cineembed/{repo,artifacts}` — repo + artifacts both live on Drive
- Created `notebooks/00_drive_setup.ipynb` (5 cells) — one-time helper that mounts, verifies 12 required files, creates models/eval dirs, installs package
- Updated setup cell in `02_train_ae`, `04_train_dec`, `05_results` — replaced zip-unpack with direct Drive paths + `assert REPO_ROOT.exists()` guard
- `01_smoke_test.ipynb` left untouched (local-only)
- All notebooks parse cleanly
- Commit: `ef21d66`

### 2026-05-04 — T11p + T12p complete (write-only)
- `notebooks/04_train_dec.ipynb`: 8 cells, MVP scope = 1 run (`dec_z64_k21`)
- `notebooks/05_results.ipynb`: 6 cells, preliminary intermediate-report results table
- Both notebooks parse cleanly, follow 02_train_ae.ipynb's `get_ipython().system()` pattern
- Each notebook has commented-out cells for the deferred final-report runs
- 05_results includes a "narrative" cell that auto-checks: best deep vs best baseline rel gain, W2 vs W1, multi-modal vs vanilla — i.e., 3 of the spec's success criteria
- Commits: `8f7b8f2` (DEC), `928c3d4` (results)
- **All MVP code is written.** Next step is the user's Colab runs.

### 2026-05-04 — T9p complete (write-only)
- `notebooks/02_train_ae.ipynb`: 9 cells, scoped to 3 MVP runs (vanilla_ae_z64, ae_z64, ae_z64_w1)
- Cell 8 + 9 document and contain commented-out code for the 4 deferred runs (ae_z32, ae_z128, F1, F2, optional W4)
- Bug catch: `!pip install` magic replaced with `get_ipython().system()` for syntax validity
- All 7 code cells parse cleanly
- Commit: `58563cf`
- **TODO: User runs in Colab** (~45 min T4 compute)
- Next: T11p+T12p bundle (DEC notebook + results notebook, both write-only)

### 2026-05-04 — T8 complete
- `notebooks/01_smoke_test.ipynb`: 8 cells, end-to-end package validation
- Verified locally: AE 126k params, VAE 135k, DEC 127k; all losses non-NaN; KMeans on AE latent gives sensible (near-zero) NMI vs random labels
- Cells run in <1 min on Mac CPU
- Commit: `faebe1f`
- Next: T9p (partial AE training notebook — write only, run in Colab)

### 2026-05-04 — T7 complete
- `eval.py`: cluster_assignments_kmeans, cluster_assignments_dec, evaluate_run (3-axis L4 NMI/ARI), linear_probe, umap_plot (Agg backend)
- `tests/test_eval.py`: 4 tests
- pytest: **30 passed** (1 + 5 + 8 + 5 + 5 + 2 + 4); 1 harmless umap warning
- Pyright: type-ignore on KMeans n_init + umap import (no bundled stubs)
- Commit: `4e67a42`
- All 7 modules (data, losses, backbone, heads, train, eval) DONE — all unit tests passing
- Next: T8 (01_smoke_test.ipynb) for end-to-end package validation

### 2026-05-04 — T5+T6 bundle complete
- `heads.py`: AEHead (deterministic), VAEHead (μ/σ + reparameterization), DECHead (Student-t kernel + reinit_collapsed_centers D10 patch)
- `train.py`: train_model with auto-detected `accepts_epoch` via inspect.signature (β warmup support), early stopping, checkpoint save/load
- pytest: **26 passed** (1 + 5 + 8 + 5 + 5 + 2)
- Pyright fixes: `# type: ignore[arg-type]` on KMeans n_init (sklearn-stubs lag), unused-import cleanup
- heads.py: changed absolute `from cineembed.backbone` → relative `from .backbone` for cleaner package internals
- Pyright noise on `from cineembed import X` persists but is IDE-only — runtime + pytest fully working
- Commits: `da021c2` (heads), `152c462` (train)
- Next: T7 (eval.py)

### 2026-05-04 — T3+T4 bundle complete
- `losses.py`: compute_block_weights (with clipping), director_block_loss (G2 mask), weighted_recon_loss (canonical), weighted_recon_loss_uniform (W1), vae_elbo (β-aware), dec_loss (batch-wise P), LearnedWeightedLoss (W4)
- `backbone.py`: MultiModalBackbone with block_mask support, DEFAULT_PROJ_DIMS at module level
- `tests/test_losses.py`: 8 tests (incl. exclude_blocks regression test)
- `tests/test_backbone.py`: 5 tests (incl. block_mask test)
- pytest: **19 passed** (1 + 5 + 8 + 5)
- Pyright fix: tensor-typed accumulators in `weighted_recon_loss` and `LearnedWeightedLoss.forward` (avoid `Tensor | Literal[0]` and `Tensor | float` unions)
- Pyright noise: `from cineembed import losses/backbone` shows "unknown import symbol" until language server re-indexes — IDE-only, runtime fine
- Commits: `ed8c71d` (losses), `2c4e6f6` (backbone)
- Next: T5+T6 bundle (heads.py + train.py)

### 2026-05-04 — T2 complete
- `data.py`: load_feature_matrix, get_block_indices (director-priority classifier), get_labels (3 axes), train_val_split, lazy-indexed _BlocksDataset, make_dataloader
- `tests/test_data.py`: 5 tests, all passing
- pytest: **6 passed** (1 import + 5 data)
- Diagnostic fixes in amend: removed unused `json`, `pytest` imports; `_column_or_default` helper for type-safe DataFrame col access; converted lang_top10 to ndarray; added `pyrightconfig.json` with `extraPaths: ["src"]`
- Plan deviation noted: lang_top10 type changed Series→ndarray; test updated to use `np.unique()` instead of `.unique()`
- Commit: `a0484a6`
- Next: T3+T4 bundle (losses.py + backbone.py)

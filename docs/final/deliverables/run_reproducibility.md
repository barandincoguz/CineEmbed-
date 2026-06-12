# Reproducibility — CineEmbed

This file explains how to reproduce every empirical claim, figure, and the live demo from a fresh clone.

## 1. Environment

```bash
git clone https://github.com/barandincoguz/CineEmbed-.git
cd CineEmbed-
git checkout main                                  # final-submission branch
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,demo,wandb]"                 # ~3 min
cd frontend && pnpm install && cd ..               # ~2 min
```

Pinned interpreter versions (see `artifacts/pipeline_version.json`):
- Python 3.11+
- PyTorch 2.10.0 (CUDA 12.8 for training, CPU is sufficient for inference)
- numpy 2.0.2, pandas 2.2.2, scikit-learn 1.6.1, umap-learn 0.5.12
- sentence-transformers 5.4.1
- Node 22+, pnpm 9+

Optional credentials (only needed for live TMDb posters in the demo — system runs fine without):

```bash
cp .env.example .env                              # edit: TMDB_API_KEY=<v3 key>
# OR TMDB_ACCESS_TOKEN=<v4 bearer token>
```

## 2. Run the test suite

```bash
pytest -q                                          # 107 tests, ~25 s
```

All tests should pass. If `test_data.py::test_load_feature_matrix_md5` fails on the feature-matrix MD5 check, see `verification_notes.md` §6 — the npz container's byte MD5 differs from the canonical at-creation MD5 in `pipeline_version.json` due to zip-archive metadata; logical contents are identical.

## 3. Reproduce the deployed embedding index

```bash
# Demo backbone (the one served by the API)
python scripts/build_index.py \
    --checkpoint     artifacts/models/ae_z32/ae.pt \
    --feature-matrix artifacts/feature_matrix.npz \
    --output-dir     artifacts/inference/ae_z32/ \
    --batch-size     1024 \
    --eval-mode      retrieval \
    --eval-queries   316
```

Output (positional row-index invariant: `films.parquet[i]` ↔ `embeddings.npy[i]`):

- `embeddings.npy` (329,044 × 32, float32, L2-normalised) ~42 MB
- `films.parquet` (id, title, year, director, genres, …) ~80 MB
- `cluster_labels.npy` (MiniBatchKMeans k=21, seed 42) ~329 KB
- `cluster_meta.json` (21 auto-named clusters)
- `manifest.json` (provenance, retrieval stats, 10 eyeball queries × top-5)

Repeat with `ae_z64` / `ae_z128` checkpoints to regenerate the comparison indices.

## 4. Reproduce the four final-report figures

```bash
python scripts/generate_final_figures.py
```

Outputs into `docs/final/deliverables/figures/`:

- `zsweep_ucurve.png`              — Round 2 U-curve over z ∈ {32, 64, 128}
- `cosine_collapse_histogram.png`  — top-5 cosine distribution: `ae_z32` vs `dec_z64_k21`
- `dim_std_per_backbone.png`       — per-dimension std bar chart, 3 panels
- `training_curves.png`            — ae_z32 (100 epochs) vs ae_z128 (53 epochs)

All four are deterministic at seed = 42.

## 5. Rebuild the presentation

```bash
python scripts/build_final_presentation.py
# Output: docs/final/deliverables/final_presentation.pptx (23 slides)

# Convert to PDF for projection
/Applications/LibreOffice.app/Contents/MacOS/soffice \
    --headless --convert-to pdf \
    docs/final/deliverables/final_presentation.pptx \
    --outdir docs/final/deliverables/
```

## 6. Launch the live demo

```bash
bash scripts/dev-up.sh                             # one-shot
# → backend  uvicorn cineembed.api:app   on :8000
# → frontend Next.js 16 dev server       on :3000
open http://localhost:3000
```

Health-check:

```bash
curl -s http://localhost:8000/api/health | jq .
# {"status":"ok","backbones_loaded":["ae_z32","ae_z64","ae_z128"],
#  "n_films":329044,"tmdb_key_configured":true}

curl -s 'http://localhost:8000/api/films/search?q=inception&limit=3' | jq '.[0] | {id, title, year}'
```

## 7. Reproduce the training runs (Colab T4 budget)

Round 2 z-sweep — the empirical work that drove ADR D15 — is the smallest reproducible window into the modelling pipeline. Open `notebooks/08_round2_ae_zsweep.ipynb` in Colab and run all cells; total wallclock ≈ 35 minutes on a free-tier T4.

To rerun the MVP (six Phase-0 runs):

```bash
# In Colab, in order:
notebooks/00_colab_setup.ipynb          # one-time git clone + install
notebooks/01_smoke_test.ipynb           # 5-min sanity
notebooks/02_train_ae.ipynb             # vanilla + multi-modal AE
notebooks/03_train_contrastive.ipynb    # Phase-1 contrastive (negative result, ND-1)
notebooks/04_train_dec.ipynb            # DEC fine-tune
notebooks/05_results.ipynb              # results.json compile
notebooks/06_umap.ipynb                 # 13 UMAP figures
notebooks/07_round1_finetune.ipynb      # Round-1 negative results (ND-2, ND-3)
notebooks/08_round2_ae_zsweep.ipynb     # Round-2 (this is what locked ae_z32)
```

Total: ~6 hours of T4 wallclock end-to-end.

## 8. Reset / clean

```bash
rm -rf docs/final/deliverables/slide_renders        # JPG cache
rm  docs/final/deliverables/final_presentation.pdf  # PDF cache
# Trained models live under artifacts/models/ and should NOT be deleted —
# they are the source of every empirical claim in the report.
```

## 9. Known environment assumptions

- macOS + LibreOffice for the .pptx → PDF conversion; on Linux replace with
  `libreoffice --headless --convert-to pdf …`. On Windows, install LibreOffice
  and use `soffice.exe`.
- The deployed demo backbone (`ae_z32`) is the only one needed for the live web
  app. The MVP and over-parameterised backbones (`ae_z64`, `ae_z128`,
  `dec_z64_k21`) are retained purely as ablation evidence.
- The TMDb credentials are optional. Without them, the frontend gracefully
  falls back to deterministic gradient cards in place of posters; the API still
  serves all 8 endpoints.

## 10. Failure modes

- **First run is slow** — the initial API request triggers a one-time prewarm
  matmul on the 42 MB embedding matrix (forces the OS page cache to load).
  Subsequent requests are sub-millisecond.
- **Colab session ends mid-training** — W&B integration is offline-safe; resume
  by re-running the notebook. Checkpoints save atomically via temp-file rename.
- **`pnpm install` fails on the frontend** — fall back to `npm install` or
  `yarn install`; package-lock.json / yarn.lock are not committed but the
  dep graph in package.json is exact.

## 11. Repository state at submission

| Subsystem | State |
|---|---|
| Code (`src/cineembed/`) | 12 modules; 107-test pytest suite passes |
| Notebooks | 9 notebooks, run order 00 → 08 |
| Scripts | `build_index.py`, `train_contrastive.py`, `backfill_wandb.py`, `dev-up.sh`, `setup-teammate.sh`, `package-artifacts.sh`, `generate_final_figures.py`, `build_final_presentation.py` |
| Frontend | Next.js 16.2.6 + React 19 + Tailwind v4 + shadcn + TanStack Query 5 + Zod |
| Artifacts | 4 backbones × `{embeddings.npy, films.parquet, cluster_*, manifest.json}` |
| Documentation | `docs/FINDINGS.md`, `docs/PROGRESS.md`, `docs/adr/0001-*.md`, `docs/journal/` (13 files), `docs/report/intermediate-progress-report.{tex,pdf}`, `docs/presentation/intermediate-progress-presentation.pptx`, this `docs/final/deliverables/` tree |

*End of reproducibility recipe.*

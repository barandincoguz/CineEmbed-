# CineEmbed

**Multimodal representation learning and similarity search over 329,044 films.**

CineEmbed compresses a **564-feature multimodal movie representation** into compact latent embeddings and exposes those embeddings through a working **FastAPI + Next.js** discovery application for similarity search, cluster exploration, and model comparison.

**Course:** SENG 474 — Spring 2026 · TED University  
**Team:** Baran Dinçoğuz, Arda Arvas, Kaan Kaya  
**Status:** Completed · final project artifacts archived in June 2026

---

## At a glance

| | |
|---|---|
| **Corpus** | 329,044 films |
| **Input representation** | 564 engineered multimodal features |
| **Selected demo backbone** | `ae_z32` |
| **Embedding size** | 32 dimensions, L2-normalized |
| **Retrieval** | cosine similarity / dot product after L2 normalization |
| **Measured retrieval quality** | `genre@5 = 0.7228` over 316 evaluation queries |
| **Inference index** | ~42 MB for the 329,044 × 32 float32 embedding matrix |
| **Available comparison backbones** | `ae_z32`, `ae_z64`, `ae_z128` (+ archived DEC artifacts) |
| **Application** | FastAPI backend + Next.js/React frontend |

The selected `ae_z32` manifest records 329,044 films, 32-dimensional L2-normalized embeddings, cosine retrieval, and a mean `genre@5` of **0.7228** over 316 queries.

---

## Why this project exists

Movie recommendation is usually framed as a supervised ranking problem. CineEmbed explores a different question:

> **Can heterogeneous movie metadata be compressed into a useful latent space without requiring recommendation labels?**

The project combines representation learning, clustering, retrieval evaluation, and a full-stack demo. The model does not simply memorize titles; it learns a compact representation from multiple metadata blocks and uses nearest-neighbour search in the resulting latent space.

The engineering work spans the full path from experimentation to a usable application:

```text
movie metadata
    ↓
feature engineering / normalization
    ↓
564-dimensional multimodal matrix
    ↓
AE / VAE / DEC / contrastive experiments
    ↓
model selection by clustering + retrieval evidence
    ↓
32-dimensional L2-normalized embeddings
    ↓
cosine similarity over 329,044 films
    ↓
FastAPI
    ↓
Next.js discovery interface
```

---

## The main methodological result

The project changed direction after the evaluation criteria were expanded beyond clustering scores.

The early clustering champion, `dec_z64_k21`, looked strong under NMI-based evaluation but produced a near-collapsed retrieval geometry. It was therefore **rejected as the demo backbone** rather than promoted because it won one metric.

The subsequent AE latent-dimension sweep produced a more useful retrieval space. `ae_z32` became the final demo backbone and is retained alongside `ae_z64` and `ae_z128` for comparison.

This is the main lesson of the project:

> **A representation that clusters well is not automatically a representation that retrieves useful neighbours. Model selection must match the downstream task.**

---

## What the application provides

The final repository contains a working backend and frontend rather than only notebooks.

### Film discovery

Search for a film and retrieve nearest neighbours from the learned embedding space.

### Similar-film retrieval

The active backbone performs cosine search over the in-memory L2-normalized embedding matrix.

### Cluster exploration

The interface exposes learned groupings and representative films. The cluster view uses `k=21` MiniBatchKMeans over normalized embeddings for exploration.

### Backbone comparison

The application keeps multiple AE embedding spaces so the same query can be inspected under different latent dimensions rather than treating one model choice as unquestionable.

### Retrieval gallery

Curated queries make qualitative differences between backbones inspectable alongside quantitative metrics.

### Application pages

The Next.js application contains five primary views:

- `/` — search and similarity retrieval;
- `/cluster` — cluster overview;
- `/cluster/[k]` — individual cluster exploration;
- `/gallery` — cross-backbone retrieval examples;
- `/about` — methodology and findings.

---

## Architecture

### Modeling layer

The reusable Python package under `src/cineembed/` includes:

- multimodal backbone construction;
- Autoencoder and VAE heads;
- Deep Embedded Clustering components;
- contrastive / InfoNCE experiments;
- generic training loops;
- NMI, ARI and AMI evaluation;
- per-axis clustering analysis;
- GMM, spectral and HDBSCAN research utilities;
- optional Weights & Biases tracking.

### Retrieval layer

The selected checkpoint is precomputed over the complete film matrix. Embeddings are L2-normalized once, then similarity search is a matrix-vector product:

```text
scores = embeddings @ query_embedding
```

For `ae_z32`, the stored matrix is `329044 × 32` float32 values — roughly **42 MB** — so brute-force cosine search is practical without introducing a vector database or FAISS dependency for this dataset size.

### API layer

The FastAPI service loads the prepared inference artifacts and exposes film search, film metadata, nearest-neighbour retrieval, clusters, and supporting demo data.

### Frontend

The final interface is implemented with **Next.js 16, React 19, TypeScript, Tailwind CSS, TanStack Query, Radix/shadcn-style components**, and supporting UI libraries.

---

## Quick start

### 1. Clone

```bash
git clone https://github.com/barandincoguz/CineEmbed-.git
cd CineEmbed-
```

### 2. Install Python dependencies

```bash
pip install -e ".[demo]"
```

For research/development tooling as well:

```bash
pip install -e ".[dev,wandb,demo]"
```

### 3. Install frontend dependencies

```bash
cd frontend
pnpm install
cd ..
```

### 4. Optional TMDb configuration

```bash
cp .env.example .env
```

Add a TMDb API key if poster/backdrop enrichment is desired. The core embedding search does not depend on TMDb.

### 5. Start the application

```bash
bash scripts/dev-up.sh
```

The launcher starts:

```text
FastAPI   http://localhost:8000
Next.js   http://localhost:3000
```

The backend health endpoint is available at `/api/health`.

---

## Reproducing the inference artifacts

The repository keeps the inference pipeline separate from model training.

```bash
python scripts/build_index.py --checkpoint artifacts/models/<checkpoint>.pt
```

The final repository contains inference directories for:

```text
artifacts/inference/
├── ae_z32/
├── ae_z64/
├── ae_z128/
├── dec_z64_k21/
├── gallery.json
└── cluster_names_override.json
```

Each model-specific directory carries the artifacts required by the application and a manifest describing the representation and retrieval setup.

---

## Example: `ae_z32`

The tracked `ae_z32` manifest provides an auditable snapshot of the final retrieval representation:

```text
films:          329,044
latent dim:     32
normalization:  L2
distance:       cosine
queries:        316
genre@5 mean:   0.7228
genre@5 median: 1.0
```

Its qualitative checks include queries such as **Inception**, **The Godfather**, **Toy Story**, **Pulp Fiction**, **The Matrix**, and **Spirited Away**, with their stored top-neighbour results.

---

## Experimental path

CineEmbed intentionally retains negative results because they explain why the final model was selected.

### Phase 0 — baseline and deep clustering

The initial experiment suite compared classical and deep representations, including raw/PCA clustering, autoencoders and DEC.

### Contrastive track

A contrastive pretext stage was implemented and evaluated. The tested configurations underperformed the strongest cold-start AE representation, so contrastive learning was **not** carried forward simply because it was more complex.

### Architecture comparison

VAE and contrastive-initialized DEC experiments were also evaluated. VAE showed posterior-collapse behaviour and contrastive-initialized DEC inherited the weaker representation.

### Retrieval pivot

A retrieval evaluation exposed the mismatch between the earlier clustering winner and the actual recommendation-style use case. This invalidated `dec_z64_k21` as the production demo representation.

### Latent-dimension sweep

The AE family was then compared at 32, 64 and 128 dimensions. The final application locks the default representation to `ae_z32` while preserving the other backbones for comparison.

---

## Reproducibility

The research pipeline was built around repeatable experiments:

- global random seed `42` across NumPy, PyTorch and scikit-learn;
- deterministic train/validation split with `random_state=42`;
- tracked model checkpoints and inference manifests;
- feature-matrix fingerprinting;
- W&B integration for experiment history;
- evaluation artifacts stored under `artifacts/`;
- design and architecture decisions documented under `docs/`.

Feature matrix fingerprint recorded by the project:

```text
MD5: e99cee84b6891ea352a7b44d5d7d0ee4
```

---

## Repository map

```text
src/cineembed/          reusable modeling, evaluation and API package
frontend/               Next.js / React application
notebooks/              Colab-oriented experiment notebooks
scripts/                training, index building, enrichment and launch tools
artifacts/models/       tracked model checkpoints / model outputs
artifacts/inference/    deployable embedding artifacts and manifests
artifacts/eval/         experiment evaluation results
docs/                   progress logs, findings, ADRs, reports and design records
tests/                  Python test suite
```

Useful entry points:

- [`docs/PROGRESS.md`](docs/PROGRESS.md) — chronological research decisions and modeling state;
- [`docs/FINDINGS.md`](docs/FINDINGS.md) — empirical findings;
- [`docs/adr/0001-modeling-hybrid-architecture.md`](docs/adr/0001-modeling-hybrid-architecture.md) — architecture decision record;
- [`docs/report/intermediate-progress-report.pdf`](docs/report/intermediate-progress-report.pdf) — submitted intermediate report;
- [`artifacts/inference/ae_z32/manifest.json`](artifacts/inference/ae_z32/manifest.json) — final selected embedding manifest.

---

## Scope and limitations

CineEmbed is a university deep-learning project and research/demo system, not a production recommender trained on user interaction histories.

- Similarity is learned from movie metadata rather than collaborative user feedback.
- `genre@5` is a useful retrieval diagnostic, not a universal measure of recommendation quality.
- Some large source/intermediate artifacts are intentionally not stored in Git because of their size.
- TMDb enriches the presentation layer but is not part of the representation-learning claim.
- The project keeps failed and superseded model paths because they are part of the evidence behind the final design.

---

## Project timeline

The current Git repository begins on **4 May 2026** with the initial project structure and records final project artifacts on **12 June 2026**.

The result is a complete path from **multimodal feature engineering → deep representation learning → model selection → retrieval evaluation → FastAPI/Next.js application**, with the experimental decisions preserved alongside the final demo.

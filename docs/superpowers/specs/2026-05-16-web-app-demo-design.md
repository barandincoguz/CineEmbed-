# Web App Demo — Design Spec

**Date:** 2026-05-16
**Status:** APPROVED
**Deadline:** 2026-05-20
**Cross-ref:** ADR `0001-modeling-hybrid-architecture.md` D14;
`docs/superpowers/specs/2026-05-16-two-round-modeling-strategy.md`

---

## 1. Motivation

The SENG 474 final deliverable is a **working web app**, not just a report.
A live cosine-similarity recommender over the 64-dim latent embeddings is the
clearest possible empirical demonstration that the multi-modal architecture
produced a meaningful representation — vastly more compelling than a static
NMI table.

The demo is intentionally minimal: one model checkpoint (Round-2 winner),
one numpy file of pre-computed embeddings, three REST endpoints, a single
static HTML page. Everything runs on a laptop with no GPU.

---

## 2. API contract

FastAPI app exposed at `cineembed.api:app`. JSON over HTTP. All endpoints
read from in-RAM artifacts loaded at startup.

### 2.1 `GET /api/films/search`

Query-string search by title prefix / substring.

**Request:**

```
GET /api/films/search?q=blade&limit=10
```

| Param | Type | Default | Notes |
|---|---|---|---|
| `q` | str (required) | — | Case-insensitive substring match on title |
| `limit` | int | 10 | Max results |

**Response (200):**

```json
{
  "query": "blade",
  "results": [
    {"id": 78,    "title": "Blade",          "year": 1998},
    {"id": 36586, "title": "Blade Runner",   "year": 1982},
    {"id": 335984, "title": "Blade Runner 2049", "year": 2017}
  ]
}
```

### 2.2 `GET /api/films/{id}/similar`

Top-N nearest neighbours by cosine over the L2-normalized z=64 latent.

**Request:**

```
GET /api/films/335984/similar?top=5
```

| Param | Type | Default | Notes |
|---|---|---|---|
| `id` | int (path) | — | TMDb id, must exist in `films.parquet` |
| `top` | int (query) | 5 | One of 2 / 5 / 10 (UI tier) |

**Response (200):**

```json
{
  "query_id": 335984,
  "query_title": "Blade Runner 2049",
  "results": [
    {"id": 78, "title": "Blade Runner", "year": 1982, "similarity": 0.913},
    {"id": 1726, "title": "Iron Man", "year": 2008, "similarity": 0.802},
    ...
  ]
}
```

`similarity` is the cosine in [-1, 1]; for L2-normalized embeddings this is
the dot product.

**Errors:**

- `404` if `id` not in `films.parquet`.

### 2.3 `GET /api/films/random`

Random films, used as UI cold-start and a "surprise me" affordance.

**Request:**

```
GET /api/films/random?n=12
```

| Param | Type | Default | Notes |
|---|---|---|---|
| `n` | int | 12 | Max 50 |

**Response (200):**

```json
{
  "results": [
    {"id": 12345, "title": "...", "year": 1993},
    ...
  ]
}
```

---

## 3. Inference architecture

### 3.1 Pre-compute step (`scripts/build_index.py`)

**Contract:** backbone-agnostic. The Round-2 winner is identified by name in
the script's CLI args; the script:

1. Loads `artifacts/feature_matrix.npz` (329044, 564).
2. Instantiates the named backbone class with the stored
   `model_config.json` hyperparameters.
3. Loads `state_dict` from `artifacts/models/<winner>.pt`.
4. Encodes all 329k rows in batches (no gradient).
5. L2-normalizes each row of the resulting (329044, 64) latent.
6. Saves `artifacts/inference/embeddings.npy` — float32 (329044, 64) ≈ 80 MB.
7. Joins on `movies_eda_final.csv` to materialize id/title/year/genres/lang
   and saves `artifacts/inference/films.parquet`.

```bash
python scripts/build_index.py \
  --checkpoint artifacts/models/<winner>.pt \
  --features artifacts/feature_matrix.npz \
  --movies-csv data/movies_eda_final.csv \
  --out artifacts/inference/
```

### 3.2 Runtime cosine search

The API loads `embeddings.npy` and `films.parquet` once at startup:

```python
E = np.load("artifacts/inference/embeddings.npy")   # (329044, 64), L2-normed
films = pd.read_parquet("artifacts/inference/films.parquet")
```

For `/similar?top=N`:

```python
q = E[idx_of_id]            # (64,)
sims = E @ q                # (329044,)
top_idx = np.argpartition(-sims, top + 1)[:top + 1]  # exclude self
top_idx = top_idx[np.argsort(-sims[top_idx])]
```

Measured locally: 329k × 64 matmul + topk completes in **<10 ms** on a
modern laptop (numpy + BLAS). No FAISS, no annoy, no vector DB — the
problem size genuinely fits in RAM with millisecond latency.

Memory footprint: 329044 × 64 × 4 B = 80.3 MB for embeddings,
~25 MB for the parquet (titles dominate). Total ≈ 110 MB resident.

---

## 4. Frontend tier

Minimal static HTML + vanilla JS. No framework, no build step.

- Single page at `/` served from the `/static/` mount.
- Search box → calls `/api/films/search` on debounced input.
- Selecting a search result calls `/api/films/{id}/similar?top=N`.
- Top-N selector: radio group for 2 / 5 / 10.
- Result cards: title, year, similarity score.
- The `frontend-design` skill is used to keep the visual layer above the
  generic-AI-aesthetic floor — distinctive, production-grade, no template
  smell.

**Posters: DEFERRED — open decision.** Each row in `films.parquet` carries
a TMDb `id`; the natural option is `GET https://api.themoviedb.org/3/movie/{id}`
on-demand (with browser-side caching) once a TMDb API key is in place. Decision
deferred behind the model + REST priority.

---

## 5. Deployment

**Local dev:**

```bash
uvicorn cineembed.api:app --reload
# → http://localhost:8000
```

- Static files served from `cineembed/static/` via FastAPI's
  `StaticFiles` mount at `/static/`.
- `/` redirects to `/static/index.html`.
- `embeddings.npy` + `films.parquet` paths are configurable via
  `CINEEMBED_INFERENCE_DIR` env var (default `artifacts/inference/`).

**No production deployment in scope.** The local-dev command is the
demo experience; if the course evaluation requires a hosted URL, the
~100 MB artifact + tiny stateless API can be deployed to any free PaaS
(Fly, Render, Hugging Face Spaces) — out of scope for this spec.

---

## 6. Open decisions

- Poster source (TMDb on-demand vs none) — deferred to after the API +
  frontend land.
- Search ranking (substring match vs fuzzy / typo-tolerant) — current
  spec is substring, sufficient for the demo.
- Whether to expose the genre / language / decade labels in the response
  payload — yes if frontend cards need them; trivial addition.

---

## 7. Acceptance

- [ ] `scripts/build_index.py` produces `embeddings.npy` (329044, 64) and
      `films.parquet` from the Round-2 winner checkpoint.
- [ ] `cineembed.api:app` starts under `uvicorn` and serves all three
      endpoints with the contract above.
- [ ] `/api/films/{id}/similar` returns in <50 ms p95 on a laptop.
- [ ] Static UI works end-to-end: search → select → see top-N similar.
- [ ] The demo runs without network access (no TMDb call) when posters
      are deferred.

# CineEmbed — Deployed System Architecture Brief

A code-grounded reference for the final report's "System / Methodology / Architecture" sections. Every claim below is anchored to a `file:line` reference; no generalization beyond what is in the repo as of `2026-05-19`.

Repo root: `/Users/barandincoguz/Desktop/deep learning movie project`

---

## 0. Executive snapshot

- **Dataset:** TMDb-derived feature matrix `(329044, 564)` saved as `artifacts/feature_matrix.npz` with MD5 `e99cee84b6891ea352a7b44d5d7d0ee4` (`artifacts/pipeline_version.json:11`).
- **Encoder:** `MultiModalBackbone` — per-modality linear projection over 7 blocks → concat → 2-layer FC → latent `z` (`src/cineembed/backbone.py:33-104`). Used by AE / VAE / DEC / Contrastive heads (heads only differ).
- **Deployed model:** Demo backbone `ae_z32` (z=32 AE), MVP backbone `ae_z64`, over-parameterised `ae_z128`. `dec_z64_k21` is the MVP-era winner kept for reproducibility but disqualified for retrieval (angular collapse).
- **Inference index:** `scripts/build_index.py` encodes all 329 044 rows, L2-normalizes the latents, writes `artifacts/inference/<backbone>/{embeddings.npy, films.parquet, cluster_labels.npy, cluster_meta.json, manifest.json}` plus a global `films_master.parquet` and `gallery.json`.
- **Backend:** FastAPI app at `src/cineembed/api.py:115` (`lifespan` boot loader at `:70`), serving 8 endpoints. Embeddings loaded via `np.load(..., mmap_mode='r')` and `prewarmed` once. Retrieval is `state.embeddings[bb] @ state.embeddings[bb][row]`.
- **Frontend:** Next.js 16.2.6 + React 19 + Tailwind v4 + shadcn/Radix UI + TanStack Query 5 (`frontend/package.json`). 5 routes: `/`, `/cluster`, `/cluster/[k]`, `/gallery`, `/about`. Zod-validated client.
- **Tests:** 107 test functions across 21 files (1535 LOC). README claims "68 tests" but the live count is 107.

---

## 1. ML pipeline — `src/cineembed/`

### 1.1 Module one-liners and key signatures

| File | One-line purpose | Key public symbols |
|---|---|---|
| `backbone.py:33` | Shared multi-modal encoder: per-block projection → concat → FC → latent `z` | `MultiModalBackbone(block_dims, proj_dims=DEFAULT_PROJ_DIMS, *, hidden_dim=128, latent_dim=64, dropout=0.2)` |
| `heads.py:66, 92, 133, 173` | Four interchangeable heads that wrap the backbone | `AEHead`, `VAEHead`, `ContrastiveHead`, `DECHead` |
| `losses.py:10, 30, 64, 108, 127, 165, 209` | Reconstruction + KL + InfoNCE family | `compute_block_weights`, `weighted_recon_loss` (W2), `director_block_loss` (G2), `vae_elbo`, `dec_loss`, `info_nce_loss`, `LearnedWeightedLoss` (W4) |
| `data.py:65, 101, 137, 271, 316` | Feature loader + DataLoaders (incl. contrastive paired-view) | `load_feature_matrix`, `get_labels`, `train_val_split`, `make_dataloader`, `make_contrastive_dataloader` |
| `eval.py:39-298` | Clustering + retrieval evaluation: KMeans/GMM/Spectral/HDBSCAN/DEC, NMI/ARI/AMI, per-axis-k sweep, multilabel macro-NMI, linear probe, UMAP plot | `cluster_assignments_kmeans`, `_gmm`, `_spectral`, `_hdbscan`, `_dec`, `evaluate_run`, `evaluate_run_per_axis_k`, `multilabel_macro_nmi`, `linear_probe`, `umap_plot` |
| `train.py:14` | Generic training loop with Adam + grad-clip + early stopping + W&B per-epoch hook | `train_model(*, model, loss_fn, train_loader, val_loader=None, n_epochs=100, lr=1e-3, weight_decay=1e-5, early_stop_patience=10, gradient_clip_norm=1.0, ...)` |
| `wandb_integration.py:54, 117, 141, 171, 181` | Optional W&B context manager + per-epoch + final-eval + image + artifact + table loggers (offline-safe no-ops if W&B disabled) | `wandb_run`, `log_epoch`, `log_eval` (auto-computes `geo_nmi = (genre_nmi · lang_nmi · decade_nmi)^(1/3)` at `:165`), `log_image`, `log_artifact`, `log_table` |
| `api.py:115` | FastAPI sidecar serving all `/api/*` endpoints | `app`, endpoints listed in §3 |
| `api_models.py:10-99` | Pydantic v2 schemas with camelCase JSON wire shape | `Film`, `Neighbor`, `Cluster`, `ClusterDetail`, `Backbone`, `HealthResponse`, `CosineHistogram` |
| `search.py:11` | RapidFuzz prefix + fuzzy title search over `films_master.parquet` | `FilmSearcher.search(q, limit=10)` — staged: exact-prefix scan, then fuzzy WRatio @ cutoff 70 |
| `tmdb.py:39` | Async TMDb v3/v4 client with disk-LRU 30-day cache, dedup via in-flight futures, AsyncLimiter token bucket (35 req / 10 s) | `TMDbClient.get_enrichment(film_id) -> TmdbBlob` |
| `cluster_naming.py:53` | Heuristic auto-namer: dominant genre + modal decade per cluster | `auto_name_clusters(cluster_labels, films, k=21)` |
| `keywords.py:6, 39` | Curated style/plot keyword split — `STYLISTIC_DICT` frozenset of 49 stylistic markers | `split_keywords(keywords)` capped at `MAX_KEYWORDS_PER_BUCKET=8` |
| `enrich.py:19` | Robust country parser (TMDb JSON dict or plain name) → ISO-3166 alpha-2 via `pycountry`, LRU-cached | `parse_country(raw)` |

### 1.2 Multi-modal backbone — concrete numbers

`backbone.py:33`

```python
DEFAULT_PROJ_DIMS = {                                        # backbone.py:9
    'numerical': 16, 'genre': 16, 'language': 16,
    'decade':    4,  'awards':   16, 'text':     64,
    'director':  32,
}
```

Block input dims (`artifacts/feature_metadata.json` `block_dims`, also `tests/conftest.py:13-21`):

| Block        | Input dim | Projected dim | Dropout |
|--------------|----------:|--------------:|--------:|
| numerical    |         6 |            16 |   0.10  |
| genre        |        22 |            16 |   0.10  |
| language     |        31 |            16 |   0.10  |
| decade       |         2 |             4 |   0.10  |
| awards       |         6 |            16 |   0.10  |
| text         |       384 |            64 |   0.20  |
| director     |       113 |            32 |   0.20  |
| **TOTAL**    |   **564** |       **164** |        |

Dropout for `text` and `director` is 0.2; all others use 0.1 (`backbone.py:57`).

The projected concat (164-d) feeds:

```python
self.backbone = nn.Sequential(                               # backbone.py:65
    nn.Linear(concat_dim, hidden_dim),                       # 164 -> 128
    nn.ReLU(inplace=True),
    nn.Dropout(dropout),                                     # 0.2
    nn.Linear(hidden_dim, latent_dim),                       # 128 -> z ∈ {32, 64, 128}
)
```

Each `_BlockProjection` is `Linear(in_dim, out_dim) → ReLU → Dropout` (`backbone.py:20-30`).

`forward(blocks, block_mask=None)` supports per-row stochastic masking (`backbone.py:76-104`). A mask value of `0.0` zeros the entire projected block; an `(B, 1)` tensor zeros per row. Default 1.0 (kept). Used by the SimCLR-style contrastive augmentation.

Param count is held under 500k by `test_backbone.py:test_backbone_param_count_under_500k`.

### 1.3 Decoder — symmetric block-aware mirror

`_MultiModalDecoder` (`heads.py:26-63`) mirrors the encoder:

1. `Linear(latent_dim, hidden_dim) → ReLU → Linear(hidden_dim, concat_dim)` to a 164-d concatenated representation.
2. Slice the concat back into per-block sub-vectors using `proj_dims`.
3. Each `_BlockDecoder` (`heads.py:12-23`) is `Linear(proj_dim, max(proj_dim, 32)) → ReLU → Linear(max(proj_dim, 32), block_dim)` — i.e. independent per-block reconstruction.

### 1.4 AE / VAE / Contrastive / DEC heads

- **`AEHead` (`heads.py:66`)** — `encode → z`, then `decoder(z)` → block-wise reconstruction. The standard reconstruction objective.
- **`VAEHead` (`heads.py:92`)** — adds `fc_mu` and `fc_log_var` heads of dim `z_dim → z_dim`; reparameterizes `z = μ + σ ⊙ ε`; returns `(decoded, μ, log_var)`. Used with `vae_elbo` (`losses.py:108`).
- **`ContrastiveHead` (`heads.py:133`)** — wraps the backbone with a 2-layer projection MLP for SimCLR-style pretext: `Linear(z, z) → BatchNorm1d(z) → ReLU → Linear(z, projection_dim=128)`. After pretext the projection is discarded (Chen et al. 2020 convention); downstream AE/DEC operate on raw backbone `z`. `forward(blocks, block_mask=None)` accepts a different stochastic mask per augmented view.
- **`DECHead` (`heads.py:173`)** — wraps the backbone + an AE decoder + a learnable `cluster_centers` parameter of shape `(n_clusters, latent_dim)`. `initialize_centers(z_array)` does KMeans-20-init on a precomputed latent matrix (`heads.py:192-200`). `reinit_collapsed_centers(...)` re-seeds clusters that hold fewer than `size_floor * n_total` samples (default `0.001`, `heads.py:202-234`) — the spec's anti-collapse mitigation (D10). `soft_assignments(z)` computes the Student-t kernel `q_unnorm = (1 + ||z - μ_j||² / α)^{-(α+1)/2}`, row-normalized (`heads.py:236-241`).

### 1.5 Losses — exact formulas

`losses.py`

**W2 inverse-variance block weighting** (`losses.py:10-27`):

```
w_b = clip(1 / total_variance(block_b), w_min=0.1, w_max=10.0)
```

where `total_variance(block_b) = sum_j Var(X[:, j])` for `j` in block `b`. The eps floor is `1e-6`. The clipping band `[0.1, 10]` is the D9 stability fix.

**Canonical reconstruction loss** (`weighted_recon_loss`, `losses.py:64-95`):

```
L_recon = Σ_{b ≠ director, b ∉ skip}  w_b · MSE(decoded[b], target[b])
                +  director_block_loss(decoded.dir, target.dir, has_bio, w_dir)
```

`exclude_blocks` is an optional set used by F1/F2 modality-ablation runs (spec §8.3.2) so the model is not penalized for failing to reconstruct a masked input.

**G2 masked director loss** (`losses.py:30-61`): the 113-d director block decomposes into `[0:64]` PCA-compressed bio + `[64]` has_bio flag + `[65:96]` dir_lang one-hot (31) + `[96:112]` dir_country one-hot (16) + `[112]` has_dir_lang.

```
loss_bio    = mean_over_rows_where_has_bio==1 of MSE(decoded[:, 0:64], target[:, 0:64])
                                                 (averaged over 64 dims)
loss_other  = MSE(decoded[:, 64:113], target[:, 64:113])
loss_dir    = w_dir * 0.5 * (loss_bio + loss_other)
```

Bio coverage is only 3.18% of films (`artifacts/director_profile_metadata.json:3`), so masking is essential — without it, the model would be penalized for ~97% of rows.

**VAE ELBO** (`losses.py:108-124`):

```
KL    = -0.5 · Σ_d (1 + log_var - μ² - exp(log_var))  [per row, then mean over batch]
ELBO  = L_recon + β · KL
```

Returns `(loss_tensor, recon_value_float, kl_value_float)` for separate logging.

**DEC KL loss with batch-wise sharpened target P** (`losses.py:127-162`, spec D10):

```
q_ij        = (1 + ||z_i − μ_j||² / α)^{-(α+1)/2}      (Student-t kernel, α=1.0)
q           = row-normalize q                          (B, k)
f_j         = Σ_i q_ij                                  (column sum, k)
p_ij        ∝ q_ij² / f_j                                (sharpening)
p           = row-normalize p, .detach()                (target stops gradient)
L_KL        = mean over i of  Σ_j  p_ij · log(p_ij / q_ij)
L_DEC       = L_KL + λ_recon · L_recon                   (λ_recon = 0.1 default)
```

Batch-wise (not dataset-wide) P is the D10 fix — original DEC computes P over the full dataset, which is intractable for 329k rows; the batch-wise approximation works at our scale.

**Symmetric InfoNCE** (`losses.py:165-206`, spec §2.1, Chen et al. 2020 SimCLR):

```
z_a, z_b      = L2-normalize(view_a), L2-normalize(view_b)
z             = concat([z_a, z_b]) shape (2B, d)
sim           = (z @ z.T) / τ      shape (2B, 2B)
mask diag     = -inf                                     (no self-similarity)
targets[i]    = (i + B) mod 2B                           (positive pair index)
L_InfoNCE     = cross_entropy(sim, targets)
```

Default `temperature τ = 0.1` (lower than vision's 0.5 because heterogeneous tabular geometry is denser and modality-dropout views are less radical than image augmentations).

**Augmentation primitive** — `_sample_block_mask_batch` (`data.py:213-238`) draws per-row Bernoulli(1 − `drop_prob`) over the 7 blocks, then guarantees at least one block survives per row by re-sampling a kept block. `make_contrastive_dataloader` (`data.py:271-313`) yields paired views with independent masks via `_contrastive_collate`. Default `drop_prob = 0.3` — each view loses ~2 of 7 modalities in expectation.

**LearnedWeightedLoss (W4 stretch, Kendall et al. 2018)** (`losses.py:209-237`) — per-block `log_sigma` jointly trained: `loss = Σ_b exp(-s_b) · L_b + 0.5 · s_b`.

### 1.6 Training loop

`train.py:14-149` — `Adam` with `weight_decay=1e-5`, `gradient_clip_norm=1.0`, val-loss early-stopping (default `patience=10`, `min_delta=1e-4`), per-epoch console log, optional W&B logging via `wandb_run` arg, atomic checkpoint save on each `val_loss` improvement. Supports tuple-returning losses (VAE/DEC return `(loss, recon, kl)`); the loop strips to `loss[0]` (`train.py:91-92, 109-110`). Auto-detects whether `loss_fn` accepts an `epoch` argument for schedules like VAE β warmup (`train.py:62-70`). `extra_params` can be passed to optimize learned uncertainty weights jointly (W4).

`_move_batch_to_device` (`train.py:152-167`) handles both flat batches `{blocks, has_bio}` and contrastive paired batches `{view_a, view_b}` where each view also carries a `block_mask`.

### 1.7 Contrastive pretext driver

`scripts/train_contrastive.py:210-323` — the Phase-1 driver that pretrains the backbone via InfoNCE, saves a `pretext_backbone.pt` (backbone-only state_dict) and `pretext_full.pt` (with projection head for resume), and posts NMI/ARI/AMI on KMeans + GMM + per-axis-k against the MVP `dec_z64_k21` baseline (geno_nmi=0.332).

---

## 2. Inference index build — `scripts/build_index.py`

### 2.1 Pipeline (`scripts/build_index.py:393-501`)

```
checkpoint .pt
  └─ _load_backbone(args, block_dims)              # reconstructs head, peels backbone
       └─ AEHead | VAEHead | DECHead | raw backbone
feature_matrix.npz
  └─ cdata.load_feature_matrix                     # (X, feature_names)
       └─ cdata.get_block_indices                  # block_slices
has_bio = X[:, dir_slice.start + 64]               # extracted from director block, col 64
_encode_all(bb, X, has_bio, block_slices, ...)     # batched forward
  └─ z_all = concat → L2-normalize → float32       # (N, latent_dim)
_build_films_table(artifacts, expected_rows=N)     # CSV → minimal parquet
  └─ asserts row count match (positional alignment invariant)
_retrieval_eval(z_norm, films_df, k, n_queries)    # genre@k + angular-spread
_eyeball_top5(z_norm, films_df, EYEBALL_QUERIES)   # 10 well-known queries
_run_clustering(out_dir, k=21)                     # MiniBatchKMeans + auto_name_clusters
```

### 2.2 Outputs (per backbone)

`artifacts/inference/<backbone>/`:

- `embeddings.npy` — `(N, latent_dim)` float32, L2-normalized so cosine = dot product. ae_z32: 42 MB, ae_z64: 84 MB, ae_z128: 168 MB.
- `films.parquet` — id, title, year, director_name, genres (list[str]), overview, popularity, vote_average, vote_count, runtime, original_language. ~80 MB (`scripts/build_index.py:443-449`).
- `cluster_labels.npy` — `(N,) uint8` from `MiniBatchKMeans(n_clusters=21, batch_size=4096, n_init='auto', random_state=42)` (`scripts/build_index.py:381`). 329 KB.
- `cluster_meta.json` — list of 21 dicts: `{id, name="<genre> · <decade>s", size, topGenres=[{genre, pct}×3], modalDecade}` (`cluster_naming.py:53-79`). Example: `Action · 2010s` size=14 200 (`artifacts/inference/ae_z32/cluster_meta.json`).
- `manifest.json` — schema_version, checkpoint path + sha256[:32], model_type, latent_dim, hidden_dim, n_clusters, n_films, embedding_dim, normalization=`L2`, distance_metric, retrieval block (`genre_at_k_mean`, `_median`, `_std`, plus `angular` random-pair cosine stats), eyeball block (10 queries × 5 neighbors), wall_clock_seconds (`scripts/build_index.py:481-499`).

The repo's deployed `ae_z32` manifest reports `genre_at_k_mean = 0.7228` over 316 effective queries, `random_pair_cos_mean = 0.302 ± 0.301` (healthy spread, range `[-0.43, 1.00]`) — `artifacts/inference/ae_z32/manifest.json`.

### 2.3 Global artifacts (not per backbone)

`artifacts/inference/`:

- `films_master.parquet` — 78.7 MB, used directly by `api.lifespan` (no row-positional dependency on a specific backbone).
- `gallery.json` — 139 KB; output of `scripts/build_gallery.py:142-146`, the 5 × 3 × 5 matrix for `/gallery`.
- `cluster_names_override.json` — currently `{"ae_z32": {}, "ae_z64": {}, "ae_z128": {}}` (empty; supports manual rename loaded at `api.py:60`).
- `backbones.json` (under `artifacts/`, not `inference/`) — 715 B; the metadata served by `GET /api/backbones`.

```json
[
  {"id":"ae_z32","z":32,"label":"AE z=32 (demo backbone)","genreAtFive":0.723,"gnmi":0.334,"preferred":true,...},
  {"id":"ae_z64","z":64,"label":"AE z=64 (MVP carry-over)","genreAtFive":0.715,"gnmi":0.328,"preferred":false,...},
  {"id":"ae_z128","z":128,"label":"AE z=128 (over-parameterised)","genreAtFive":0.722,"gnmi":0.273,"preferred":false,...}
]
```

### 2.4 L2-normalization + cosine retrieval

`scripts/build_index.py:206-208`:

```python
norms = np.linalg.norm(z_all, axis=1, keepdims=True)
norms = np.where(norms < 1e-8, 1.0, norms)
return (z_all / norms).astype(np.float32)
```

Because rows are unit vectors, `cosine(a, b) = a · b`, so retrieval is a single matrix-vector product `embeddings @ embeddings[row_idx]` (`api.py:230, scripts/build_index.py:339`).

---

## 3. Backend — FastAPI (`src/cineembed/api.py`)

### 3.1 Boot sequence (`api.py:70-112`)

The `@asynccontextmanager` `lifespan` runs once per process:

1. `state.backbones_meta = json.loads(artifacts/backbones.json)` — `api.py:74`.
2. `state.films = pd.read_parquet(artifacts/inference/films_master.parquet, engine="pyarrow")` — `api.py:77`.
3. `state.row_to_id`, `state.id_to_row` — O(N) Python dict built from `films["id"].astype(int).tolist()` — `api.py:80-81`.
4. Optional `cluster_names_override.json` loaded — `api.py:84-86`.
5. For each `bb ∈ {ae_z32, ae_z64, ae_z128}`:
   - `state.embeddings[bb] = np.load(artifacts/inference/<bb>/embeddings.npy, mmap_mode="r")` — `api.py:90`. Mmap means embeddings live as paged memory; no full RAM load on cold start.
   - `state.cluster_labels[bb] = np.load(.../cluster_labels.npy)` — `api.py:92`.
   - `state.cluster_meta[bb] = _load_cluster_meta(...)` — `api.py:93` (also applies override names).
6. **Prewarm**: `_ = state.embeddings["ae_z32"] @ state.embeddings["ae_z32"][0]` — `api.py:96`. Forces the OS page cache to load the 42 MB matrix on first request, so the first user-facing call is fast.
7. `state.searcher = FilmSearcher(state.films)` — `api.py:99`. Lowercases titles into a Python list, materializes popularity floats.
8. `state.tmdb = TMDbClient(api_key=os.env.TMDB_API_KEY, access_token=os.env.TMDB_ACCESS_TOKEN, cache_dir=artifacts/cache/tmdb)` — `api.py:102`.

CORS middleware allows GET from `CORS_ORIGINS` env (default `http://localhost:3000,http://127.0.0.1:3000`) — `api.py:117-123`.

### 3.2 Endpoints

| Method | Path | Signature | Purpose | Line |
|---|---|---|---|---|
| GET | `/api/health` | `HealthResponse` | status, backbones_loaded, films, tmdb_key_configured | `api.py:126` |
| GET | `/api/backbones` | `list[Backbone]` | The 3-row backbones metadata array | `api.py:136` |
| GET | `/api/films/search` | `q: str (1-200), backbone='ae_z32', limit=10` → `list[Film]` | RapidFuzz title search (TMDb-lazy) | `api.py:141` |
| GET | `/api/films/{film_id}` | `backbone='ae_z32'` → `Film` | Single-film detail, TMDb-enriched | `api.py:215` |
| GET | `/api/films/{film_id}/similar` | `backbone='ae_z32', limit=10` → `list[Neighbor]` | Top-k cosine neighbors; top-5 TMDb-enriched in parallel | `api.py:243` |
| GET | `/api/films/{film_id}/cosine-dist` | `backbone='ae_z32', bins=30` → `{bins, counts, stats, top10}` | Histogram of cosine to all other films + top-10 | `api.py:357` |
| GET | `/api/clusters` | `backbone='ae_z32'` → `list[Cluster]` | 21 clusters with 4 preview films each (by popularity) | `api.py:292` |
| GET | `/api/clusters/{k}` | `k: 0-20, backbone='ae_z32', limit=50` → `ClusterDetail` | Cluster `k` with up to 50 films, top-5 TMDb-enriched | `api.py:312` |
| GET | `/api/gallery` | `→ dict` (Gallery schema) | Returns `artifacts/inference/gallery.json` (precomputed) | `api.py:350` |

### 3.3 Retrieval implementation

`api.py:227-240`:

```python
def _compute_cosines(film_id, backbone):
    row = state.id_to_row[film_id]
    q   = state.embeddings[backbone][row]
    return state.embeddings[backbone] @ q              # (N,) cosines

@lru_cache(maxsize=50)
def _compute_cosines_cached(film_id, backbone) -> tuple:
    return (_compute_cosines(film_id, backbone),)      # wrap; ndarrays aren't hashable

def get_cosines(film_id, backbone):
    return _compute_cosines_cached(film_id, backbone)[0]
```

`similar` (`api.py:243-275`) uses `np.argpartition(-cosines, k+1)[:k+1]`, then sorts that slice — partial sort is O(N + k log k) vs full O(N log N). Self is dropped post-hoc; the top 5 ids are TMDb-enriched in parallel via `asyncio.gather(*tmdb.get_enrichment(fid)…)` while remaining 6-10 are left lazy.

`cosine_dist` (`api.py:357-398`) computes a 30-bin histogram of the cosine vector excluding self over `[-1, 1]`, plus `mean / std / min / max / p50 / p95` and top-10 cosines. The frontend `CosineHeatmap` renders this directly with Recharts.

### 3.4 Cluster info

- `cluster_meta` is loaded at boot from `artifacts/inference/<bb>/cluster_meta.json` and merged with `cluster_names_override.json` (`api.py:60-67`).
- `_cluster_top_n_rows(backbone, k, n)` (`api.py:278-289`) returns row indices in cluster `k`, sorted by `popularity` DESC with stable sort.
- `Cluster` ships 4 preview films (popularity-ranked); `ClusterDetail` ships up to `limit=50`. TMDb enrichment is capped at top-5 for both, to keep the gather wave bounded.

### 3.5 TMDb integration

`src/cineembed/tmdb.py:39`

- Auth precedence: v4 access token (Bearer JWT) > v3 api_key (query param) — `tmdb.py:71-76`.
- Rate limit: `AsyncLimiter(35, 10)` — 35 requests / 10 s — `tmdb.py:56`.
- Disk-LRU cache at `artifacts/cache/tmdb/<film_id>.json`, TTL 30 days (`CACHE_TTL_SEC = 30·24·3600`) — `tmdb.py:20, 78-99`.
- Atomic write via `<id>.json.tmp → .replace` — `tmdb.py:101-105`.
- In-flight dedup via `self._inflight: dict[int, asyncio.Future]` so a burst on the same film_id (e.g. cluster preview + film detail) results in a single TMDb call — `tmdb.py:138-153`.
- 429 backoff: single retry after `asyncio.sleep(2.0)` — `tmdb.py:114-117`.
- Image URLs: `make_poster_url(path) → https://image.tmdb.org/t/p/w342{path}`; backdrop uses `w1280` — `tmdb.py:31-36`.

`TmdbBlob` dataclass (`tmdb.py:23-28`) carries only `{poster_path, backdrop_path, tagline, keyword_names}` — keyword_names are then fed through `split_keywords` (`keywords.py:39-59`) to produce the `style[]` / `plot[]` chips on the film panel.

---

## 4. Frontend — Next.js 16 / Tailwind v4 / shadcn

### 4.1 Stack (`frontend/package.json`)

- `next@16.2.6`, `react@19`, `react-dom@19`, `typescript@5.7.3`.
- `tailwindcss@^4.2.0`, `@tailwindcss/postcss@^4.2.0`, `tw-animate-css@1.3.3`.
- `@tanstack/react-query@^5.100.10` — server-state cache, 5-min `staleTime`, `retry: 1`, `refetchOnWindowFocus: false` (`frontend/app/providers.tsx:7-15`).
- `zod@^3.24.1` — every API response is parsed through a `*Schema.parse(json)` at `frontend/lib/api.ts:34`.
- `@radix-ui/react-*` (29 primitives) + `lucide-react@^0.564.0` + `recharts@2.15.0` + `class-variance-authority` + `tailwind-merge` + `cmdk` + `sonner` + `vaul` + `zustand` + `react-hook-form`.

### 4.2 Routes (App Router)

| Path | File | What it shows |
|---|---|---|
| `/` | `app/page.tsx` | Search + 4-tile stats strip (`329,044 / 3 / 32 / cosine`) + educational callout "How retrieval works" + empty state (Inception/Spirited Away/Pulp Fiction quick-picks) + 58/42 split for `SelectedFilmPanel` and `SimilarFilmsPanel` when `?film=<id>` is set. URL is the source of truth for `film` and `backbone`. |
| `/cluster` | `app/cluster/page.tsx` | "Clusters (k=21)" grid + educational callout "How clusters form" + 21 `ClusterCard`s in a 3-col responsive grid. |
| `/cluster/[k]` | `app/cluster/[k]/page.tsx` | Cluster detail: name, size, top genres, modal decade, plus up to 50 film posters (6-col grid on lg). Clicking a poster routes to `/?film=<id>&backbone=<bb>`. |
| `/gallery` | `app/gallery/page.tsx` | Pre-rendered server component fetching `gallery.json` (`revalidate: 3600`). Editorial 5-query × 3-backbone matrix with numbered section headers (V7) and per-cell `genre@5` annotation. |
| `/about` | `app/about/page.tsx` | Two methodological findings: (1) "NMI ≠ retrieval quality" — dec_z64_k21 disqualified for angular collapse; (2) "Sweet spot at z=32" — U-curve with ae_z32 winning on both genre@5 and gNMI. |

Layout (`app/layout.tsx`): fixed-width sidebar (220 px) + main content. `<Providers>` wraps the tree with the TanStack QueryClient. `Geist` + `Geist_Mono` fonts. Vercel `Analytics` mounted in production only.

### 4.3 Components (`frontend/components/`)

| File | Purpose |
|---|---|
| `sidebar.tsx:14` | Fixed 220 px nav with 4 links (Home, Clusters, Gallery, About); `usePathname` for active state. V2 visual polish: vertical purple gradient accent strip + radial logo glow. |
| `search-bar.tsx:13` | 300 ms debounced combobox over `/api/films/search`. ARIA combobox/listbox. |
| `backbone-switcher.tsx:13` | Radio-group toggle for `ae_z32 / ae_z64 / ae_z128`. Updates `?backbone=` and invalidates 5 query keys (`film`, `similar`, `cosineDist`, `clusters`, `cluster`) so the new backbone's data fetches fresh. Tooltip shows `genre@5` + `gNMI`. |
| `selected-film-panel.tsx:18` | 58% column. Backdrop image masked via linear-gradient at opacity 0.12 (V8 selected-film backdrop fade). Title, director, runtime, country, tagline, genres, rating + votes, cluster id, time-bucket, current backbone. Style/Plot chips from `split_keywords` (rendered as a unified "Keywords" list if `style.length == 0`). Embeds `CosineHeatmap` dynamically (no SSR). |
| `similar-films-panel.tsx:26` | 42% column. Numbered top-10 list. Each row colors its cosine badge: `≥0.95 strong` (green), `≥0.80 good` (blue), `<0.80 other` (slate). Hover lifts row by 0.5 px with shadow. |
| `cosine-heatmap.tsx:14` | Recharts BarChart of the 30-bin cosine distribution + the `μ/σ/p50/p95/max` stats line + top-10 list. Loading state uses the shimmer skeleton. Info tooltip explains `1 = same direction, 0 = orthogonal`. |
| `cluster-card.tsx:7` | Card on `/cluster` — dot bullet, cluster name (e.g. `Action · 2010s`), size, top-2 genre badges with pct, 2-poster preview grid. Hover lifts the card and softens shadow. |
| `film-poster.tsx:6` | Renders TMDb `posterUrl` via `next/image` when available; otherwise a deterministic HSL gradient card built from `(film_id * 2654435761) % 360` (`api.py:209-212`) as a fallback chip with the title overlaid. Sizes `sm / md / lg`. |
| `empty-state.tsx:15` | Centered "Search 329,044 films" prompt with 3 example chips (Inception/Spirited Away/Pulp Fiction). |
| `error-fallback.tsx`, `theme-provider.tsx`, `footer.tsx` | Standard. Footer line: `329,044 films · 3 backbones · L2-normalized cosine · multimodal autoencoder over 7 feature blocks`. |
| `components/ui/` | 59 shadcn primitives, generated by shadcn CLI (button, card, dialog, dropdown-menu, sheet, tooltip, …). |

### 4.4 State management

- **TanStack Query** is the only server-state cache. All API calls go through `frontend/lib/api.ts` which wraps `fetchJson(path, schema, init)` (`lib/api.ts:18-35`). Each request validates the response with `schema.parse(json)`; a non-OK response throws `ApiError(status, detail)`.
- Query keys: `["film", filmId, backbone]`, `["similar", filmId, backbone]`, `["cosineDist", filmId, backbone]`, `["clusters", backbone]`, `["cluster", k, backbone]`, `["backbones"]`, `["search", debouncedQ, backbone]`.
- `BackboneSwitcher` invalidates 5 of these on change.
- URL is the canonical state for `filmId` and `backbone` on the home route — selecting a film calls `router.replace(?film=<id>, { scroll: false })` (`app/page.tsx:35-40`). `useSearchParams` reads them back.

### 4.5 Educational callouts

Two prominent in-page explainer blocks, each with an icon + heading + paragraph + chip strip:

- **"How retrieval works"** (`app/page.tsx:80-102`) — explains the 32-dim multimodal embedding over 7 blocks, cosine top-10 over 329 044 films, and the U-curve finding. Chips: `7 feature blocks`, `cosine top-10`, `329,044-film index`, `live distribution heatmap`.
- **"How clusters form"** (`app/cluster/page.tsx:30-50`) — explains `MiniBatchKMeans(k=21)` on L2-normalized embeddings + auto-naming from dominant genre + modal decade. Chips: `k=21`, `MiniBatchKMeans`, `L2-normalized cosine`, `auto-named per cluster`.

### 4.6 Visual polish (V-tier system in `app/globals.css`)

The "V1–V12" labels are inline comments in `globals.css` and the components. Mapping found in the repo:

| Tier | Location | What it is |
|---|---|---|
| V1 | `globals.css:117-121` | `.dot-grid` background — 22 px radial-gradient purple dot grid utility (used on `<div>` in `app/page.tsx:43`). |
| V2 | `sidebar.tsx:22-35` | Vertical gradient accent strip on the sidebar + radial blur halo behind the `Film` logo icon. |
| V5 | `globals.css:104-114` | Fixed-position SVG fractalNoise grain overlay (`mix-blend-mode: multiply`, `opacity 0.035`, `z-index 1`). |
| V7 | `app/gallery/page.tsx:35-48` | Editorial numbered section headers (`01`, `02`, … in light 4xl tabular-nums). |
| V8 | `selected-film-panel.tsx:36-46` | Backdrop image fading from full opacity at top to transparent at 55% via mask-image. |
| V9 | `globals.css:123-126` | `.shadow-primary-soft` — purple-tinted soft shadow `0 1px 0 rgba(110, 86, 207, 0.04), 0 2px 8px -2px rgba(110, 86, 207, 0.08)`. Used on home callout, cluster callout, cluster cards, selected-film card. |
| V10 | `globals.css:96-98` | Geist `font-feature-settings: "ss01" on, "ss03" on, "cv11" on` — stylistic alt zero, alt four, single-story 'a'. |
| V12 | `globals.css:128-143` | `.shimmer` keyframe + utility — 1.8 s linear-infinite linear-gradient sweep used as the skeleton loading state on cluster cards, film posters, cosine heatmap, similar-films list, selected-film panel. |

Color tokens (`globals.css:6-47`): primary `#6e56cf` (purple), bg `#f8f9fb`, card `#ffffff`, muted `#f1f0f5`, border `#e5e4ec`, ring `#6e56cf`. `--radius: 0.625rem`. The CineEmbed-specific tokens (`--ce-purple`, `--ce-purple-bg`, …) duplicate these for use outside the shadcn token system.

### 4.7 Mocking and dev modes

- `frontend/lib/mock-data.ts` exists for offline UI work; the live components import only from `@/lib/api`, so production is API-backed.
- `BackboneSwitcher` has a typed `FALLBACK` array of the three backbones inline (`backbone-switcher.tsx:7-11`) so the UI still renders if `/api/backbones` fails.

---

## 5. Data pipeline

### 5.1 Source dataset

The project starts from a TMDb-derived raw dump (CSV at `data/`) processed by `eda_v2.ipynb` (located at repo root). The EDA notebook header references §1-§5: Setup & Reproducibility, Pipeline Function Definitions, Pipeline Execution, EDA Visualizations, Persistence (`eda_v2.ipynb:5-12`). Outputs land in `artifacts/`.

The model artifact ecosystem (`artifacts/pipeline_version.json`):

```json
{
  "seed": 42,
  "timestamp_utc": "2026-05-04T19:59:05Z",
  "library_versions": {
    "numpy": "2.0.2", "pandas": "2.2.2",
    "sentence_transformers": "5.4.1",
    "torch": "2.10.0+cu128",
    "umap_learn": "0.5.12", "scikit_learn": "1.6.1"
  },
  "model_name": "paraphrase-multilingual-MiniLM-L12-v2",
  "n_films": 329044,
  "feature_dim": 564,
  "feature_matrix_md5": "e99cee84b6891ea352a7b44d5d7d0ee4"
}
```

The text-overview embedding is the 384-d `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` representation — confirmed by both `model_name` here and the 384-column `text_0…text_383` block in `feature_metadata.json`.

### 5.2 Feature matrix layout — `(329044, 564)`

Source of truth: `artifacts/feature_metadata.json:block_dims`. Tests pin the same numbers at `tests/conftest.py:13-21`.

| # | Block | Dim | Encoding | Feature-name prefix(es) |
|---|---|---:|---|---|
| 1 | numerical | 6 | Per-feature standard / minmax scaling + missingness flags | `log_popularity`, `log_vote_count`, `runtime_norm`, `vote_average_norm`, `has_vote`, `has_engagement` |
| 2 | genre | 22 | Multi-label one-hot over 21 TMDb genres + `has_genre` flag | `genre_Action`, `genre_Adventure`, …, `genre_Western`, `has_genre` |
| 3 | language | 31 | One-hot over top-30 `original_language` codes + `lang_other` | `lang_ar`, `lang_cn`, …, `lang_zh` |
| 4 | decade | 2 | Min-max normalized decade `(decade − 1900) / 130` + `has_release_date` flag | `decade_norm`, `has_release_date` |
| 5 | awards | 6 | log1p of TMDb prior nominations / wins (total, oscar, palme) | `prior_log_total_nominations`, `_total_wins`, `_oscar_nominations`, `_oscar_wins`, `_palme_nominations`, `_palme_wins` |
| 6 | text | 384 | Sentence-transformers MiniLM L2-normalized embedding of `overview` | `text_0`, …, `text_383` |
| 7 | director | 113 | 64-d PCA of director-bio embedding (`bio_pca_explained_variance = 0.833` over 64 components) + `has_director_bio` + 31-d director-language one-hot + 16-d director-country one-hot + `has_director_lang`. Block decomposition: `[0:64]` bio_pca, `[64]` has_bio, `[65:96]` dir_lang, `[96:112]` dir_country, `[112]` has_dir_lang | `dir_bio_pca_0..63`, `has_director_bio`, `dir_lang_en..other`, `dir_country_USA..other`, `has_director_lang` |
| | **TOTAL** | **564** | | |

Director-block stats (`artifacts/director_profile_metadata.json`):
- 505 directors have bios → only 3.18% film coverage on bio.
- Lang coverage: 99.99% of films (`has_director_lang` near-universal).
- PCA explained variance: 0.833.
- Top languages: en, de, es, fr, pt, ja, it, ru, ko, zh, ta, nl, hi, cn, ml, da, tr, sv, cs, pl, th, ar, el, hu, sr, fi, id, fa, no, te, other (= 31, matching `lang` block).
- Top director countries: USA, GER, FRA, ARG, JPN, IND, ITA, BRA, RUS, SGP, KOR, FIN, DNK, CZE, BEL, other (= 16, matching `dir_country` block).

### 5.3 Block discovery at load time

`data.py:13-62` derives block slices by scanning `feature_names` left-to-right and classifying each by prefix (`_classify_feature` at `:28`). The classifier checks `director` before `language` so that `dir_lang_*` columns aren't misrouted (the ordering note is comment-documented at `:32-33`). Adjacent same-class runs are coalesced into `slice(start, stop)` (`:48-58`). The function raises if any block ends up non-contiguous, guaranteeing the column layout invariant.

### 5.4 Preprocessing decisions

- **Standard scaling** for the numerical block (mean 0, std 1, learned on training data) — applied in `eda_v2.ipynb` §3 and persisted via `artifacts/scalers.pkl`.
- **Bio masking (G2)** — `dir_bio_pca_*` columns contribute to the loss only where `has_director_bio == 1`, otherwise their loss is zero (`losses.py:30-61`). Without this, 97% of rows would be penalized for failing to reconstruct zeros.
- **Missingness flags** — every modality with optional content has a paired `has_*` indicator (`has_vote`, `has_engagement`, `has_genre`, `has_release_date`, `has_director_bio`, `has_director_lang`). Spec §3.2 keeps these as explicit features rather than imputing.
- **`feature_matrix_raw.npz`** (`artifacts/`, 395 MB) is kept alongside `feature_matrix.npz` (402 MB) for downstream ablations on unscaled inputs.
- **Train / val split** — `train_val_split(n, val_frac=0.1, seed=42)` (`data.py:137-144`) is a deterministic permutation; the same `seed=42` is used everywhere (notebooks, `train_contrastive.py`, `build_index.py`).
- **Feature matrix MD5: `e99cee84b6891ea352a7b44d5d7d0ee4`** (matches the spec; pinned in `pipeline_version.json` and quoted in `README.md`).

### 5.5 Labels for evaluation (NMI/ARI/AMI)

`get_labels(csv_path, top_lang_n=10)` (`data.py:101-134`) derives three orthogonal label axes from `movies_eda_final.csv`:

- `primary_genre` — first piece of the `genres` pipe-separated string; empty → `'Unknown'`.
- `decade_bin` — direct from `decade` column, or reconstructed from `decade_norm` via `decade_norm * 130 + 1900` rounded down to nearest 10; masked to 0 for rows where `has_release_date == 0`.
- `lang_top10` — bucket of original_language; everything outside the top-10 collapsed to `'other'`.

`evaluate_run` (`eval.py:140-159`) then reports `{genre,decade,lang}_{nmi,ari,ami}`. `evaluate_run_per_axis_k` (`eval.py:162-199`) does the per-axis-k sweep using `DEFAULT_AXIS_K = {'genre': 21, 'decade': 12, 'lang': 11}` to match each axis's ground-truth cardinality. `multilabel_macro_nmi` (`eval.py:202-261`) treats each of the 21 genre columns as a binary partition and macro-averages.

---

## 6. Tests — `tests/`

### 6.1 Counts

- **21 test files**, 1535 LOC total (excluding `__init__.py` and `__pycache__`).
- **107 test functions** (`grep -E "^def test_|^async def test_" tests/*.py | wc -l`).
- `pyproject.toml:40-43` sets `addopts = "-v --tb=short"` and `asyncio_mode = "auto"` for `pytest-asyncio`.
- `conftest.py:48-93` provides a `synthetic_feature_matrix` fixture: a `(200, 564)` mini-matrix matching the production layout exactly (block dims, has_bio sparsity, text L2-normalized, sparse genre + lang + dir one-hots, has_release_date prevalence, etc.). This is the shared workhorse — `synthetic_blocks_dict`, `synthetic_has_bio`, `synthetic_labels` all derive from it.

### 6.2 Coverage map (per file, what's verified)

| File | Tests | Covers |
|---|---:|---|
| `test_import.py` | 1 | Package import + `__version__ == "0.1.0"` |
| `test_data.py` | 7 | Block slice derivation, .npz load, label CSV parsing, deterministic split, dataloader yields `(blocks, has_bio)`, **contrastive dataloader yields two views with masks**, "every row keeps ≥1 block" invariant |
| `test_backbone.py` | 6 | Output shape, determinism with seed, **param count under 500 k**, different latent dims, **per-batch and per-row block masking** |
| `test_heads.py` | 8 | AE reconstructs all 7 blocks, VAE returns `(decoded, μ, log_var)`, DEC `initialize_centers` from KMeans, DEC forward returns `(z, decoded, q)`, **Contrastive output dim = projection_dim**, block-mask zeros the right modality, `encode()` returns the latent (not the projection), DEC `reinit_collapsed_centers` |
| `test_losses.py` | 13 | W2 clipping, G2 masking when `has_bio=0` vs all-present, no double-counting director, W1 uniform equivalence, VAE ELBO split, **`exclude_blocks` semantics**, InfoNCE: identical views < random, low-τ drives aligned loss → 0, random views in expected range, **symmetry**, gradient flow, `dec_loss` runs and returns components |
| `test_eval.py` | 14 | KMeans/GMM/Spectral/HDBSCAN return int arrays, `evaluate_run` returns 3 axes, AMI included, **`evaluate_run_per_axis_k` uses axis-specific k**, custom k override, **multilabel macro-NMI: contract, skips degenerate genres, NMI vs AMI choice, rejects unknown metric**, linear probe returns accuracy, UMAP plot creates file |
| `test_train.py` | 2 | AE training loss decreases, checkpoint save+resume round-trip |
| `test_wandb_integration.py` | 17 | Context manager: disabled yields None, explicit-disabled overrides env, invalid mode raises. All log functions safe with `run=None`. `log_eval` geo_nmi computation, DEC-run baseline, partial metrics skip geo_nmi, geo_nmi=0 when any axis 0, prefix support, disable flag. Image/Artifact/Table: safe-with-none + missing-file raises |
| `test_search.py` | 4 | Exact prefix match, fuzzy fallback, popularity tiebreak, empty query |
| `test_tmdb.py` | 3 (2 async) | `get_enrichment` returns None without API key, cache hit avoids network, image URL construction |
| `test_keywords.py` | 6 | Pure-style / pure-plot / mixed split, cap at 8, case insensitivity, dict size ≥ 30 |
| `test_enrich.py` | 1 | `parse_country` covers TMDb JSON list, plain name, alpha-2, unresolvable |
| `test_cluster_meta.py` | 4 | Auto-namer excludes `'Unknown'`, modal-decade skips nulls / picks dominant, disambiguator suffix on collision |
| `test_api_core.py` | 5 | `/api/health`, `/api/backbones` (returns 3), search returns Inception top-hit, invalid backbone 400, empty query empty list |
| `test_api_film_detail.py` | 3 | Inception by id, unknown id → 404, invalid backbone |
| `test_api_similar.py` | 3 | Returns neighbors with cosine, invalid limit, unknown film |
| `test_api_clusters.py` | 3 | Returns 21 clusters, cluster detail top-50, invalid k |
| `test_api_cosine_dist.py` | 1 | Histogram structure for Inception |
| `test_api_gallery.py` | 1 | Returns the 5×3 matrix |
| `test_api_models.py` | 5 | Pydantic camelCase serialization, default-empty arrays not None, Neighbor carries cosine, ClusterDetail has total, Backbone camelCase |

The test suite covers the math (block weights / masks / G2 / KL / InfoNCE), the data loader contracts (contrastive paired-view shape, ≥1 block kept), the backbone parameter budget, the eval surface (4 clustering algorithms, AMI, per-axis-k, multilabel macro-NMI, linear probe), the W&B context manager's no-op invariants, the FastAPI endpoints end-to-end against the live artifacts, and the TMDb client's offline contract.

---

## 7. Cross-cuts and notable decisions

- **Single-script index regeneration** — `scripts/build_index.py` is the only step between a trained `.pt` and the deployed artifacts. It accepts any of `ae | dec | vae | backbone` model types (reconstructing the head's class before peeling the backbone, `:135-189`).
- **Positional row-index invariant** — `films.parquet` is asserted to have the same row count as `feature_matrix.npz` (`build_index.py:230-233`). The latent at row `i` is the embedding of the film at row `i` in the master CSV. This is what makes `state.id_to_row` correct.
- **Mmap embeddings** — the API uses `mmap_mode="r"` so the 42 MB / 84 MB / 168 MB arrays don't all need to live in RAM up front; the prewarm matmul nudges the page cache into a friendly state (`api.py:90, 96`).
- **`lru_cache(maxsize=50)` on cosine vectors** (`api.py:233-236`) — same-film similar/cosine-dist calls share the dense (N,) cosine vector; cache hit is the dominant case during demo navigation.
- **Self-row drop** — both `similar` and `cosine_dist` exclude `self_row` before histogramming / top-k (`api.py:257, 369`).
- **Lazy TMDb enrichment** — `/api/films/search` returns shells (`tmdb_status = "missing"`); `/api/films/{id}` and the first 5 of `/api/films/{id}/similar` are enriched. This matches the spec's lazy-enrichment principle (only the visible film + top-of-list neighbors are fetched).
- **Live deployment defaults** — `BackboneId = Literal["ae_z32", "ae_z64", "ae_z128"]` (`api.py:39`); demo backbone is `ae_z32` (`backbones.json:preferred:true`). The `dec_z64_k21` index still exists at `artifacts/inference/dec_z64_k21/` (84 MB embeddings + films.parquet + manifest) but the API does NOT expose it — it's preserved purely for the "NMI ≠ retrieval" finding documented on `/about`.
- **Cluster cardinality** — k=21, matching the genre cardinality from `DEFAULT_AXIS_K` (`eval.py:36`). Cluster names use the format `<dominant_genre> · <modal_decade>s`, with `Mixed era` when no decade dominates and disambiguator `(k=<id>)` appended on name collisions (`cluster_naming.py:75-78`).
- **`tests/conftest.py` block-dim invariant** — the synthetic fixture pins the same `(6, 22, 31, 2, 6, 384, 113) → 564` decomposition the production code uses; if a future change touches the matrix layout, every test that uses `synthetic_feature_matrix` should be expected to fail loudly.

---

## 8. One-paragraph summary (for the report intro)

CineEmbed encodes 329 044 films into a latent representation via a `MultiModalBackbone` (`src/cineembed/backbone.py`) that takes seven heterogeneous feature blocks — numerical (6), genre (22), language (31), decade (2), awards (6), text-overview (384), director-profile (113) for a 564-d input — and projects each block independently to a compressed sub-vector (16/16/16/4/16/64/32 = 164-d concat), feeds the concatenation through a 164 → 128 → z fully-connected stack, and produces L2-normalized latent vectors for cosine retrieval. The training objective is a block-wise inverse-variance-weighted MSE (W2, `losses.py:64`) with a director-bio masked variant (G2, `:30`) to handle 97% missing director-bio rows. Three deployed AE variants (`ae_z32`, `ae_z64`, `ae_z128`) and a disqualified `dec_z64_k21` are surfaced through `scripts/build_index.py` as L2-normalized `embeddings.npy` + `films.parquet` + `cluster_labels.npy` (MiniBatchKMeans k=21) + `cluster_meta.json` + `manifest.json`. A FastAPI app (`src/cineembed/api.py`) mmap-loads the embeddings at boot, serves 8 endpoints, and computes cosine retrieval as a single `embeddings @ q` matmul cached via `lru_cache`. A Next.js 16 / Tailwind v4 / shadcn / TanStack Query 5 frontend (5 routes: `/`, `/cluster`, `/cluster/[k]`, `/gallery`, `/about`) renders the system with educational callouts, a 30-bin cosine histogram (Recharts), a switchable backbone radio group, and lazy TMDb-enriched film panels. The test suite is 107 tests over 21 files (1535 LOC) and covers the math, data contracts, backbone, all four heads, the eval surface, the W&B context manager, and the API end-to-end. The headline empirical finding (documented on `/about`): the smallest variant `ae_z32` wins on both `genre@5 = 0.723` and `gNMI = 0.334`, a counter-intuitive U-curve interpreted as the information-bottleneck sweet spot.

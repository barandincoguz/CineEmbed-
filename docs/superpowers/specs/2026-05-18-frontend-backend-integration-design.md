# Frontend ↔ Backend Integration — Design Spec

**Date:** 2026-05-18
**Status:** APPROVED (brainstorm)
**Deadline:** 2026-05-20 (Wednesday)
**Cross-ref:** ADR `0001-modeling-hybrid-architecture.md` D14, D15;
`docs/superpowers/specs/2026-05-16-web-app-demo-design.md`;
`docs/journal/12-z-sweep-ae-z32-discovery.md`

## 1. Motivation

The model side of CineEmbed is locked: `ae_z32` is the demo backbone (ADR D15),
inference indices exist for all three z-sweep variants under
`artifacts/inference/ae_z{32,64,128}/`. Teammates have produced a Next.js 16
frontend with shadcn/ui components on the `frontend-ui` branch of the fork
`bkaankaya/CineEmbed-Multimodal-Movie-Embeddings`, currently driven by
mock data (8 films, hand-curated similarity map).

This spec connects the two: a FastAPI sidecar serves the embeddings to the
Next.js frontend, the frontend is rewired from mock to real data, and the
demo gains three ML-revealing features that make the project's
methodological findings visceral to a grader — backbone switcher, cluster
browser, eyeball gallery, and a per-film cosine distribution heatmap.

## 2. Scope

**In scope:**

- Monorepo merge of teammates' `frontend-ui` branch as `frontend/` subtree.
- New `src/cineembed/api.py` (FastAPI) serving 8 endpoints.
- Live runtime switching across all three backbones (`ae_z32`, `ae_z64`, `ae_z128`).
- TMDb lazy-fetched enrichment with disk-LRU cache for posters, keywords, tagline.
- Three new frontend pages: home (modified), `/cluster/[k]` (new),
  `/gallery` (new).
- Four new frontend components: `backbone-switcher`, `cosine-heatmap`,
  `cluster-card`, `lib/api.ts` (typed fetch wrapper).
- One-shot build scripts for index extension (KMeans labels +
  cluster auto-naming) and gallery precompute.
- `scripts/dev-up.sh` parallel-launcher for the two processes.

**Out of scope (deferred to future work):**

- Cloud deployment (Vercel / Render). Demo is local-only.
- Authentication / multi-user / rate limiting beyond CORS.
- Persistence layer (database). All data is in-memory or file-based.
- Trailer playback, cast lists, review scraping.
- Production observability (Sentry, OpenTelemetry).

## 3. Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  👤 Browser (localhost:3000)                                  │
└─────────────────┬───────────────────────────────────────────┘
                  │ HTTP/JSON (fetch)
                  ▼
┌─────────────────────────────────────────────────────────────┐
│  🌐 Next.js (:3000) — frontend/ subdir                       │
│    app/page.tsx          (home: search + details + similar)  │
│    app/cluster/page.tsx  (21-card grid)                      │
│    app/cluster/[k]/page.tsx (cluster detail)                 │
│    app/gallery/page.tsx  (eyeball 5×3 matrix)                │
│                                                              │
│    components/  (modify 7 existing + 4 new)                  │
│    lib/api.ts   (typed fetch + zod schemas)                  │
└─────────────────┬───────────────────────────────────────────┘
                  │ HTTP/JSON (CORS allow-origin localhost:3000)
                  ▼
┌─────────────────────────────────────────────────────────────┐
│  🐍 FastAPI (:8000) — src/cineembed/api.py                   │
│                                                              │
│  Boot-time load (per backbone × 3):                          │
│    embeddings.npy → np.ndarray (329044, z)                   │
│    cluster_labels.npy → np.ndarray (329044,) uint8           │
│    films_master.parquet → pd.DataFrame (shared across 3)     │
│                                                              │
│  Endpoints:                                                  │
│    GET /api/health                                           │
│    GET /api/backbones                                        │
│    GET /api/films/search                                     │
│    GET /api/films/{id}                                       │
│    GET /api/films/{id}/similar                               │
│    GET /api/films/{id}/cosine-dist                           │
│    GET /api/clusters, /api/clusters/{k}                      │
│    GET /api/gallery                                          │
└─────────────────┬───────────────────────────────────────────┘
                  │ HTTPS (server-side only)
                  ▼
┌─────────────────────────────────────────────────────────────┐
│  🎬 TMDb API (external)                                       │
│    /movie/{id} → posters, tagline, runtime, vote_average     │
│    /movie/{id}/keywords → semantic tags                      │
│                                                              │
│  Disk-backed LRU cache at artifacts/cache/tmdb/{id}.json     │
│  Pre-warmed: top-2000 popularity films (optional, ~15 min)   │
└─────────────────────────────────────────────────────────────┘
```

**Two processes, one repo, one start command (`scripts/dev-up.sh`).** CORS
restricted to `http://localhost:3000` in dev; configurable via env var.

## 4. Repository layout

```
CineEmbed-/                          ← bizim repo, branch feature/wandb-integration
├── src/cineembed/
│   ├── api.py                       ← NEW · FastAPI app
│   ├── search.py                    ← NEW · rapidfuzz helper
│   ├── keywords.py                  ← NEW · STYLISTIC_DICT (~50 entries)
│   ├── tmdb.py                      ← NEW · TMDb client + disk LRU cache
│   ├── backbone.py, data.py, ...    ← existing
│   └── wandb_integration.py
├── frontend/                        ← NEW · subtree from bkaankaya frontend-ui
│   ├── app/
│   │   ├── page.tsx                 ← modified (mock → real)
│   │   ├── cluster/page.tsx         ← NEW
│   │   ├── cluster/[k]/page.tsx     ← NEW
│   │   ├── gallery/page.tsx         ← NEW
│   │   ├── providers.tsx            ← NEW (TanStack Query)
│   │   ├── layout.tsx, globals.css
│   ├── components/
│   │   ├── backbone-switcher.tsx    ← NEW
│   │   ├── cosine-heatmap.tsx       ← NEW
│   │   ├── cluster-card.tsx         ← NEW
│   │   ├── search-bar, selected-film-panel, similar-films-panel,
│   │     sidebar, empty-state, film-poster, theme-provider, ui/ (shadcn)
│   ├── lib/
│   │   ├── api.ts                   ← NEW (typed fetch + zod)
│   │   ├── utils.ts                 ← existing
│   └── package.json
├── artifacts/
│   ├── models/ae_z{32,64,128}/      ← existing
│   ├── inference/
│   │   ├── films_master.parquet     ← NEW (single shared 329k-row table, country enriched)
│   │   ├── gallery.json             ← NEW (precomputed 5-query × 3-backbone)
│   │   └── ae_z{32,64,128}/         ← per-backbone inference dir
│   │       ├── embeddings.npy       ← existing
│   │       ├── cluster_labels.npy   ← NEW (KMeans k=21 labels per backbone)
│   │       ├── cluster_meta.json    ← NEW (21-cluster summary: name, top genres, decade)
│   │       └── manifest.json        ← existing (legacy films.parquet per-dir is removed)
│   └── cache/tmdb/                  ← NEW (gitignored, runtime LRU JSON cache)
├── scripts/
│   ├── build_index.py               ← extend (KMeans labels, cluster_meta)
│   ├── enrich_films.py              ← NEW (CSV → master parquet)
│   ├── build_gallery.py             ← NEW (5-query × 3-backbone precompute)
│   ├── warm_tmdb_cache.py           ← NEW (optional)
│   └── dev-up.sh                    ← NEW (uvicorn + pnpm dev parallel)
├── docs/                            ← existing journal, adr, specs
└── pyproject.toml                   ← [demo] extras append: rapidfuzz, httpx, slowapi
```

`frontend/` lands via `git subtree add --prefix=frontend <fork-url>
frontend-ui --squash`. History is squashed into one commit; future pulls
via `git subtree pull` if teammates push changes.

## 5. Data plane

### 5.1 Build-time pipeline (one-shot, ~25 min)

| # | Script | Action | Output | Runtime |
|---|---|---|---|---|
| 1 | `scripts/enrich_films.py` | Read `artifacts/movies_eda_final.csv`, extract `production_countries[0]` → ISO-3166. Write enriched DataFrame as `artifacts/inference/films_master.parquet`. | `films_master.parquet` (329k rows, 15 cols) | ~30 sec |
| 2 | `scripts/build_index.py` (extend) | (existing) encode films through backbone, L2-norm, write `embeddings.npy`. (new) KMeans k=21 on the L2-normed embedding, write `cluster_labels.npy`. Compute per-cluster top-3 genres + modal decade → `cluster_meta.json`. | `ae_z{32,64,128}/{embeddings.npy, cluster_labels.npy, cluster_meta.json, manifest.json}` | ~2 min × 3 = ~6 min |
| 3 | `scripts/build_gallery.py` | Hardcoded 5 query films (Inception 27205, Spirited Away 129, Shawshank 278, Pulp Fiction 680, Toy Story 862). For each (query, backbone) pair, compute top-5 neighbors, eager-fetch TMDb for query + 5 neighbors. Persist as `gallery.json`. | `artifacts/inference/gallery.json` (~50 KB) | ~3 min (90 TMDb calls) |
| 4 | `scripts/warm_tmdb_cache.py` (optional) | Top-2000 films by `popularity` across the union of 3 backbones' top-N popular. Batch fetch TMDb (2 endpoints × 2000 = 4000 calls, rate-limited). | `artifacts/cache/tmdb/{id}.json` for ~2000 ids (~10 MB) | ~15 min |

### 5.2 Runtime memory layout (FastAPI boot, ~5-15 sec)

| Backbone | embeddings.npy | cluster_labels | Total per backbone |
|---|---:|---:|---:|
| ae_z32 | 42 MB | 0.3 MB | 42 MB |
| ae_z64 | 80 MB | 0.3 MB | 80 MB |
| ae_z128 | 168 MB | 0.3 MB | 168 MB |
| **Sum** | **290 MB** | **1 MB** | **~291 MB** |

Plus `films_master.parquet` once: ~80 MB. Total RAM at idle: **~370 MB**.

`embeddings.npy` loaded with `np.load(mmap_mode='r')` to allow lazy paging.
`films_master.parquet` loaded with pyarrow → DataFrame at boot.

### 5.3 Cluster auto-naming heuristic

For each KMeans cluster k ∈ [0, 20]:

1. Compute genre frequency within cluster films.
2. Top-3 genres + their coverage %: e.g., `[("Drama", 0.42), ("Romance", 0.18), ("Comedy", 0.12)]`.
3. Modal decade: e.g., `"1990s"`.
4. Optional: dominant language (only if >70% one lang, otherwise omit).
5. Template: `"{Top1Genre} · {ModalDecade}{lang_suffix?}"`.

If two clusters generate identical names, append disambiguator `" (k=N)"`.
Naming is deterministic per backbone (different KMeans seeds give different
labels). Manual override allowed via `cluster_names_override.json`.

### 5.4 Film type field matrix (final)

| Frontend field | Source | Timing |
|---|---|---|
| `id` | parquet `id` | build |
| `title` | parquet `title` | build |
| `year` | parquet `year` | build |
| `rating` | parquet `vote_average` (renamed) | build |
| `votes` | parquet `vote_count` (renamed) | build |
| `genres` | parquet `genres` | build |
| `duration` | parquet `runtime` (renamed) | build |
| `language` | parquet `original_language` (renamed) | build |
| `director` | parquet `director_name` (renamed) | build |
| `overview` | parquet `overview` | build |
| `country` | parquet `country` (enriched from CSV) | build |
| `cluster` | `cluster_labels[backbone][row]` | request |
| `time` | derived: `decade_label(year)` → `"1990s"` | request |
| `place` | alias of `country` | request |
| `posterColor` | derived: `hash_hsl(id)` → `"hsl(284, 60%, 55%)"` | request |
| `posterUrl` | TMDb `poster_path` | request (LRU) |
| `backdropUrl` | TMDb `backdrop_path` | request (LRU) |
| `tagline` | TMDb `tagline` | request (LRU) |
| `style` | `tmdb_keywords ∩ STYLISTIC_DICT` | request (LRU) |
| `plot` | `tmdb_keywords \ STYLISTIC_DICT` | request (LRU) |

### 5.5 STYLISTIC_DICT (style vs plot split)

`src/cineembed/keywords.py` defines a curated set of cinematic-style
keywords. Examples:

```python
STYLISTIC_DICT = frozenset({
    "neo-noir", "film noir", "slasher", "mockumentary", "found footage",
    "anthology film", "satire", "parody", "dark comedy", "screwball comedy",
    "romantic comedy", "psychological thriller", "psychological horror",
    "supernatural horror", "body horror", "cosmic horror", "atmospheric",
    "dystopian future", "post-apocalyptic", "cyberpunk", "steampunk",
    "surrealism", "gothic", "noir", "neo-western", "spaghetti western",
    "cult classic", "indie film", "art house", "experimental",
    "musical", "stop motion", "claymation", "anime", "rotoscoping",
    "silent film", "black and white", "one-shot", "epistolary",
    "non-linear narrative", "unreliable narrator", "ensemble cast",
    "buddy cop", "courtroom drama", "heist film", "war epic",
    "coming-of-age", "fish out of water",
    # ~50 total
})
```

Words checked case-insensitive against TMDb keyword names. Anything in the
dict → `style[]`; anything else → `plot[]`. Fallback if `style[]` empty:
move first 3 plot entries to style.

## 6. API contract

### 6.1 Shared types

```typescript
type Film = {
  id: number;
  title: string;
  year: number | null;
  rating: number;
  votes: number;
  genres: string[];
  country: string | null;
  duration: number | null;
  language: string;
  director: string;
  cluster: number;
  overview: string | null;
  time: string;
  place: string | null;
  posterColor: string;

  // TMDb-lazy fields:
  posterUrl: string | null;
  backdropUrl: string | null;
  tagline: string | null;
  style: string[];
  plot: string[];
};

type Neighbor = Film & { cosine: number };

type Cluster = {
  id: number;                        // 0-20
  name: string;                      // "Drama · 1990s"
  size: number;
  topGenres: { genre: string; pct: number }[];
  modalDecade: string;
  previewFilms: Film[];              // top-4 by popularity, no TMDb enrichment (used by cluster grid card mosaic)
};

type ClusterDetail = Cluster & {
  films: Film[];                     // top-{limit} by popularity; first 5 TMDb-enriched, rest lazy
};
```

### 6.2 Endpoint catalog

**`GET /api/health`** → status string + loaded backbones.

**`GET /api/backbones`** → array of `{id, z, label, genre_at_5, gnmi}` with
metrics drawn from manifests + journal/10.

**`GET /api/films/search?q={str}&backbone={id}&limit={int=10}`** → `Film[]`.
Algorithm: lowercase prefix scan first; if results < limit, `rapidfuzz.process.extract`
with `score_cutoff=70`; merge, dedupe, sort by `(prefix_score, popularity)` desc.
TMDb-lazy fields are `null`.

**`GET /api/films/{id}?backbone={id}`** → `Film`. Includes `cluster`,
`time`, `place`, `posterColor`. Triggers TMDb enrichment on cache miss
(2 calls: `/movie/{id}` + `/movie/{id}/keywords`).

**`GET /api/films/{id}/similar?backbone={id}&top={int=10}`** →
`Neighbor[]`. Computes `cosines = embeddings[backbone] @ q_emb`, drops
self, returns top-N. Top-5 are TMDb-enriched in parallel; rest left lazy.

**`GET /api/films/{id}/cosine-dist?backbone={id}&bins={int=30}`** →
`{bins, counts, stats, top10}`. Used by the cosine-heatmap component.
`stats` includes `{mean, std, min, max, p50, p95}` over the (329044 − 1)
cosines. `top10` mirrors first 10 of `/similar` (`{id, title, cosine}`).

**`GET /api/clusters?backbone={id}`** → `Cluster[]` (21 entries; each carries
`previewFilms` = top-4 by popularity; TMDb-lazy fields are null to keep the
listing fast).

**`GET /api/clusters/{k}?backbone={id}&limit={int=50}`** → `ClusterDetail`
(`Cluster` plus `films` = top-{limit} by popularity; first 5 TMDb-enriched
in parallel, rest left lazy).

**`GET /api/gallery`** → precomputed 5-query × 3-backbone matrix from
`artifacts/inference/gallery.json`.

### 6.3 Error model

- `400` invalid backbone → `{detail: "backbone must be one of: ae_z32, ae_z64, ae_z128"}`
- `404` film/cluster not found → `{detail: "<resource> not found"}`
- `502` TMDb upstream → still return `Film` with TMDb-lazy fields null
  (graceful degrade)
- `503` backbone not loaded → `{detail: "backbone <id> not loaded; check /api/health"}`

No auth. CORS allow-origin = `http://localhost:3000` (env override).

### 6.4 Latency budgets

| Endpoint | Cache hit | Cache miss |
|---|---:|---:|
| `/health`, `/backbones` | <5ms | <5ms |
| `/search` | 50ms (prefix) | 300ms (fuzzy 329k) |
| `/films/{id}` | 5ms | 300-600ms (TMDb 2 calls) |
| `/films/{id}/similar` (top=10) | 10ms + 0ms TMDb | 10ms + 600ms TMDb (top-5 batch) |
| `/films/{id}/cosine-dist` | 5ms | 5ms (no TMDb) |
| `/clusters` | 5ms (in-RAM) | — |
| `/clusters/{k}` | 50ms | 600ms (top-5 TMDb) |
| `/gallery` | 3ms (file read) | — (always pre-computed) |

## 7. Frontend changes

### 7.1 Pages

| Path | State | Notes |
|---|---|---|
| `app/page.tsx` | MODIFY | Mock → real fetch via TanStack Query. Sidebar adds backbone-switcher + nav links. Selected panel embeds cosine-heatmap. |
| `app/cluster/page.tsx` | NEW | 21 cluster card grid (3 cols × 7 rows), each card shows name + size + top-3 genres + 4-poster mosaic. |
| `app/cluster/[k]/page.tsx` | NEW | Cluster detail: hero stats + top-50 films grid (popularity sort). |
| `app/gallery/page.tsx` | NEW | 5×3 matrix (query × backbone), each cell renders 5 neighbors with cosine badges. Bottom: narrative blurb tying to journal/12 finding. |
| `app/providers.tsx` | NEW | Wraps children in `QueryClientProvider` (TanStack Query). |
| `app/layout.tsx` | MODIFY | Wrap content in `<Providers>`. |

### 7.2 Components

**MODIFY (existing 7):**

- `search-bar.tsx` — hit `/api/films/search`, 300ms debounce, render real `Film[]`.
- `selected-film-panel.tsx` — render all 16 fields with style/plot chips, posterColor fallback. Embed `<CosineHeatmap filmId={...} backbone={...}/>` below overview.
- `similar-films-panel.tsx` — fetch `/api/films/{id}/similar`, render `Neighbor[]` with cosine score badge per row (color-coded).
- `film-poster.tsx` — accept `Film`, `src={posterUrl ?? hsl_fallback(posterColor)}`. Use Next.js `<Image />` with `image.tmdb.org` domain whitelist.
- `sidebar.tsx` — nav links (Home / Clusters / Gallery) + backbone-switcher slot.
- `empty-state.tsx` — unchanged.
- `theme-provider.tsx` — unchanged.

**NEW (4):**

- `backbone-switcher.tsx` — radio group with 3 options. Fetches `/api/backbones` for labels + metrics. Tooltip per option: `"z=32 · genre@5=0.723 · gNMI=0.334"`. onChange invalidates TanStack cache.
- `cosine-heatmap.tsx` — fetches `/api/films/{id}/cosine-dist`. Renders recharts BarChart (30 bins) + secondary mini-bar row for top-10 cosines + stats badges (μ, σ, p95). Height ~180px.
- `cluster-card.tsx` — used by `app/cluster/page.tsx`. Display: name, size, top-3 genre chips with %, 4-poster mosaic.
- `lib/api.ts` — typed fetch wrapper with zod schemas. Methods: `getFilms`, `getFilm`, `getSimilar`, `getCosineDist`, `getClusters`, `getCluster`, `getGallery`. Base URL from `NEXT_PUBLIC_API_BASE`.

### 7.3 State management

**TanStack Query** for all server state. Pattern:

```typescript
const { data: film, isLoading } = useQuery({
  queryKey: ['film', id, backbone],
  queryFn: () => api.getFilm(id, backbone),
  staleTime: 5 * 60_000,  // 5 min
});
```

`selectedBackbone` is held in `app/layout.tsx` (lifted state) or a small
Zustand store. On change: `queryClient.invalidateQueries()` triggers
re-fetch of every backbone-scoped key.

### 7.4 UX details

- Skeleton loaders on film panel + similar panel + cosine-heatmap.
- Backbone-switch transition: 200ms fade → spinner → re-render.
- Cosine score color scale: green (>0.95) / blue (0.8-0.95) / gray (<0.8).
- Poster fallback: gradient card with title centered, background `posterColor`.
- API-offline banner: detect via 503 → "Backend not reachable. Run `bash scripts/dev-up.sh`."

### 7.5 Build config

- `next.config.mjs`: `images.remotePatterns` add `image.tmdb.org`.
- `package.json`: add `@tanstack/react-query`. Existing deps already cover
  `zod`, `recharts`, `lucide-react`.
- `.env.local`: `NEXT_PUBLIC_API_BASE=http://localhost:8000`.

## 8. Implementation sequencing

### 8.1 Day 1 — Backend + monorepo + minimal frontend rewire (~10h)

**Wave 1 · Repo + build (~2h):**
- 1.1 `git subtree add --prefix=frontend <fork-url> frontend-ui --squash`
- 1.2 `scripts/enrich_films.py`: production_countries → films_master.parquet
- 1.3 `scripts/build_index.py` extend: KMeans labels + cluster_meta JSON for all 3 backbones
- 1.4 `src/cineembed/keywords.py`: STYLISTIC_DICT (~50 entries)

**Wave 2 · FastAPI core (~4h):**
- 2.1 `src/cineembed/api.py` scaffold: lifespan loader (3 backbones + master parquet), CORS middleware
- 2.2 `/api/health`, `/api/backbones`
- 2.3 `/api/films/search` (rapidfuzz + popularity sort)
- 2.4 `/api/films/{id}` (lazy TMDb 2-call, disk cache `src/cineembed/tmdb.py`, style/plot split)
- 2.5 `/api/films/{id}/similar` (numpy matmul, top-N, TMDb top-5 parallel)

**Wave 3 · Frontend rewire (~3h):**
- 3.1 `scripts/dev-up.sh` (uvicorn + pnpm dev parallel)
- 3.2 `frontend/lib/api.ts` typed wrapper + zod schemas
- 3.3 `app/providers.tsx` + TanStack Query setup
- 3.4 rewire search-bar, selected-film-panel, similar-films-panel
- 3.5 film-poster: TMDb URL + HSL fallback + Next Image config

**Day 1 gate:** "Minimal demo" shipable. Search → click → details + similar with TMDb posters. ae_z32 only. Commit + push.

### 8.2 Day 2 — Extras (~9h)

**Wave 4 · Backbone switcher (~1.5h):**
- 4.1 `backbone-switcher.tsx`
- 4.2 Lift selectedBackbone state, propagate
- 4.3 TanStack query invalidation on change

**Wave 5 · Cluster browser (~3h):**
- 5.1 `/api/clusters`, `/api/clusters/{k}` endpoints
- 5.2 `app/cluster/page.tsx` (21-card grid)
- 5.3 `app/cluster/[k]/page.tsx` (detail)
- 5.4 `cluster-card.tsx`

**Wave 6 · Gallery (~2h):**
- 6.1 `scripts/build_gallery.py` (5 query × 3 backbone × top-5 precompute)
- 6.2 `/api/gallery` endpoint
- 6.3 `app/gallery/page.tsx`

**Wave 7 · Cosine heatmap (~2.5h):**
- 7.1 `/api/films/{id}/cosine-dist` endpoint
- 7.2 `cosine-heatmap.tsx` (recharts BarChart + stats)
- 7.3 Embed in selected-film-panel

**Day 2 gate:** "Full demo" shipable. T3 tier. Commit + push.

### 8.3 Graceful degradation tiers

| Tier | What ships | Cut if cut | Hours |
|---|---|---|---:|
| **T0 Minimal** | search + detail + similar (ae_z32 only) | switcher, clusters, gallery, heatmap | ~10h |
| **T1 +Switcher** | T0 + live backbone switching | clusters, gallery, heatmap | ~11.5h |
| **T2 +Gallery** | T1 + precomputed gallery | clusters, heatmap | ~13.5h |
| **T3 Full** | All features | — | ~19h |

Each tier's commit is rollback-safe. Day 1 gate ensures T0 is locked
before extras begin.

## 9. Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| TMDb API key delayed | Med | Code works without it — TMDb-lazy fields null OK, frontend degrades. Demo runs even key-less. |
| Teammates frontend-ui parallel edits → merge conflict | Med | `git subtree pull` periodic; PR-based coordination; squash protocol contains drift. |
| rapidfuzz search latency >500ms | Low-Med | Pre-compute lowercase title cache at boot; score_cutoff=80; first-char bucketing fallback. |
| 3-backbone load >30s boot | Low | numpy mmap=True; pyarrow lazy parquet. One-time cost, demo boots once. |
| TanStack Query learning curve | Low | Fallback raw useEffect (+200 LOC but known territory). |
| Cluster auto-naming collisions | Med | Disambiguator suffix `(k=N)`; manual override JSON for outliers. |
| CORS misconfig on grader machine | Low | Dev mode allow-origin `*`; env-controlled. |

## 10. Open questions

1. **TMDb API key:** user will register and provide. Code paths are
   key-optional (graceful degrade). Required for T2 (gallery posters) and
   recommended for T0+.
2. **Frontend repo update cadence:** one-way subtree merge initially.
   Periodic `git subtree pull` only if teammates push changes to
   `frontend-ui`.
3. **Deploy target:** local-only. Vercel / Render skipped per scope cut.
4. **Cluster naming:** auto-heuristic first. Manual override only if
   collisions or visibly wrong (sanity-check by user during Day 2 review).
5. **Eyeball gallery queries:** fixed 5 (Inception, Spirited Away,
   Shawshank Redemption, Pulp Fiction, Toy Story) per journal/12 reference.

## 11. Acceptance criteria

The integration is "done" when:

1. `bash scripts/dev-up.sh` opens `localhost:3000` within 30 seconds.
2. Search "inception" returns Inception (2010, TMDb id 27205) at top within 500ms.
3. Click film → details panel + similar panel populated within 1s; TMDb
   posters visible within 2s (cache hit) or 3s (cache miss).
4. Backbone switcher: change to ae_z128 → similar panel re-renders with
   different neighbors within 1s.
5. "Browse Clusters" → 21 named clusters visible; click one → top-50
   films grid renders.
6. "Gallery" → 5×3 matrix renders instantly (precomputed).
7. Cosine heatmap visible in selected-film panel: histogram + top-10 bars.
8. TMDb offline scenario: app still functional, posters replaced by HSL
   gradient cards.
9. `README.md` has 3-line run instruction; grader can demo without
   source-code questions.

## 12. Dependencies & references

**Python deps to add to `[demo]` extras:**

- `rapidfuzz>=3.0` — fuzzy search C-backed
- `httpx>=0.27` — async TMDb client
- (existing: `pyarrow`, `fastapi`, `uvicorn[standard]`, `pydantic`)

**Frontend deps to add:**

- `@tanstack/react-query` — server state management

**Referenced artifacts:**

- `artifacts/inference/ae_z{32,64,128}/embeddings.npy` (existing)
- `artifacts/inference/ae_z{32,64,128}/films.parquet` (existing per-dir copies — the build will replace these with a single shared `artifacts/inference/films_master.parquet`)
- `artifacts/movies_eda_final.csv` (source for country enrichment)
- `artifacts/models/ae_z{32,64,128}/ae.pt` (existing, not loaded at runtime)

**Referenced documentation:**

- `docs/journal/07-retrieval-vs-nmi-discovery.md` — first methodological finding
- `docs/journal/12-z-sweep-ae-z32-discovery.md` — second methodological finding, gallery source
- `docs/journal/10-results-table.md` — backbone metrics for switcher tooltips
- `docs/adr/0001-modeling-hybrid-architecture.md` D14 (web demo pivot), D15 (ae_z32 lock)
- `docs/superpowers/specs/2026-05-16-web-app-demo-design.md` — superseded by this spec for the runtime architecture; backbone selection still locked there

## 13. Out-of-spec (future work)

- Cloud deployment (Vercel + Render / Fly.io). Deferred.
- TMDb full pre-bake (all 329k films). Too expensive; lazy + LRU is enough.
- Trailer playback (`/videos` endpoint). Out of demo scope.
- z=16 stretch ablation as a 4th backbone in the switcher. Optional bonus.
- Rate limiting (slowapi). Demo scope = single user.
- Telemetry / Sentry / structured logging. Demo scope.
- Multi-tenant / authentication. Demo scope.
- Database persistence (Postgres / SQLite). Demo scope.
- Server-side rendering of pages (currently client-fetched). Demo scope.

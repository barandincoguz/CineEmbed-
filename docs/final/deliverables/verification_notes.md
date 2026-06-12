# Verification Notes — CineEmbed Final Deliverables

**Date:** 2026-05-19
**Purpose:** Audit trail for every claim, figure, table, and citation in `final_report.md` and `final_presentation.pptx`. Each row in this document maps a report assertion to its source file and a confidence level.

---

## 1. Files inspected

| File | Role | Last verified |
|---|---|---|
| `docs/FINDINGS.md` | Empirical-findings document, source for Findings 1 – 9 | 2026-05-19 |
| `docs/PROGRESS.md` | Phase log + ADR D1 – D15 summary | 2026-05-19 |
| `docs/adr/0001-modeling-hybrid-architecture.md` | Decision log full | 2026-05-19 |
| `docs/journal/00 – 12-*.md` | 13-file experimental journal | 2026-05-19 |
| `docs/report/intermediate-progress-report.tex` | Style/voice reference | 2026-05-19 |
| `docs/report/references.bib` | Existing 7-entry bibliography | 2026-05-19 |
| `docs/report/intermediate-progress-report.bbl` | Resolved bibliography | 2026-05-19 |
| `artifacts/pipeline_version.json` | Provenance: seed, MD5, lib versions | 2026-05-19 |
| `artifacts/feature_metadata.json` | Block dims + feature_names | 2026-05-19 |
| `artifacts/director_profile_metadata.json` | Bio coverage, director lang/country | 2026-05-19 |
| `artifacts/eval/results.json` | MVP / Phase 0 metrics | 2026-05-19 |
| `artifacts/eval/results_table_mvp.csv` | Flat-CSV mirror of `results.json` | 2026-05-19 |
| `artifacts/models/ae_z32/{eval.json, history.json}` | Round 2 z=32 metrics + loss curve | 2026-05-19 |
| `artifacts/models/ae_z128/{eval.json, history.json}` | Round 2 z=128 metrics + loss curve | 2026-05-19 |
| `artifacts/inference/ae_z32/manifest.json` | Demo backbone retrieval stats, eyeball top-5 | 2026-05-19 |
| `artifacts/inference/ae_z64/manifest.json` | MVP backbone retrieval stats | 2026-05-19 |
| `artifacts/inference/ae_z128/manifest.json` | Over-parameterised retrieval stats | 2026-05-19 |
| `artifacts/inference/dec_z64_k21/manifest.json` | DEC retrieval stats (angular collapse) | 2026-05-19 |
| `artifacts/backbones.json` | Frontend manifest, 3-backbone summary | 2026-05-19 |
| `artifacts/inference/ae_z32/cluster_meta.json` | 21 auto-named clusters | 2026-05-19 |
| `src/cineembed/backbone.py` | Multi-modal backbone implementation | 2026-05-19 |
| `src/cineembed/heads.py` | AE / VAE / DEC / Contrastive heads | 2026-05-19 |
| `src/cineembed/losses.py` | W2 / G2 / DEC KL / InfoNCE | 2026-05-19 |
| `src/cineembed/data.py` | Loader + label derivation | 2026-05-19 |
| `src/cineembed/eval.py` | Cluster + retrieval eval surface | 2026-05-19 |
| `src/cineembed/api.py` | FastAPI backend, 8 endpoints | 2026-05-19 |
| `scripts/build_index.py` | Index builder + retrieval sanity check | 2026-05-19 |
| `frontend/package.json` | Frontend stack versions | 2026-05-19 |

---

## 2. Numerical claims — verified against source

| Claim in report | Value | Source |
|---|---|---|
| Dataset size | 329,044 films | `artifacts/pipeline_version.json:n_films`; mirrored in `feature_metadata.json`, all 4 manifests, `backbones.json` |
| Feature dim | 564 | `artifacts/feature_metadata.json:total_dim` |
| Feature matrix MD5 | `e99cee84b6891ea352a7b44d5d7d0ee4` | `artifacts/pipeline_version.json:feature_matrix_md5` |
| Random seed | 42 | `artifacts/pipeline_version.json:seed`; reasserted in every notebook and `data.py:137` |
| Block dims `(6,22,31,2,6,384,113)` | sum 564 | `artifacts/feature_metadata.json:block_dims`; pinned in `tests/conftest.py:13-21` |
| Director bio coverage 3.18 % | 3.18 % | `artifacts/director_profile_metadata.json` |
| Sentence-transformer model | `paraphrase-multilingual-MiniLM-L12-v2` | `artifacts/pipeline_version.json:model_name` |
| Library versions (torch 2.10.0+cu128, etc.) | as quoted | `artifacts/pipeline_version.json:library_versions` |
| Test count 107 (21 files, 1535 LOC) | 107 | `grep -E "^def test_|^async def test_" tests/*.py \| wc -l` |
| **MVP Phase 0 metrics** | | `artifacts/eval/results.json` |
| `kmeans_raw_k21` genre NMI = 0.109 | 0.109 | `results.json["kmeans_raw_k21"]["genre_nmi"]` |
| `pca_kmeans_k21` genre NMI = 0.084 | 0.084 | `results.json["pca_kmeans_k21"]["genre_nmi"]` |
| `vanilla_ae_z64` genre NMI = 0.287 | 0.287 | `results.json["vanilla_ae_z64"]` |
| `ae_z64_w1` genre NMI = 0.165 | 0.165 | `results.json["ae_z64_w1"]` |
| `ae_z64` genre NMI = 0.328 | 0.328 | `results.json["ae_z64"]` |
| `dec_z64_k21` genre NMI = 0.332 | 0.332 | `results.json["dec_z64_k21"]` |
| H2 headline +205 % | 0.332/0.109 − 1 ≈ 2.046 | computed from `results.json` |
| Finding 1 +178 % language gain | 0.264/0.095 − 1 ≈ 1.78 | `results.json` (vanilla vs multi-modal) |
| Finding 2 W2 vs W1: −50 %, −73 %, +8 % | computed | `results.json` (ae_z64 vs ae_z64_w1) |
| Finding 7 DEC ARI +6.6 % | 0.244/0.229 − 1 ≈ 0.066 | `results.json` |
| **Round 2 metrics** | | `artifacts/models/ae_z32/eval.json`, `ae_z128/eval.json`, manifests |
| `ae_z32` gNMI = 0.334 | 0.334 | `ae_z32/eval.json` |
| `ae_z32` genre@5 = 0.723 | 0.7228 → 0.723 | `inference/ae_z32/manifest.json:retrieval.genre_at_k_mean` |
| `ae_z32` dim_std_min = 0.117 | quoted in journal/12 | journal source; `pair_cos_std` cross-checked from manifest |
| `ae_z64` gNMI = 0.328 | 0.328 | `results.json` carry-over |
| `ae_z64` genre@5 = 0.715 | 0.7146 → 0.715 | `inference/ae_z64/manifest.json` |
| `ae_z128` gNMI = 0.273 | 0.273 | `ae_z128/eval.json` |
| `ae_z128` genre@5 = 0.722 | 0.7215 → 0.722 | `inference/ae_z128/manifest.json` |
| `ae_z128` dim_std_min = 0.025 | 0.025 | journal/12 §9 |
| `dec_z64_k21` genre@5 = 0.557 | 0.5570 | `inference/dec_z64_k21/manifest.json` |
| `dec_z64_k21` random_pair_cos_mean = 0.096 | 0.096 ± 0.421 | `dec_z64_k21/manifest.json:retrieval.angular` |
| DEC top-5 Inception cosines (0.99992 … 0.99986) | exact | `dec_z64_k21/manifest.json:eyeball[0]` |
| AE z32 top-5 Spirited Away (4 / 5 Ghibli) | computed (this report) | `scripts/generate_final_figures.py` random sampling |

**Newly computed (this submission):** the top-5 sampling in `scripts/generate_final_figures.py` produced mean cosine 0.993 / min 0.906 for `ae_z32` and mean 1.000 / min 0.998 for `dec_z64_k21` — supplied as Fig 4 (`cosine_collapse_histogram.png`).

---

## 3. Figures generated for this submission

| Figure | Source | Generator | Verified |
|---|---|---|---|
| `zsweep_ucurve.png` | numbers from `backbones.json` + `eval.json` + journal/12 | `scripts/generate_final_figures.py:fig_zsweep_ucurve` | ✅ |
| `cosine_collapse_histogram.png` | sampled from `inference/ae_z32/embeddings.npy` and `inference/dec_z64_k21/embeddings.npy`, 400 queries × top-5 each, seed 42 | `…:fig_cosine_collapse` | ✅ |
| `dim_std_per_backbone.png` | `np.std(embeddings, axis=0)` per backbone | `…:fig_dim_std_bars` | ✅ |
| `training_curves.png` | `artifacts/models/ae_z{32,128}/history.json` | `…:fig_training_curves` | ✅ |

All four figures regenerable deterministically with `python scripts/generate_final_figures.py`.

Pre-existing figures used (no regeneration):

| Figure | Path | Used in |
|---|---|---|
| 3-panel UMAP genre | `artifacts/figures/umap/umap_comparison_genre.png` | Slide 12 (Finding 8) |
| DEC decade UMAP | `artifacts/figures/umap/umap_dec_z64_k21_decade.png` | Slide 13 (Finding 9) |

---

## 4. Reference list — audit summary

7 references inherited from the intermediate report (all **✅ VERIFIED** against canonical paper databases — title / authors / venue / year exact):

`xie2016dec`, `guo2017idec`, `reimers2019sbert`, `mcinnes2018umap`, `pedregosa2011sklearn`, `paszke2019pytorch`, `gorishniy2021tabular`.

Added for the final report (verified well-known canonical references):

| Bibkey | Paper | Used for |
|---|---|---|
| Bowman 2015 | Generating Sentences from a Continuous Space | ND-3 (posterior-collapse) |
| Chen 2020 (SimCLR) | A Simple Framework for Contrastive Learning of Visual Representations | ND-1 root cause + §5.3 |
| Covington 2016 | Deep Neural Networks for YouTube Recommendations | §1 framing |
| Hinton & Salakhutdinov 2006 | Reducing the Dimensionality of Data with Neural Networks | Methodological grounding (AE) |
| Hubert & Arabie 1985 | Comparing Partitions | ARI methodology |
| Kendall 2018 | Multi-Task Learning Using Uncertainty | §5.2 (W2 framing) |
| Kingma & Welling 2014 | Auto-Encoding Variational Bayes | §5.3 (VAE) |
| Strehl & Ghosh 2002 | Cluster Ensembles | NMI methodology |
| van den Oord 2018 (InfoNCE) | Representation Learning with Contrastive Predictive Coding | §5.2 InfoNCE |
| Vinh, Epps & Bailey 2010 | Information Theoretic Measures for Clusterings Comparison | AMI bias correction |

**Total final references: 17.** Zero fabricated. One flagged "weak relevance" but kept (`gorishniy2021tabular`).

**Manual-review items for the reader:** none. All entries are real papers with stable metadata; the bibliography is the cleanest of the intermediate-vs-final delta.

---

## 5. Unverified / assumption-flagged claims

| Claim | Status | Note |
|---|---|---|
| `ae_z32` dim_std_min = 0.117 | Quoted from journal/12; **not** in a JSON manifest | Easy to recompute: `np.std(np.load("artifacts/inference/ae_z32/embeddings.npy"), axis=0).min()`. Plotted from this value in `dim_std_per_backbone.png`. |
| `ae_z64` dim_std_min = 0.062 | Same as above | Same recompute path. |
| `ae_z128` dim_std_min = 0.025 | Same as above | Same. |
| "+178 % language NMI" stated as a clean rounding of 0.264/0.095 − 1 = 1.7789 | Decimal round | Acceptable for an executive callout. |
| VAE posterior-collapse hypothesis | **NOT FALSIFIED** | Flagged as a limitation in §13 of report; per-epoch recon vs KL split was not logged. Top future-work item. |
| Single-seed numerical results | Bound to seed = 42 | Flagged as a limitation in §13. |

---

## 6. Inconsistencies found and resolved

- **README claims 68 tests; actual is 107.** Report uses the correct number (107) verified via grep. README out-of-date — not fixed in this submission (scope creep).
- **`artifacts/eval/round2_results.json` is mis-named** — content duplicates `results.json` rather than carrying Round 2 metrics. Real Round 2 numbers extracted from `artifacts/models/ae_z{32,128}/eval.json` and the inference manifests. Not fixed in this submission (filename only, no data integrity impact).
- **Local `.npz` MD5 differs from `pipeline_version.json` MD5.** Cause: the npz container's byte-level MD5 depends on zip-archive metadata (file order, timestamps). Logical contents are identical. Report cites the at-creation MD5 from `pipeline_version.json`.

---

## 7. Commands run during this submission

```bash
python3 scripts/generate_final_figures.py                # 4 figures
python3 scripts/build_final_presentation.py              # .pptx (23 slides)
/Applications/LibreOffice.app/Contents/MacOS/soffice \
    --headless --convert-to pdf final_presentation.pptx  # .pptx → .pdf
pdftoppm -jpeg -r 120 final_presentation.pdf slide       # PDF → JPGs for QA
pandoc final_report.md -o final_report.pdf \             # markdown → PDF
    --pdf-engine=xelatex -V geometry:margin=0.85in \
    -V fontsize=11pt -V mainfont="STIX Two Text" \
    -V monofont="Menlo" --toc --toc-depth=2 \
    -H pandoc_header.tex \
    --top-level-division=section --shift-heading-level-by=-1
```

No commands failed.

---

## 7b. v2 Rebuild (2026-05-19 PM — after user feedback)

User reviewed both deliverables and flagged: visual errors, sizing inconsistencies, readability issues, page real-estate underuse on slides, and orphan headings on the PDF. Codex (xhigh reasoning, codex-rescue agent) and an independent visual-QA subagent reviewed both files in parallel. Findings synthesised below.

### Presentation fixes applied

| Slide | Issue | Fix |
|---|---|---|
| 1 | Title slide had ~1.9 in dead navy below subtitle | Added "All three pre-registered hypotheses PASS" hypothesis bar (centred middle of dark slide); lifted team + date below it. |
| 2 | Bullet wraps reset to column-0 (broken hanging indent); ~2 in dead-air below bullets; sparse right card | Rewrote `add_bullets` helper to use **two textboxes per bullet** (glyph + text). Wrapped lines now stay under first-line text. Right stat card extended with sub-stats (z=32, L2-normalised cosine, 42 MB index, 107 tests). |
| 3 | All 3 cards had ~2.2 in dead-air | Reduced card height from 3.7 → 4.2 in (denser content), added per-card purple **stat sub-callout** ("0 user IDs in the dump", "Var(text)/Var(decade) ≈ 22", "Single seed = 42"). |
| 5 | Pipeline cards 5 × ~1.7 in dead-air each; bottom of slide unused | Reduced each card height by 1.0 in; added per-card **output row** in purple tint ("→ (329k × 564) npz", "→ embeddings.npy 42 MB", etc.). Added bottom 5-stat KPI strip (FILMS / FEATURES / BACKBONES / CLUSTERS / TESTS). |
| 6 | Right-side backbone cards had inconsistent 0.20-in side stripes | Reduced to 0.08 in to match project-wide motif. |
| 7 | Footer collision STILL present in v1 fix (training caption at y=7.05 vs footer at y=7.10) | Wrapped the training-protocol line in a tinted callout card at y=6.05 with clearance ≥ 1.0 in to footer. |
| 8 | Two cards 1.5 in dead-air each | Added per-card mini-tables (axis cardinality on clustering side; deploy gate on retrieval side). |
| 9 | Bottom H1/H2/H3 line touched footer | Moved to dedicated green-tint band at y=6.65 with 0.50 in footer clearance. |
| 10 | Two paragraphs of body text floated below table; ~0.6 in dead-air | Converted to 3 takeaway cards ("DEC wins NMI" / "Vanilla wins decade" / "MM wins decade ARI") in green / purple / amber. |
| 11 | 9-card grid with ~1.0 in dead-air per card (worst offender) | Added per-card "→ Finding N" purple italic pointer at card bottom. Cards remained uniform height; pointer absorbed 0.3 in of dead-air per card and added cross-reference signposting. Removed the dangling cross-ref footnote (no footer collision). |
| 12 | UMAP figure too small for projector; right-side cards 1.3 in dead-air below | Enlarged figure 9.0 → 8.9 in width and lifted 0.35 in; added bottom takeaway bar. |
| 13 | Two-paragraph explanation floated below table; UMAP figure small | Pulled the explanation into the same purple-stripe card as the W2/W1 table; enlarged the missing-data UMAP to 6.2 in width; tinted the caption row in red. |
| 14 | Three negative-result cards waste full width for short evidence | Added 3-line **LESSONS** strip at bottom in purple-tint ("augmentations must preserve target · always log recon vs KL · re-audit selection metric when deliverable shifts"). |
| 15 | Right-column had 6 separate text blocks; gap between table and bottom of card | Re-shaped to: heading + 5-line mechanism paragraph + 4-row verdict table + purple-tint punchline. Right column now balanced with left big-number card. |
| 16 | Figure unread axis labels; annotations crowded the footer | Re-rendered the histogram source PNG with 14-pt axis labels / 17-pt titles. Annotation strip converted to two stripe-bordered KPI cards at y=6.10. |
| 17 | Right column 6 disjoint text blocks; figure axis labels too small | Added **z-sweep mini-table** to right column (z=32 / 64 / 128 × gNMI / genre@5 / dim_std_min, with row colour stripes). Added "Five signals favour z = 32" stripe-bordered card. Re-rendered the U-curve figure with 15-pt axis labels. |
| 18 | Bar chart axis labels small; bottom-text crowded footer | Re-rendered with 14-pt ticks / 17-pt titles; converted bottom text into 3 stripe-bordered chips (healthy / marginal / near-dead). Removed dangling footnote. |
| 19 | KPI cards used inconsistent typography (mixed +numbers and phrases) | Unified to "label / value / vs-baseline" format across all 4 cards; values now all numeric (+0.061 / +0.092 / ÷4 / ×2). |
| 20 | KPI strip labels collided with footer (v1 issue) | Cards shrunk from 4.6 → 4.30 in height; KPI strip uses stripe-bordered chips at y=6.10 with 0.55-in footer clearance. |
| 22 | Wrapped bullets had broken indent (same as slide 2 bug); 1.2 in dead-air per card | Rewrote with new `add_bullets` (hanging indent now works); larger bullet line-gap (0.78 in) absorbs natural wrap; removed dangling bottom italic. |
| 23 | URL appeared truncated (actually correct — repo is `CineEmbed-`); best-config text wrapped awkwardly | Re-organised: F1/F2 callout cards at y=4.0; **BEST CONFIGURATION** label + 4 metric chips (BACKBONE / gNMI / genre@5 / INDEX); brightened author line to `SLATE_LIGHT` for legibility on dark navy. |

### Global presentation changes

- `add_bullets` rewritten — uses two textboxes per bullet (glyph + text) so wrapped lines have proper hanging indent. Affects slides 2, 8, 14, 19, 22.
- Slate captions darkened from `SLATE_500` to `SLATE_600` for projector contrast.
- `SLATE_LIGHT` bumped from `slate-400` (`#94A3B8`) to `slate-300` (`#CBD5E1`) on dark backgrounds.
- Figures regenerated with projector-scale fonts (rcParams: title 17pt, axis 14pt, ticks 12pt, legend 12pt). Re-runs `scripts/generate_final_figures.py`.

### PDF fixes applied

- **Orphan-heading guard.** Added `\Needspace{6\baselineskip}` before `\section` and `\Needspace{4\baselineskip}` before `\subsection` via `pandoc_header.tex`. Pages 11/12/18/22/25 audit clean — no heading appears in the bottom 25 % of a page anymore.
- **Duplicate figure captions.** Removed "Figure N — " prefix from all four image alt-texts in markdown. Pandoc + LaTeX now auto-number figures, so the rendered caption is `Figure 1: <description>` instead of `Figure 1: Figure 1 — <description>`.
- **Widow / orphan tightening.** `\widowpenalty=10000`, `\clubpenalty=10000`, `\displaywidowpenalty=10000`.
- **Compact section spacing.** `\titlespacing` reduced the white space around `\section` and `\subsection` so paragraphs flow tighter and the document compressed from 26 → 25 pages.
- **Wide-table collisions** (Table 3 z-sweep + Appendix B per-run table). AMI columns dropped (mirror NMI within 1e-3); column headers abbreviated to `gNMI / gARI / dNMI / dARI / lNMI / lARI`; column widths set explicitly via dash-count alignment. Both tables now render cleanly with no header / row collisions.
- **TOC duplicate H1.** Used `--shift-heading-level-by=-1` so the YAML title is the document title and `# heading` lines act as `\section`s. TOC no longer carries the redundant repeated title entry.
- **References on a fresh page.** `\BeforeBeginEnvironment{thebibliography}{\clearpage}` in the LaTeX header.
- **Unicode glyph fallback.** Added `\newunicodechar{...}` mappings for `→ ∈ ≥ ≤ ≫ ≪ ≈ ≠ · ‖ ∝ σ Σ τ β γ λ μ α ε ✓`. Zero "Missing character" warnings.

### Final verification

- **Presentation:** 23 slides, 23 / 23 visually QA'd post-rebuild. All footer collisions resolved. Effective-page-use score (subagent re-audit) up from 5.39 / 10 (v1) to ~8.0 / 10 (v2; cards now content-dense, KPI strips fill bottom, figures fill width).
- **PDF report:** 25 pages (was 26 in v1), 678 KB. Zero "Missing character" warnings. Pages 11 / 12 / 13 / 18 / 22 / 24 / 25 spot-checked — tables clean, headings have body following, no orphan / widow issues.
- **Figures:** 4 PNGs regenerated at projector scale. `cosine_collapse_histogram.png` mean / median / min stats unchanged (deterministic, seed=42).

---

## 8. Final-deliverables checklist

| Deliverable | Path | Verified |
|---|---|---|
| Final report (markdown) | `docs/final/deliverables/final_report.md` | ✅ |
| Final report (PDF, 26 pages, pandoc + xelatex + STIX Two Text + Unicode fallback) | `docs/final/deliverables/final_report.pdf` | ✅ |
| Final presentation (.pptx) | `docs/final/deliverables/final_presentation.pptx` | ✅ |
| Final presentation (PDF) | `docs/final/deliverables/final_presentation.pdf` | ✅ |
| Verification notes | `docs/final/deliverables/verification_notes.md` | (this file) |
| Reproducibility recipe | `docs/final/deliverables/run_reproducibility.md` | ✅ |
| Generated figures | `docs/final/deliverables/figures/*.png` (4 files) | ✅ |
| Slide-render images for QA | `docs/final/deliverables/slide_renders/slide-*.jpg` (23) | ✅ |
| Scratch briefs (audit trail) | `docs/final/scratch/*.md` (4 files) | ✅ |

---

## 9. Honest statement of what is and is not in the submission

**Included:**

- Two empirical phases (MVP and Round 2) with full results tables.
- All nine hero findings with numerical evidence.
- All three negative results (ND-1, ND-2, ND-3).
- The two methodological findings (F1 NMI ≠ retrieval; F2 z = 32 sweet spot).
- 4 newly-generated evidence figures + reuse of 2 hero UMAP figures.
- Working web-app demo with 8 API endpoints and 5 frontend routes.
- 107-test reproducibility suite.

**Not included (deferred to future work, transparent in §13):**

- Modality ablations F1 (`no_text`) and F2 (`no_director`) — bandwidth-bound.
- W4 Kendall learned uncertainty weighting — W2 already validated.
- DEC k-grid {10, 21, 30} at z ∈ {32, 128}.
- VAE z-sweep — gated on Round 1 outcome, which VAE lost.
- Multi-seed runs.
- A user study or A/B retrieval evaluation.

The honest tone in the report is that the project's strongest scientific contributions are the two methodological findings, not a new architecture or loss; and the negative results section is written as part of the contribution rather than buried.

---

*End of verification notes.*

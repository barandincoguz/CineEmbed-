# CineEmbed — References Audit

**Date:** 2026-05-19
**Auditor:** Claude (audit pass for final report, due 2026-05-20)
**Source files:**
- `docs/report/references.bib` (7 entries)
- `docs/report/intermediate-progress-report.tex` (6 distinct `\cite{}` calls covering all 7 entries)
- `docs/report/intermediate-progress-report.bbl` (rendered bibliography — matches `.bib` exactly)

---

## 1. Citation Inventory (intermediate report)

Every `\cite{}` call found in `intermediate-progress-report.tex`, with the claim it supports:

| # | Bibkey | Line | Cited claim / context |
|---|--------|------|------------------------|
| 1 | `reimers2019sbert` | 287 | "Wikipedia director bios ... embedded with all-MiniLM-L6-v2" — supports use of Sentence-BERT family embeddings |
| 2 | `gorishniy2021tabular` | 308 | "seven independent `_BlockProjection` layers, one per modality" — supports modality-specific projection design for tabular DL |
| 3 | `xie2016dec` | 329 | "DEC fine-tuning ... soft assignments q_ij ... auxiliary target p_ij" — supports the DEC method itself |
| 4 | `guo2017idec` | 329 | Co-cited with DEC; supports the improved/local-structure variant referenced for the recon+KL combined loss |
| 5 | `paszke2019pytorch` | 338 | "Implementation in PyTorch" — software citation |
| 6 | `pedregosa2011sklearn` | 338 | "KMeans / NMI / ARI from scikit-learn" — software citation |
| 7 | `mcinnes2018umap` | 409 | "UMAP projection, 15K subsample, cosine metric" — supports UMAP as the visualization tool |

All 7 entries in `references.bib` are cited (no orphans). All 7 appear in the `.bbl` exactly as declared in `.bib`.

---

## 2. Per-Entry Verification

Format: `bibkey | claimed title | claimed authors | venue | year | claim supported? | status`

### 2.1 `xie2016dec`
- **Claimed title:** Unsupervised Deep Embedding for Clustering Analysis
- **Claimed authors:** Xie, Junyuan; Girshick, Ross; Farhadi, Ali
- **Venue:** ICML 2016 (pages 478–487)
- **Year:** 2016
- **Claim supported:** Yes — this paper is the canonical DEC paper, defines the soft-assignment q_ij and auxiliary target p_ij used in §3.3 of the report. Exact quantities cited in the report (q_ij Student-t kernel, p_ij = q_ij²/sum_i q_ij, KL(P||Q) loss) all match the paper.
- **Status:** VERIFIED. Standard canonical DEC reference. Title/authors/venue/year match the ICML 2016 publication exactly.

### 2.2 `guo2017idec`
- **Claimed title:** Improved Deep Embedded Clustering with Local Structure Preservation
- **Claimed authors:** Guo, Xifeng; Gao, Long; Liu, Xinwang; Yin, Jianping
- **Venue:** IJCAI 2017 (pages 1753–1759)
- **Year:** 2017
- **Claim supported:** Yes — IDEC is the canonical follow-up that adds reconstruction loss alongside the DEC KL term ("Total loss γ·KL(P||Q) + L_recon" in the report directly mirrors IDEC's joint objective).
- **Status:** VERIFIED. Authors, venue (IJCAI 2017), and page range (1753–1759) all match the published paper.

### 2.3 `reimers2019sbert`
- **Claimed title:** Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks
- **Claimed authors:** Reimers, Nils; Gurevych, Iryna
- **Venue:** EMNLP 2019 (technically EMNLP-IJCNLP 2019)
- **Year:** 2019
- **Claim supported:** Partially — the report uses `all-MiniLM-L6-v2`, which is a distilled MiniLM model distributed by the sentence-transformers library that the Reimers & Gurevych paper introduced. Citing the SBERT paper for the sentence-transformers framework is standard and correct, although strictly the `all-MiniLM-L6-v2` checkpoint derives from Wang et al.'s MiniLM. SBERT is the conventionally cited reference in this position.
- **Status:** VERIFIED. (Optional improvement: also cite Wang et al. MiniLM 2020 for the specific architecture distillation, but SBERT alone is acceptable academic practice.)

### 2.4 `mcinnes2018umap`
- **Claimed title:** UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction
- **Claimed authors:** McInnes, Leland; Healy, John; Melville, James
- **Venue:** arXiv preprint arXiv:1802.03426
- **Year:** 2018
- **Claim supported:** Yes — this is the canonical UMAP technical report; used here to credit the dimensionality-reduction tool.
- **Status:** VERIFIED. (Note: arXiv preprint citation is correct; UMAP was never formally published at a venue — the arXiv tech report is the canonical reference, alongside the JOSS software paper by the same authors. Optional polish: add the JOSS 2018 software paper for completeness.)

### 2.5 `pedregosa2011sklearn`
- **Claimed title:** Scikit-learn: Machine Learning in Python
- **Claimed authors:** Pedregosa et al. (16 authors)
- **Venue:** Journal of Machine Learning Research, vol. 12, pp. 2825–2830
- **Year:** 2011
- **Claim supported:** Yes — standard software citation for scikit-learn KMeans, NMI, ARI.
- **Status:** VERIFIED. Canonical JMLR 2011 sklearn citation. Author list, volume, and pages match exactly.

### 2.6 `paszke2019pytorch`
- **Claimed title:** PyTorch: An Imperative Style, High-Performance Deep Learning Library
- **Claimed authors:** Paszke, Adam; Gross, Sam; Massa, Francisco; Lerer, Adam; Bradbury, James; Chanan, Gregory; Killeen, Trevor; Lin, Zeming; Gimelshein, Natalia; Antiga, Luca; and others
- **Venue:** Advances in Neural Information Processing Systems 32 (NeurIPS 2019)
- **Year:** 2019
- **Claim supported:** Yes — standard software citation for the deep learning framework.
- **Status:** VERIFIED. Canonical NeurIPS 2019 PyTorch citation; authors and venue match exactly.

### 2.7 `gorishniy2021tabular`
- **Claimed title:** Revisiting Deep Learning Models for Tabular Data
- **Claimed authors:** Gorishniy, Yury; Rubachev, Ivan; Khrulkov, Valentin; Babenko, Artem
- **Venue:** Advances in Neural Information Processing Systems 34 (NeurIPS 2021)
- **Year:** 2021
- **Claim supported:** Borderline — the cited paper benchmarks MLP / ResNet / FT-Transformer on tabular data and does propose feature-tokenizer-style projections for heterogeneous columns. However, it is **not the strongest support** for "seven independent `_BlockProjection` layers, one per modality." The report's design is closer to **multi-modal block-projection architectures**, not specifically the Gorishniy et al. FT-Transformer.
- **Status:** VERIFIED (real paper, authors and venue match exactly), but the **relevance is weak**. Consider keeping it as a generic "deep learning on tabular data" citation and adding a stronger reference for multi-modal projection (e.g., a multi-modal fusion / mixture-of-modalities reference, or simply remove it if no stronger reference is added). The paper itself is real and well-known.

---

## 3. Summary Verdict

| Status | Count | Entries |
|--------|-------|---------|
| ✅ VERIFIED (well-known, exact match) | 6 | `xie2016dec`, `guo2017idec`, `reimers2019sbert`, `mcinnes2018umap`, `pedregosa2011sklearn`, `paszke2019pytorch` |
| ⚠️ SUSPICIOUS (real paper but weak relevance) | 1 | `gorishniy2021tabular` |
| ❌ FABRICATED-LIKELY | 0 | — |
| ❓ UNVERIFIED | 0 | — |

**Net assessment:** The current intermediate report's bibliography is clean. All 7 entries are real, well-known papers with correct author / venue / year metadata. There are no fabricated citations. The only flag is a mild relevance concern for `gorishniy2021tabular` — it is a real and reputable NeurIPS 2021 paper, but it does not strongly justify the *multi-modal* projection design as cited. Keep it (it justifies "deep learning on heterogeneous tabular features" generically) or replace with a stronger multi-modal citation.

**Drop recommendation:** **None mandatory.** Optionally consider dropping `gorishniy2021tabular` only if you find a more specific multi-modal-fusion / block-wise-projection reference to swap in. Otherwise keep it.

---

## 4. Coverage Gaps for the Final Report

The current 7-entry list is sufficient for the intermediate report but **thin for a final report**. The final report will (per the in-progress / planned sections) cover topics not yet cited:

- **VAE family** (planned for W13) → no current citation
- **β-VAE / disentanglement** (if discussed) → no current citation
- **KMeans++ initialization** (used in DEC and baselines) → no current citation
- **Recommendation-system background** (project framing as a "movie recommender") → no current citation
- **Contrastive learning** (mentioned in the contrastive notebook `notebooks/03_train_contrastive.ipynb`) → no current citation
- **Multi-task / inverse-variance weighting** (W2 + planned W4 Kendall uncertainty) → no current citation
- **NMI / ARI metrics** (used heavily; the report uses sklearn impls but no methodological citation) → no current citation
- **Two-Tower / content-based recommenders** (if reframing as a recommender) → no current citation

---

## 5. Proposed Final Reference List (clean, verified, 17 entries)

Designed to cover the topics in the prompt: recommendation systems, content-based filtering, autoencoders, deep clustering (DEC), contrastive learning (InfoNCE / SimCLR), VAE, UMAP, KMeans / spectral / HDBSCAN, multi-task weighting, multi-modal representation learning. All entries below are real, widely-cited papers with stable metadata.

### Deep clustering (core method)
1. **Xie, Girshick & Farhadi (2016)** — *Unsupervised Deep Embedding for Clustering Analysis*. ICML 2016, pp. 478–487. **[keep — already in bib as `xie2016dec`]**
2. **Guo, Gao, Liu & Yin (2017)** — *Improved Deep Embedded Clustering with Local Structure Preservation*. IJCAI 2017, pp. 1753–1759. **[keep — already in bib as `guo2017idec`]**

### Autoencoders / representation learning
3. **Hinton & Salakhutdinov (2006)** — *Reducing the Dimensionality of Data with Neural Networks*. Science 313 (5786), pp. 504–507. **[add — foundational AE citation]**

### Variational autoencoders (planned VAE family)
4. **Kingma & Welling (2014)** — *Auto-Encoding Variational Bayes*. ICLR 2014 (arXiv:1312.6114). **[add — canonical VAE]**
5. **Higgins et al. (2017)** — *β-VAE: Learning Basic Visual Concepts with a Constrained Variational Framework*. ICLR 2017. **[add — β-VAE / disentanglement; cite only if you discuss β]**

### Contrastive learning (mentioned in notebook 03)
6. **Chen, Kornblith, Norouzi & Hinton (2020)** — *A Simple Framework for Contrastive Learning of Visual Representations* (SimCLR). ICML 2020. **[add — canonical contrastive learning]**
7. **van den Oord, Li & Vinyals (2018)** — *Representation Learning with Contrastive Predictive Coding* (InfoNCE). arXiv:1807.03748. **[add — InfoNCE objective]**

### Clustering algorithms (baselines & DEC initialization)
8. **Arthur & Vassilvitskii (2007)** — *k-means++: The Advantages of Careful Seeding*. SODA 2007, pp. 1027–1035. **[add — KMeans++ init used in DEC and baselines]**
9. **Campello, Moulavi & Sander (2013)** — *Density-Based Clustering Based on Hierarchical Density Estimates* (HDBSCAN). PAKDD 2013, pp. 160–172. **[add only if HDBSCAN is reported as a baseline; otherwise drop]**

### Dimensionality reduction / visualization
10. **McInnes, Healy & Melville (2018)** — *UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction*. arXiv:1802.03426. **[keep — already in bib as `mcinnes2018umap`]**
11. **van der Maaten & Hinton (2008)** — *Visualizing Data using t-SNE*. Journal of Machine Learning Research 9 (Nov), pp. 2579–2605. **[add only if you contrast UMAP vs t-SNE; otherwise optional]**

### Evaluation metrics
12. **Strehl & Ghosh (2002)** — *Cluster Ensembles — A Knowledge Reuse Framework for Combining Multiple Partitions*. Journal of Machine Learning Research 3 (Dec), pp. 583–617. **[add — canonical NMI reference]**
13. **Hubert & Arabie (1985)** — *Comparing Partitions*. Journal of Classification 2 (1), pp. 193–218. **[add — canonical ARI reference]**

### Multi-task / loss weighting (W2 inverse-variance + planned W4)
14. **Kendall, Gal & Cipolla (2018)** — *Multi-Task Learning Using Uncertainty to Weigh Losses for Scene Geometry and Semantics*. CVPR 2018. **[add — directly supports W4 learned uncertainty and the broader inverse-variance weighting motivation in W2]**

### Sentence / text embeddings (for the `text` modality)
15. **Reimers & Gurevych (2019)** — *Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks*. EMNLP-IJCNLP 2019. **[keep — already in bib as `reimers2019sbert`]**

### Recommendation systems framing
16. **Covington, Adams & Sargin (2016)** — *Deep Neural Networks for YouTube Recommendations*. RecSys 2016, pp. 191–198. **[add — canonical two-tower / candidate-generation reference for recommender-system framing]**

### Software (keep both)
17. **Paszke et al. (2019)** — *PyTorch: An Imperative Style, High-Performance Deep Learning Library*. NeurIPS 2019. **[keep — already in bib as `paszke2019pytorch`]**
18. **Pedregosa et al. (2011)** — *Scikit-learn: Machine Learning in Python*. JMLR 12, pp. 2825–2830. **[keep — already in bib as `pedregosa2011sklearn`]**

### Optional / situational (cite only if discussed)
- **Bardes, Ponce & LeCun (2022)** — *VICReg: Variance-Invariance-Covariance Regularization for Self-Supervised Learning*. ICLR 2022. — only if you contrast variance-based contrastive losses.
- **Grill et al. (2020)** — *Bootstrap Your Own Latent (BYOL)*. NeurIPS 2020. — only if you reference negative-free contrastive methods.
- **Zbontar et al. (2021)** — *Barlow Twins: Self-Supervised Learning via Redundancy Reduction*. ICML 2021. — only if cited for variance-redundancy framing.
- **Ng, Jordan & Weiss (2002)** — *On Spectral Clustering: Analysis and an Algorithm*. NeurIPS 2002, pp. 849–856. — only if spectral clustering is a reported baseline.
- **Arik & Pfister (2021)** — *TabNet: Attentive Interpretable Tabular Learning*. AAAI 2021. — only if you discuss interpretable tabular DL beyond the Gorishniy citation.

### Drop / consider replacing
- **Gorishniy et al. (2021)** `gorishniy2021tabular` — keep only if you want a generic "deep learning for tabular data" citation. The relevance to *multi-modal* projection blocks is weak; a stronger anchor for the multi-modal design would be Covington et al. (2016) for the recommender-system framing OR Kendall et al. (2018) for the multi-task / per-block weighting framing. If trimming to ≤15 entries, this is the first to cut.

---

## 6. Final Counts (proposed)

- **Core (mandatory):** 14 entries (items 1–4, 6, 7, 8, 10, 12, 13, 14, 15, 16, 17, 18 — minus item 5 if you don't discuss β-VAE, minus item 11 if you don't discuss t-SNE, minus item 9 if you don't run HDBSCAN).
- **With situational additions:** up to ~18 entries.
- **Sweet spot for a SENG 474 final report:** **15 entries** is a defensible target. Keep the 6 verified entries from the intermediate report, drop `gorishniy2021tabular` only if you have a stronger swap, and add the 9 entries marked **[add]** that map directly to topics already in the report or the planned-work table (VAE, contrastive, KMeans++, NMI/ARI methodology, multi-task weighting, recommender framing).

---

**End of audit.**

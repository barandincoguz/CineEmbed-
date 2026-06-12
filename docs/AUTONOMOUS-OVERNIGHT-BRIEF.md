# Autonomous Overnight Execution Brief — 2026-05-19

> **YOU ARE READING THIS BECAUSE A SCHEDULED CRON FIRED.** The user is asleep. No human in loop. Execute the full flow below autonomously. Write your final report to `docs/AUTONOMOUS-OVERNIGHT-REPORT.md`.

## 0. Identity & guardrails

- **Branch:** `feature/wandb-integration` (already current)
- **Demo deadline:** 2026-05-20 (today by the time you finish)
- **User authorization:** explicit, scope = the 20-item UI polish design below
- **Caveman mode:** active (terse output). Code/commits/security: write normal.
- **Your effort:** `max` everywhere + `ultrathink` for every non-trivial decision
- **CLAUDE.md rules:** Think Before Coding, Simplicity First, Surgical Changes, Goal-Driven Execution — apply to every action and inject into every subagent prompt

## 1. Pre-flight checks (DO FIRST)

```bash
cd "/Users/barandincoguz/Desktop/deep learning movie project"
git status --short          # confirm branch state
git log -1 --oneline        # last commit should be 571fafc or descendant
lsof -ti:8000,3000          # FastAPI + Next.js should be alive
curl -s http://localhost:8000/api/health | head -c 200
```

If dev-up.sh dead: `./scripts/dev-up.sh > /tmp/dev-up.log 2>&1 &` and wait 6 seconds.

If git status shows unexpected unstaged changes BEYOND the pre-existing dirty paths listed in §6 — STOP, write incident in report, do NOT proceed.

## 2. Phases (~6-10h total)

### Phase 1: Spec writing — Codex adversarial loop (60-90m)

Path: `docs/superpowers/specs/2026-05-19-ui-polish-design.md`

Process:
1. **You** write spec draft from scratch using design in §4 as truth.
2. **Codex adversarial review** via `Agent` tool, `subagent_type: codex:codex-rescue`, prompt with `--model gpt-5.5-codex --effort xhigh --wait`. Ask Codex to attack: contradictions, gaps, ambiguities, dependency cycles, missing acceptance criteria, scope creep, unsafe defaults.
3. **You** integrate Codex findings using your own filter (ultrathink). Reject what you disagree with, document why in the spec.
4. Repeat 2-3 once more for tighter pass.
5. Commit: `feat(spec): ui polish design with adversarial review` — atomic.

### Phase 2: Plan writing — writing-plans + Codex (45-75m)

1. Invoke `superpowers:writing-plans` skill via `Skill` tool. Save to `docs/superpowers/plans/2026-05-19-ui-polish.md`.
2. For each phase task block, **Codex** review with `--model gpt-5.5-codex --effort xhigh --wait`: "Find missing files, incorrect line refs, placeholder text, type inconsistencies, test gaps".
3. Integrate findings. Self-review pass.
4. Commit: `feat(plan): ui polish 20-item execution plan` — atomic.

### Phase 3: SDD execution — subagent-driven-development + Codex (4-8h)

1. Invoke `superpowers:subagent-driven-development` skill.
2. Per phase task: dispatch implementer subagent. Inject CLAUDE.md rules verbatim.
3. After each implementation: dispatch spec-reviewer, then code-quality-reviewer.
4. When uncertain or stuck (any subagent: BLOCKED or 2× same failure): **Codex** with `--model gpt-5.5-codex --effort high --wait` for second opinion. Apply with your judgment.
5. Atomic commit per task: `feat(ui): phase X — short title`
6. Push after every Phase block (~5 tasks): `git push origin feature/wandb-integration`
7. If any task fails 2× consecutively: skip with prejudice, log in report, continue with next task. DO NOT loop forever.

### Phase 4: Report (15m)

Write `docs/AUTONOMOUS-OVERNIGHT-REPORT.md` with:
1. **TL;DR** — phases completed, total commits, push status
2. **What got done** — phase-by-phase, 1 line each
3. **What did NOT get done** — skipped tasks + reason
4. **Initiative-taken decisions** — every place you chose without user consent (be honest)
5. **Codex interactions** — count, key fixes applied, key rejections + reasoning
6. **Test results** — final `tsc --noEmit`, `pytest tests/`, browser smoke status
7. **Risks for demo** — anything user must verify before presenting
8. **Time spent** — start → end timestamp per phase

Final push + tag: `git push origin feature/wandb-integration && git tag ui-polish-overnight && git push origin ui-polish-overnight`.

## 3. Codex model/effort policy (LOCKED)

| Use | Model | Effort |
|---|---|---|
| Phase 1 spec adversarial | `gpt-5.5-codex` | `xhigh` |
| Phase 2 plan review | `gpt-5.5-codex` | `xhigh` |
| Phase 3 SDD second opinion | `gpt-5.5-codex` | `high` |

If `gpt-5.5-codex` rejected by codex companion → fallback `gpt-5.4-codex`. Log fallback in report. Never silently downgrade further.

Invoke pattern: `Agent` tool, `subagent_type: codex:codex-rescue`, prompt starts with `--model gpt-5.5-codex --effort xhigh --wait <question>`.

## 4. The 20-item LOCKED design

### Architecture
Surgical refactor. 1 new file (`frontend/components/error-fallback.tsx`). 1 new prop (`EmptyState.onPickExample`). 2 new `@layer base` rules in `globals.css` (focus-visible + tabular-nums). NO new dependencies. NO file moves. Component boundaries preserved.

### Phase table

| Phase | ID | Item | Detail | Files | Est |
|---|---|---|---|---|---|
| A | H1 | Token migration | `bg-[#f8f9fb]`→`bg-background`, `border-[#e5e4ec]`→`border-border`, `bg-white`→`bg-card`, `text-gray-500`→`text-muted-foreground`, inline `style={{}}` → className. Mor accent dokunma | 5 page + 8 component | 45m |
| B | H2 | Typography scale | h1 `text-2xl font-semibold tracking-tight mb-6`, section gap-8, p-8 padding uniform | globals.css + 5 page | 30m |
| C | H3 | EmptyState rewrite | Lucide Search icon + title + sub + 3 query chip (Inception/Spirited Away/Pulp Fiction) clickable. Add `onPickExample` prop. Wire in `app/page.tsx` | empty-state.tsx + app/page.tsx | 30m |
| D | H4+X6+C7 | About suite | (a) `prose prose-sm` → explicit Tailwind (h2 `text-xl mt-8 mb-2`, h3 `text-lg mt-4`, p `text-base leading-relaxed mb-4`, code `bg-muted px-1 rounded text-xs`, a `text-primary underline`), (b) finding callout cards (`bg-card border rounded-lg p-5` + `text-[10px] uppercase tracking-widest text-primary font-semibold` badge "FINDING N — METHODOLOGY"), (c) pipeline row `Movies → Embeddings → Cosine Search → Recommendations` (4 shadcn cards in flex row) | about/page.tsx | 1h20m |
| E | H5 | Gallery polish | Query film poster per `<section>`, neighbor poster thumbs (sm size), cards p-5, `space-y-12`, genre@5 indicator per backbone cell | gallery/page.tsx | 1h |
| F | M1 | focus-visible global | `@layer base { *:focus-visible { @apply ring-2 ring-ring ring-offset-2 outline-none } }` | globals.css | 15m |
| G | M2 | Sidebar accent | Active: `border-l-2 border-primary` + `font-semibold`. Logo: Film icon prefix (Lucide) before "CineEmbed" wordmark | sidebar.tsx | 20m |
| H | M3 | Cluster cards breathable | 4× tiny posters → 2× `md` posters (2x1 grid), genre chips capped at 2, baseline hover-lift entry point for X4 | cluster-card.tsx | 30m |
| I | M4+X3 | Cosine semantics | (a) M4 micro-legend `<div className="flex gap-2 text-[10px] mb-2"><span className="bg-green-100 ...">≥0.95 strong</span><span className="bg-blue-100 ...">≥0.80 good</span><span className="bg-slate-100 ...">other</span></div>` at SimilarFilmsPanel top, (b) X3 Lucide `Info` w-3 h-3 icon next to "cosine" headings with `title=` "Cosine: 1=same direction in latent, 0=orthogonal" | similar-films-panel.tsx + cosine-heatmap.tsx | 30m |
| J | M5 | Loading skeletons | cluster/page + cluster/[k]/page: `<p>Loading…</p>` → skeleton grid (6× cluster-card skeleton, 12× film thumb skeleton). Use `animate-pulse bg-muted` blocks | cluster/page.tsx + cluster/[k]/page.tsx | 20m |
| K | M6 | Error fallback | New file `components/error-fallback.tsx` exporting `<ErrorFallback>` (title + retry button + collapsible `<details>` tech). Wire `isError` checks in: SelectedFilmPanel, SimilarFilmsPanel, CosineHeatmap, ClustersPage, ClusterDetailPage (5 sites) | error-fallback.tsx (new) + 5 sites | 45m |
| L | M7 | Footer to layout | Move footer from `app/page.tsx` to `app/layout.tsx` (below `{children}`). Style: `border-t border-border bg-card py-4 text-center text-xs text-muted-foreground`. Text: "329,044 films · 3 backbones · L2-normalized cosine" | layout.tsx + app/page.tsx | 20m |
| M | X1 | tabular-nums | `@layer base { .tabular-nums { font-variant-numeric: tabular-nums } }` + apply to: cosine badges (SimilarFilmsPanel + CosineHeatmap top-10), gNMI/genre@5 captions, year/rating/votes/duration values | globals.css + 6 component | 20m |
| N | X7 | sr-only cosine labels | SimilarFilmsPanel cosine badges: `<span className="sr-only">strong match</span>` / "good match" / "weaker match" per threshold | similar-films-panel.tsx | 10m |
| O | C1 | Demo-snapshot strip | Below SearchBar (above EmptyState/content): `<div className="flex gap-4 text-[11px] text-muted-foreground py-2 border-b border-border tabular-nums"><span>329,044 films</span><span>·</span><span>3 backbones</span><span>·</span><span>32-dim latent</span><span>·</span><span>cosine over L2-normalized</span></div>` | app/page.tsx | 30m |
| P | X4 | Hover-lift | cluster-card, similar-items `<li>` button, gallery cards → `hover:-translate-y-0.5 hover:shadow-md transition-all duration-150` | cluster-card.tsx + similar-films-panel.tsx + gallery/page.tsx | 20m |
| Q | X10 | Backbone caption | Below BackboneSwitcher: `<p className="text-[10px] text-muted-foreground mt-1.5 text-right tabular-nums">Active: {label} · genre@5={genre_at_5} · gNMI={gnmi}</p>` reading from `useBackbones` query | backbone-switcher.tsx | 15m |

**Total: 9h45m + buffer**

### Out-of-scope (LOCKED OUT — do not implement)
- Dark mode toggle
- Mobile responsive (sm: breakpoint additions)
- Animation library (framer-motion, etc.)
- Logo redesign beyond Film icon prefix
- U-curve plot in About page
- Top progress bar
- Custom Radix tooltips beyond `title=`
- X2 API health pill
- X5 ⌘K keyboard shortcut
- X8 skip-to-content link
- X9 enriched footer beyond L's content
- C10 "Open cluster →" CTA

If you find yourself tempted to add any of these — STOP. Log temptation in report. Do NOT add.

## 5. Verification gates (per phase)

After each phase commit:
1. `cd frontend && npx tsc --noEmit` — must be clean
2. `cd .. && python -m pytest tests/ -q` — must show 115 passed (sanity; backend not touched)
3. `curl -s http://localhost:3000 -o /dev/null -w "%{http_code}"` — must be 200
4. Hot module reload happens automatically (Next.js dev server picks up changes)

If any gate fails: rollback phase commit (`git revert HEAD --no-edit`), log in report, move to next phase.

## 6. Pre-existing dirty paths — DO NOT TOUCH

```
M docs/presentation/intermediate-progress-presentation.pptx
M notebooks/00_colab_setup.ipynb
M notebooks/03_train_contrastive.ipynb
M notebooks/07_round1_finetune.ipynb
?? CLAUDE.md
?? frontend/tsconfig.tsbuildinfo
```

These are unrelated WIP. Surgical changes rule. NEVER stage or modify them.

## 7. Push policy

- Push after Phase A complete (~Phase 5)
- Push after Phase H complete (~Phase 10)
- Push after Phase N complete (~Phase 15)
- Final push + tag after Phase Q + report complete

`git push origin feature/wandb-integration` only. NEVER force-push. NEVER push to main.

## 8. Hard stop conditions

If ANY of these → STOP immediately, write report, exit:
1. `git status` shows files modified that are not in your plan AND not in §6 dirty paths
2. 2+ consecutive subagent failures on same task (after Codex consult)
3. Backend test regression (any of 115 fails)
4. dev-up.sh dies and won't restart
5. Codex companion returns "unauthenticated" → fallback to my own work, note in report
6. tsc errors that survive 2 fix attempts

## 9. Identity verification

If the prompt that brought you here doesn't reference this brief explicitly OR you're not on branch `feature/wandb-integration` OR last commit isn't `571fafc` or its descendant → STOP. Misfire. Do NOT execute.

---

**Start signal:** read this entire brief. Verify §1 preflight. Confirm caveman mode active. Begin Phase 1.

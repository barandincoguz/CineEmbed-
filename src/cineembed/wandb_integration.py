"""W&B integration helpers — keeps wandb concerns out of core modules.

Design:
    - `wandb_run(...)` is a context manager. Pass to train_model as `wandb_run=run`.
    - If wandb is uninstalled OR `WANDB_MODE=disabled`, it yields None.
    - All log_* helpers tolerate `run is None` and become no-ops.
    - Eval helpers in eval.py stay pure: callers compose results, then call
      `log_eval(run, results)` once, when ready to push.

Why this shape (not invasive instrumentation in eval.py):
    - eval.py has 7 separate functions (cluster_assignments_*, evaluate_run,
      multilabel_macro_nmi, linear_probe, umap_plot). Sprinkling wandb.log
      inside each one would couple them to a network side-effect.
    - Notebooks compose these freely; one final `log_eval(...)` call from the
      notebook keeps eval.py pure and testable.

Typical use (from a notebook):
    from cineembed.wandb_integration import wandb_run, log_epoch, log_eval, log_image
    from cineembed.train import train_model

    with wandb_run(
        config={'model':'AE','z_dim':64,'lr':1e-3},
        run_name='ae_z64_run5',
        tags=['ae-family','sweep-may10'],
    ) as run:
        history = train_model(..., wandb_run=run)        # per-epoch logged
        eval_metrics = evaluate_run(cluster_ids, labels)  # pure, no wandb
        log_eval(run, eval_metrics)                       # one push
        umap_plot(z, labels, title='AE z=64', savepath='figures/ae_umap.png')
        log_image(run, 'figures/ae_umap.png', key='umap_genre')
"""
from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

DEFAULT_PROJECT = "cineembed"


_VALID_MODES: tuple[str, ...] = ("online", "offline", "disabled", "shared")


def _wandb_available() -> bool:
    """True if wandb is importable in the current env."""
    try:
        import wandb as _w  # noqa: F401
        return True
    except ImportError:
        return False


@contextmanager
def wandb_run(
    config: dict,
    *,
    run_name: str | None = None,
    project: str = DEFAULT_PROJECT,
    entity: str | None = None,
    tags: list[str] | None = None,
    group: str | None = None,
    notes: str | None = None,
    mode: str | None = None,
) -> Iterator[Any | None]:
    """Initialize a W&B run as a context manager. Yields the run object, or None.

    Args:
        config: hyperparameters / metadata to log at run start.
        run_name: human-readable run name. None → auto-generated.
        project: W&B project (default 'cineembed').
        entity: team/user (None → user's default from netrc).
        tags: list of tags for filtering on the dashboard.
        group: group runs together (e.g. 'ae-family', 'dec-family').
        notes: free-text description shown on the run page.
        mode: 'online' (default), 'offline' (sync later), 'disabled' (no-op).
              If None, reads WANDB_MODE env var; falls back to 'online'.

    Yields:
        The wandb.Run object, or None if wandb is unavailable / disabled.

    The run is automatically finished on context exit (even on exception).
    """
    if not _wandb_available():
        yield None
        return

    import wandb

    if mode is None:
        mode = os.getenv("WANDB_MODE", "online")
    if mode not in _VALID_MODES:
        raise ValueError(
            f"mode must be one of {_VALID_MODES}, got {mode!r}"
        )
    if mode == "disabled":
        yield None
        return

    run = wandb.init(
        project=project,
        entity=entity,
        config=config,
        name=run_name,
        tags=tags or [],
        group=group,
        notes=notes,
        mode=mode,  # type: ignore[arg-type]  # validated above
        reinit="finish_previous",
    )
    try:
        yield run
    finally:
        wandb.finish()


def log_epoch(
    run: Any | None,
    *,
    epoch: int,
    train_loss: float,
    val_loss: float,
    lr: float | None = None,
    extra: dict[str, float] | None = None,
) -> None:
    """Per-epoch metrics. Safe no-op if run is None."""
    if run is None:
        return
    payload: dict[str, Any] = {
        "epoch": epoch,
        "train_loss": float(train_loss),
        "val_loss": float(val_loss),
    }
    if lr is not None:
        payload["lr"] = float(lr)
    if extra:
        payload.update({k: float(v) for k, v in extra.items()})
    run.log(payload)


def log_eval(
    run: Any | None,
    eval_dict: dict[str, float],
    *,
    prefix: str = "",
    add_geo_nmi: bool = True,
) -> None:
    """Final eval metric push. Auto-computes geo_nmi when 3 NMI keys present.

    `eval_dict` keys are passed through with optional prefix. Recognized NMI
    keys (case-sensitive): 'genre_nmi', 'lang_nmi', 'decade_nmi'.

    geo_nmi = (genre_nmi · lang_nmi · decade_nmi)^(1/3)
    Composite metric — drops to 0 if any axis is 0, encouraging multi-axis
    optimization rather than over-fitting one axis.
    """
    if run is None:
        return
    payload = {f"{prefix}{k}": float(v) for k, v in eval_dict.items()
               if isinstance(v, (int, float))}
    if add_geo_nmi:
        g = eval_dict.get("genre_nmi")
        l = eval_dict.get("lang_nmi")
        d = eval_dict.get("decade_nmi")
        if all(isinstance(x, (int, float)) for x in (g, l, d)):
            product = max(g * l * d, 0.0)  # type: ignore[operator]
            payload[f"{prefix}geo_nmi"] = product ** (1 / 3) if product > 0 else 0.0
    run.log(payload)


def log_image(run: Any | None, fig_path: str | Path, *, key: str = "umap") -> None:
    """Push a saved figure (PNG/JPG) as a W&B Image. No-op if run is None."""
    if run is None:
        return
    if not Path(fig_path).is_file():
        raise FileNotFoundError(f"Figure not found: {fig_path}")
    import wandb
    run.log({key: wandb.Image(str(fig_path))})


def log_artifact(
    run: Any | None,
    path: str | Path,
    *,
    name: str,
    type: str = "model",
    description: str | None = None,
) -> None:
    """Version a file (checkpoint, results.json) as a W&B artifact.

    Args:
        path: local file to upload.
        name: artifact name (will be visible on the dashboard).
        type: 'model', 'dataset', 'eval-output', etc.
        description: free-text description.
    """
    if run is None:
        return
    if not Path(path).is_file():
        raise FileNotFoundError(f"Artifact source not found: {path}")
    import wandb
    artifact = wandb.Artifact(name=name, type=type, description=description)
    artifact.add_file(str(path))
    run.log_artifact(artifact)


def log_table(
    run: Any | None,
    rows: list[list[Any]],
    *,
    columns: list[str],
    key: str = "table",
) -> None:
    """Push a tabular result (e.g. cluster assignments) as a W&B Table."""
    if run is None:
        return
    import wandb
    table = wandb.Table(columns=columns, data=rows)
    run.log({key: table})

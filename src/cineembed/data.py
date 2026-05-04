"""Data loading and label extraction for the cineembed modeling phase."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader, Dataset


# Mapping from block name to identifying prefixes in feature_names (per spec §3.1).
BLOCK_PREFIX_RULES = {
    'numerical': ('log_popularity', 'log_vote_count', 'runtime_norm',
                  'vote_average_norm', 'has_vote', 'has_engagement'),
    'genre':     ('genre_', 'has_genre'),
    'language':  ('lang_',),
    'decade':    ('decade_norm', 'has_release_date'),
    'awards':    ('prior_log_',),
    'text':      ('text_',),
    'director':  ('dir_bio_pca_', 'has_director_bio', 'dir_lang_',
                  'dir_country_', 'has_director_lang'),
}

BLOCK_ORDER = ['numerical', 'genre', 'language', 'decade', 'awards', 'text', 'director']


def _classify_feature(name: str) -> str:
    """Return the block name a feature column belongs to (deterministic priority).

    'director' is checked before 'language' so that dir_lang_* columns are not
    mis-classified into the language block.
    """
    for block in ['numerical', 'genre', 'director', 'language', 'decade', 'awards', 'text']:
        for pfx in BLOCK_PREFIX_RULES[block]:
            if name == pfx or name.startswith(pfx):
                return block
    raise ValueError(f"Cannot classify feature {name!r}")


def get_block_indices(feature_names: list[str]) -> dict[str, slice]:
    """Derive per-block column slices by scanning feature_names left-to-right.

    Production feature_matrix has block-contiguous columns. Each block's slice
    is identified by classifying every column and grouping adjacent same-class runs.
    """
    classifications = [_classify_feature(n) for n in feature_names]
    out: dict[str, slice] = {}
    i = 0
    while i < len(classifications):
        block = classifications[i]
        if block in out:
            raise ValueError(f"Block {block!r} appears non-contiguously near col {i}")
        j = i
        while j < len(classifications) and classifications[j] == block:
            j += 1
        out[block] = slice(i, j)
        i = j
    missing = set(BLOCK_ORDER) - set(out.keys())
    if missing:
        raise ValueError(f"Missing blocks: {missing}")
    return out


def load_feature_matrix(path: str | Path) -> tuple[torch.Tensor, list[str]]:
    """Load (X, feature_names) from the EDA artifact.

    X is converted to torch.float32. feature_names is returned as a Python list.
    """
    archive = np.load(Path(path), allow_pickle=True)
    X_np = archive['X'].astype(np.float32)
    names = list(archive['feature_names'])
    return torch.from_numpy(X_np), names


def _bin_decade(value):
    try:
        v = int(value)
    except (ValueError, TypeError):
        return 0
    return v if v > 0 else 0


def _column_or_default(df: pd.DataFrame, col: str, default_value) -> pd.Series:
    """Return df[col] if present, else a Series of `default_value` matching df length.

    Direct column access is preferred over df.get(...) because pandas type stubs
    flag DataFrame.get's return type as Optional, even though pandas itself never
    returns None when a default is provided. Cast to Series satisfies Pyright,
    which can't narrow `df[col]`'s return type away from DataFrame.
    """
    if col in df.columns:
        result = df[col]
        # Defensive: in single-column edge cases df[col] could return DataFrame.
        if isinstance(result, pd.DataFrame):
            result = result.iloc[:, 0]
        return result
    return pd.Series([default_value] * len(df))


def get_labels(csv_path: str | Path, top_lang_n: int = 10) -> dict[str, np.ndarray]:
    """Derive three orthogonal label vectors from movies_eda_final.csv (spec §3.2)."""
    df = pd.read_csv(csv_path, low_memory=False)

    # primary_genre = first piece of 'genres' before '|'; empty → 'Unknown'
    genres_first = _column_or_default(df, 'genres', '').fillna('').astype(str)
    primary_genre = genres_first.apply(lambda s: s.split('|')[0] if s else 'Unknown')
    primary_genre = primary_genre.replace('', 'Unknown').to_numpy()

    decade_bin = _column_or_default(df, 'decade', 0).apply(_bin_decade).to_numpy()

    lang = _column_or_default(df, 'original_language', '').fillna('other').astype(str)
    top = lang.value_counts().head(top_lang_n).index
    lang_top10 = lang.where(lang.isin(top), 'other').to_numpy()

    return {
        'primary_genre': primary_genre,
        'decade_bin':    decade_bin,
        'lang_top10':    lang_top10,
    }


def train_val_split(n: int, val_frac: float = 0.1, seed: int = 42) -> tuple[np.ndarray, np.ndarray]:
    """Random index split — deterministic given (n, val_frac, seed)."""
    rng = np.random.default_rng(seed)
    perm = rng.permutation(n)
    n_val = max(1, int(round(n * val_frac)))
    val_idx = perm[:n_val]
    train_idx = perm[n_val:]
    return train_idx, val_idx


class _BlocksDataset(Dataset):
    """Memory-efficient view of (X, has_bio) optionally restricted to indices.

    IMPORTANT: never copies X — both train and val datasets share the same underlying
    tensor and only differ in their `indices` array. With X at (329044, 564), copying
    would balloon Colab RAM to several GB unnecessarily.
    """
    def __init__(
        self,
        X: torch.Tensor,
        has_bio: torch.Tensor,
        indices: np.ndarray | None = None,
    ):
        self.X = X                 # NEVER copies
        self.has_bio = has_bio
        self.indices = None if indices is None else np.asarray(indices, dtype=np.int64)

    def __len__(self):
        return self.X.shape[0] if self.indices is None else len(self.indices)

    def __getitem__(self, i):
        real_i = int(self.indices[i]) if self.indices is not None else int(i)
        return {'X': self.X[real_i], 'has_bio': self.has_bio[real_i]}


def _split_into_blocks(X_batch: torch.Tensor, block_slices: dict[str, slice]) -> dict[str, torch.Tensor]:
    return {b: X_batch[:, slc] for b, slc in block_slices.items()}


def _collate(batch_list, block_slices):
    X = torch.stack([b['X'] for b in batch_list], dim=0)
    has_bio = torch.stack([b['has_bio'] for b in batch_list], dim=0)
    return {'blocks': _split_into_blocks(X, block_slices), 'has_bio': has_bio}


def make_dataloader(
    X: torch.Tensor,
    has_bio: torch.Tensor,
    batch_size: int,
    *,
    shuffle: bool = True,
    indices: np.ndarray | None = None,
    block_slices: dict[str, slice] | None = None,
    seed: int | None = 42,
    num_workers: int = 0,
) -> DataLoader:
    """Build a DataLoader yielding {'blocks': dict, 'has_bio': tensor} batches."""
    if block_slices is None:
        # Caller did not provide block_slices — assume production order via heuristic.
        # Production callers should pass explicit block_slices from get_block_indices().
        # Default fallback uses the canonical block dim layout.
        canonical_dims = [6, 22, 31, 2, 6, 384, 113]
        out, start = {}, 0
        for b, d in zip(BLOCK_ORDER, canonical_dims):
            out[b] = slice(start, start + d)
            start += d
        block_slices = out

    dataset = _BlocksDataset(X, has_bio, indices=indices)
    g = None
    if seed is not None:
        g = torch.Generator()
        g.manual_seed(seed)
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        generator=g,
        collate_fn=lambda batch: _collate(batch, block_slices),
    )

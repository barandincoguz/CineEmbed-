import numpy as np
import pandas as pd
import torch

from cineembed import data


def test_get_block_indices_matches_expected_dims(synthetic_feature_names):
    indices = data.get_block_indices(synthetic_feature_names)
    expected = {'numerical': 6, 'genre': 22, 'language': 31, 'decade': 2,
                'awards': 6, 'text': 384, 'director': 113}
    for block, want_dim in expected.items():
        slc = indices[block]
        assert slc.stop - slc.start == want_dim, f"{block}: got {slc.stop-slc.start}, want {want_dim}"
    assert sum(slc.stop - slc.start for slc in indices.values()) == 564


def test_load_feature_matrix(tmp_path, synthetic_feature_matrix, synthetic_feature_names):
    path = tmp_path / "feature_matrix.npz"
    np.savez(path, X=synthetic_feature_matrix, feature_names=np.array(synthetic_feature_names, dtype=object))

    X, names = data.load_feature_matrix(path)
    assert isinstance(X, torch.Tensor)
    assert X.shape == synthetic_feature_matrix.shape
    assert X.dtype == torch.float32
    assert list(names) == synthetic_feature_names


def test_get_labels_from_csv(tmp_path):
    df = pd.DataFrame({
        'genres':            ['Drama|Crime', 'Action', '', 'Comedy|Romance|Drama'],
        'decade':            [1990, 2000, 0, 2010],
        'original_language': ['en', 'fr', 'en', 'es'],
    })
    csv_path = tmp_path / "movies_eda_final.csv"
    df.to_csv(csv_path, index=False)

    labels = data.get_labels(csv_path)
    assert labels['primary_genre'].tolist() == ['Drama', 'Action', 'Unknown', 'Comedy']
    assert labels['decade_bin'].tolist() == [1990, 2000, 0, 2010]
    assert set(np.unique(labels['lang_top10'])).issubset({'en', 'fr', 'es', 'other'})


def test_train_val_split_deterministic():
    n = 100
    train_idx, val_idx = data.train_val_split(n, val_frac=0.1, seed=42)
    assert len(train_idx) == 90
    assert len(val_idx) == 10
    assert set(train_idx).isdisjoint(set(val_idx))
    # determinism
    train_idx2, val_idx2 = data.train_val_split(n, val_frac=0.1, seed=42)
    np.testing.assert_array_equal(train_idx, train_idx2)
    np.testing.assert_array_equal(val_idx, val_idx2)


def test_make_dataloader_yields_blocks_and_has_bio(synthetic_feature_matrix, block_slices):
    X = torch.from_numpy(synthetic_feature_matrix)
    has_bio = X[:, block_slices['director'].start + 64]
    loader = data.make_dataloader(X, has_bio, batch_size=32, shuffle=False)
    batch = next(iter(loader))
    assert 'blocks' in batch and 'has_bio' in batch
    assert batch['blocks']['numerical'].shape == (32, 6)
    assert batch['blocks']['text'].shape == (32, 384)
    assert batch['has_bio'].shape == (32,)

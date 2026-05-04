import numpy as np

from cineembed import eval as cev


def test_cluster_assignments_kmeans_returns_int_array():
    z = np.random.randn(200, 32).astype(np.float32)
    c = cev.cluster_assignments_kmeans(z, k=10, seed=42)
    assert c.shape == (200,)
    assert c.dtype.kind == 'i'
    assert set(np.unique(c)).issubset(set(range(10)))


def test_evaluate_run_three_axes(synthetic_labels):
    n = 200
    np.random.seed(0)
    cluster_ids = np.random.randint(0, 21, size=n)
    metrics = cev.evaluate_run(cluster_ids, synthetic_labels)
    for axis in ['genre', 'decade', 'lang']:
        assert f'{axis}_nmi' in metrics
        assert f'{axis}_ari' in metrics
        assert 0.0 <= metrics[f'{axis}_nmi'] <= 1.0
        assert -1.0 <= metrics[f'{axis}_ari'] <= 1.0


def test_linear_probe_returns_accuracy():
    z = np.random.randn(200, 32).astype(np.float32)
    labels = np.random.randint(0, 5, size=200)
    train_idx = np.arange(160)
    val_idx = np.arange(160, 200)
    result = cev.linear_probe(z, labels, train_idx=train_idx, val_idx=val_idx,
                               n_classes=5, n_epochs=10, lr=1e-2, seed=42)
    assert 'val_accuracy' in result
    assert 0.0 <= result['val_accuracy'] <= 1.0


def test_umap_plot_creates_file(tmp_path):
    z = np.random.randn(200, 32).astype(np.float32)
    labels = np.random.choice(['A', 'B', 'C'], size=200)
    out = tmp_path / "test_umap.png"
    cev.umap_plot(z, labels, title='test', savepath=out, seed=42)
    assert out.exists()
    assert out.stat().st_size > 1000  # non-trivial file

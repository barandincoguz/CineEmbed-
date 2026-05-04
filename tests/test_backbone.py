import torch

from cineembed import backbone


PROJ_DIMS = {
    'numerical': 16, 'genre': 16, 'language': 16, 'decade': 4,
    'awards': 16, 'text': 64, 'director': 32,
}
BLOCK_DIMS = {
    'numerical': 6, 'genre': 22, 'language': 31, 'decade': 2,
    'awards': 6, 'text': 384, 'director': 113,
}


def test_backbone_output_shape(synthetic_blocks_dict):
    model = backbone.MultiModalBackbone(
        block_dims=BLOCK_DIMS, proj_dims=PROJ_DIMS, hidden_dim=128, latent_dim=64,
    )
    z = model(synthetic_blocks_dict)
    assert z.shape == (200, 64)


def test_backbone_deterministic_with_seed(synthetic_blocks_dict):
    torch.manual_seed(42)
    m1 = backbone.MultiModalBackbone(
        block_dims=BLOCK_DIMS, proj_dims=PROJ_DIMS, hidden_dim=128, latent_dim=64,
    )
    z1 = m1(synthetic_blocks_dict)

    torch.manual_seed(42)
    m2 = backbone.MultiModalBackbone(
        block_dims=BLOCK_DIMS, proj_dims=PROJ_DIMS, hidden_dim=128, latent_dim=64,
    )
    z2 = m2(synthetic_blocks_dict)
    assert torch.allclose(z1, z2)


def test_backbone_param_count_under_500k():
    """Backbone size sanity — too big = wrong design."""
    model = backbone.MultiModalBackbone(
        block_dims=BLOCK_DIMS, proj_dims=PROJ_DIMS, hidden_dim=128, latent_dim=64,
    )
    n_params = sum(p.numel() for p in model.parameters())
    assert 10_000 < n_params < 500_000, f"got {n_params}"


def test_backbone_supports_different_latent_dims(synthetic_blocks_dict):
    for z_dim in [32, 64, 128]:
        model = backbone.MultiModalBackbone(
            block_dims=BLOCK_DIMS, proj_dims=PROJ_DIMS, hidden_dim=128, latent_dim=z_dim,
        )
        z = model(synthetic_blocks_dict)
        assert z.shape == (200, z_dim)


def test_backbone_block_mask_zeros_modality(synthetic_blocks_dict):
    """F1/F2 ablation: block_mask={'text': 0.0} → text projection contribution removed."""
    torch.manual_seed(42)
    model = backbone.MultiModalBackbone(
        block_dims=BLOCK_DIMS, proj_dims=PROJ_DIMS, hidden_dim=128, latent_dim=64,
    )
    z_full = model(synthetic_blocks_dict)
    mask_no_text = {b: 1.0 for b in BLOCK_DIMS}
    mask_no_text['text'] = 0.0
    z_no_text = model(synthetic_blocks_dict, block_mask=mask_no_text)
    # Ablating text MUST change the output
    assert not torch.allclose(z_full, z_no_text), \
        "block_mask={text: 0.0} should change z; backbone isn't honoring the mask"

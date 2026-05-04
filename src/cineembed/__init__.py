"""CineEmbed — Multi-modal AE/VAE/DEC for movie metadata clustering.

See docs/superpowers/specs/2026-05-04-modeling-design.md for the full design.
"""

__version__ = "0.1.0"

# Public API: submodules are accessed via `from cineembed import <module>` directly.
# Pyright resolves these via `extraPaths: ["src"]` in pyrightconfig.json.
__all__ = ['__version__']

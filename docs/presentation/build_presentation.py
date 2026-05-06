#!/usr/bin/env python3
"""Build the CineEmbed intermediate progress presentation.

Run:
    cd docs/presentation/
    python3 build_presentation.py

Output:
    docs/presentation/intermediate-progress-presentation.pptx
"""
from pathlib import Path
import sys

from pptx import Presentation

HERE = Path(__file__).parent.resolve()
sys.path.insert(0, str(HERE))
from _slides import slides as S
from _slides import theme

OUT = HERE / "intermediate-progress-presentation.pptx"


def build() -> Path:
    prs = Presentation()
    prs.slide_width  = theme.SLIDE_W
    prs.slide_height = theme.SLIDE_H
    for builder in S.BUILDERS:
        builder(prs)
    prs.save(str(OUT))
    return OUT


if __name__ == "__main__":
    out = build()
    print(f"wrote {out}  ({out.stat().st_size:,} bytes)")

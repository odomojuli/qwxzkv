"""typosquat — comprehensive, ecosystem-parametric package-name confusion.

Two-stage design: transform *families* generate the candidate confusion set
(recall-first); distance *metrics* score and rank it (precision-first). The
ecosystem (PyPI / npm / crates) is an explicit parameter so the same engine is
correct on every registry. See ``docs/formalization.md``.
"""

from __future__ import annotations

from . import metrics, transforms
from ._accel import HAVE_RUST
from .ecosystems import CRATES, ECOSYSTEMS, GENERIC, NPM, PYPI, Ecosystem
from .ecosystems import get as get_ecosystem
from .generate import Candidate, generate
from .score import score

__all__ = [
    "Ecosystem",
    "ECOSYSTEMS",
    "PYPI",
    "NPM",
    "CRATES",
    "GENERIC",
    "get_ecosystem",
    "generate",
    "Candidate",
    "score",
    "metrics",
    "transforms",
    "HAVE_RUST",
]

__version__ = "0.1.0"

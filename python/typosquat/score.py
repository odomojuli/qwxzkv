"""Composite risk scoring — combine the metric channels into one number.

``risk = ( Σ wᵢ·simᵢ / Σ wᵢ ) · π(target)`` where ``simᵢ = 1 − distanceᵢ`` and
``π`` is an optional popularity/exposure prior for the target. The full
per-channel breakdown is returned for explainability. See formalization §5.
"""

from __future__ import annotations

from typing import Optional

from . import metrics as M
from .ecosystems import Ecosystem

# Defaults reflect: edit & visual confusion dominate observed package typos;
# phonetic and motor channels are weaker corroborating signals.
DEFAULT_WEIGHTS: dict[str, float] = {
    "edit": 1.0,
    "jaccard": 0.7,
    "visual": 0.9,
    "phonetic": 0.6,
    "keyboard": 0.5,
}


def channel_similarities(a: str, b: str) -> dict[str, float]:
    return {k: 1.0 - v for k, v in M.channel_distances(a, b).items()}


def score(
    candidate: str,
    target: str,
    ecosystem: Optional[Ecosystem] = None,
    weights: Optional[dict[str, float]] = None,
    popularity: float = 1.0,
) -> dict:
    """Return a risk record for ``candidate`` relative to ``target``.

    Keys: ``risk`` (final, in [0, 1]), ``base`` (pre-popularity), ``popularity``,
    ``similarities`` (per channel), ``weights``.
    """
    w = dict(DEFAULT_WEIGHTS)
    if weights:
        w.update(weights)
    sims = channel_similarities(candidate, target)
    denom = sum(w.get(k, 0.0) for k in sims) or 1.0
    base = sum(w.get(k, 0.0) * sims[k] for k in sims) / denom
    risk = max(0.0, min(1.0, base * popularity))
    return {
        "risk": risk,
        "base": base,
        "popularity": popularity,
        "similarities": sims,
        "weights": w,
    }

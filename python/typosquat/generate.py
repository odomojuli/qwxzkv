"""The orchestrator: run transform families, apply the ecosystem identity rule,
dedupe with provenance, optionally close over the edit ball, then score and rank.

This is where comprehensiveness (union of families, optional ``N_k`` closure) and
correctness-per-registry (drop anything that normalizes to the target) come
together. Output is deterministic and sorted by descending risk.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Sequence

from . import score as _score
from . import transforms as T
from .ecosystems import PYPI, Ecosystem


@dataclass
class Candidate:
    name: str
    normalized: str
    families: set[str] = field(default_factory=set)
    risk: float = 0.0
    breakdown: dict = field(default_factory=dict)

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        fams = ",".join(sorted(self.families))
        return f"Candidate({self.name!r}, risk={self.risk:.3f}, via={fams})"


def generate(
    target: str,
    ecosystem: Ecosystem = PYPI,
    families: Optional[Sequence[str]] = None,
    max_edit: int = 1,
    closure: bool = False,
    do_score: bool = True,
    weights: Optional[dict] = None,
    popularity: float = 1.0,
) -> list[Candidate]:
    """Enumerate and rank the confusion set for ``target`` in ``ecosystem``.

    Parameters
    ----------
    families:
        Which transform families to run. Defaults to the curated, high-precision
        default set (:data:`typosquat.transforms.DEFAULT_FAMILIES`).
    max_edit, closure:
        When ``closure`` is true (or ``max_edit > 1``), also union in the provably
        complete Damerau-Levenshtein ``N_{max_edit}`` neighborhood (the strong
        comprehensiveness guarantee), at higher cost.
    do_score, weights, popularity:
        Control composite risk scoring of each candidate.
    """
    eco = ecosystem
    fam = list(families) if families is not None else T.DEFAULT_FAMILIES
    target_norm = eco.normalize(target)
    out: dict[str, Candidate] = {}

    def consider(raw: str, family: str) -> None:
        if not raw or not eco.is_valid(raw):
            return
        norm = eco.normalize(raw)
        if norm == target_norm:  # same package under ν_E — not a squat
            return
        cand = out.get(norm)
        if cand is None:
            cand = Candidate(name=raw, normalized=norm)
            out[norm] = cand
        cand.families.add(family)

    for family in fam:
        spec = T.FAMILIES.get(family)
        if spec is None:
            raise KeyError(f"unknown family {family!r}; known: {T.ALL_FAMILIES}")
        for raw in spec["fn"](target, eco):
            consider(raw, family)

    if closure or max_edit > 1:
        from . import _accel

        alphabet = set(T.LETTERS + T.DIGITS) | set(eco.separators)
        for raw in _accel.edit_neighborhood(target, max_edit, alphabet):
            consider(raw, "edit_closure")

    candidates = list(out.values())
    if do_score:
        for cand in candidates:
            record = _score.score(cand.name, target, eco, weights=weights, popularity=popularity)
            cand.risk = record["risk"]
            cand.breakdown = record

    candidates.sort(key=lambda c: (-c.risk, c.normalized))
    return candidates

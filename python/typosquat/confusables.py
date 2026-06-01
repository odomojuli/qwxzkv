"""Visual confusability data.

Three things live here:

* ``GLYPH_SUBSTITUTIONS`` — drives the ``homoglyph`` *transform* (a generator).
  Includes multigraph confusions that pure single-character maps miss
  (``rn``/``m``, ``vv``/``w``, ``cl``/``d``).
* ``visual_cost`` — per-character substitution cost in [0, 1] for the
  confusable-weighted edit *metric* (a scorer).
* ``UNICODE_CONFUSABLES`` — a small Unicode TR39-style map for the
  ``unicode_confusable`` transform, used only for ecosystems whose normalized
  names admit non-ASCII (default off for PyPI/npm/crates).
"""

from __future__ import annotations

# --- generator data: multigraph + single-char visual swaps -------------------
GLYPH_SUBSTITUTIONS: dict[str, list[str]] = {
    "m": ["rn", "nn"],
    "rn": ["m"],
    "nn": ["m"],
    "w": ["vv"],
    "vv": ["w"],
    "d": ["cl"],
    "cl": ["d"],
    "l": ["1", "i"],
    "1": ["l", "i"],
    "i": ["l", "1", "j"],
    "0": ["o"],
    "o": ["0"],
    "5": ["s"],
    "s": ["5"],
    "8": ["b"],
    "b": ["8", "6"],
    "6": ["b"],
    "9": ["g", "q"],
    "g": ["9", "q"],
    "q": ["g", "9"],
    "2": ["z"],
    "z": ["2"],
}

# --- scorer data: confusable groups for the visual edit metric ---------------
_VISUAL_GROUPS: list[frozenset[str]] = [
    frozenset("o0"),
    frozenset("l1i"),
    frozenset("5s"),
    frozenset("8b"),
    frozenset("9gq"),
    frozenset("2z"),
    frozenset("uv"),
    frozenset("nm"),
    frozenset("ce"),
    frozenset("vw"),
]
_CONFUSABLE_COST = 0.15


def visual_cost(a: str, b: str) -> float:
    """Substitution cost between two single characters for the visual metric."""
    if a == b:
        return 0.0
    la, lb = a.lower(), b.lower()
    if la == lb:
        return 0.05  # case-only difference
    for group in _VISUAL_GROUPS:
        if la in group and lb in group:
            return _CONFUSABLE_COST
    return 1.0


# --- generator data: a compact Unicode confusables table ---------------------
UNICODE_CONFUSABLES: dict[str, list[str]] = {
    "a": ["а", "α"],  # Cyrillic a, Greek alpha
    "e": ["е"],  # Cyrillic e
    "o": ["о", "ο"],  # Cyrillic o, Greek omicron
    "p": ["р"],  # Cyrillic er
    "c": ["с", "ϲ"],  # Cyrillic es, Greek lunate sigma
    "x": ["х"],  # Cyrillic ha
    "y": ["у"],  # Cyrillic u
    "i": ["і", "ı"],  # Cyrillic i, dotless i
    "s": ["ѕ"],  # Cyrillic dze
    "j": ["ј"],  # Cyrillic je
    "h": ["һ"],  # Cyrillic shha
}

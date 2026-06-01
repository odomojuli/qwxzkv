"""Scoring metrics — the discriminative stage.

These measure how *close* a candidate is to a target along five channels. They
rank candidates; they never generate them. Each ``*_distance`` returns a value in
[0, 1] (0 = identical, 1 = maximally dissimilar) unless noted. See
``docs/formalization.md`` §5.
"""

from __future__ import annotations

import math

from . import _accel
from .confusables import visual_cost
from .keyboard import KEYBOARD_DIAG, trajectory

__all__ = [
    "levenshtein",
    "damerau_levenshtein",
    "normalized_edit",
    "qgrams",
    "jaccard_distance",
    "visual_distance",
    "normalized_visual",
    "phonetic_distance",
    "keyboard_frechet",
    "normalized_keyboard_distance",
    "channel_distances",
]


# --- edit channel ------------------------------------------------------------
def levenshtein(a: str, b: str) -> int:
    return _accel.levenshtein(a, b)


def damerau_levenshtein(a: str, b: str) -> int:
    return _accel.damerau_levenshtein(a, b)


def normalized_edit(a: str, b: str) -> float:
    m = max(len(a), len(b))
    return 0.0 if m == 0 else _accel.damerau_levenshtein(a, b) / m


# --- lexical channel: order-insensitive q-gram Jaccard -----------------------
def qgrams(s: str, q: int = 2) -> set[str]:
    if len(s) < q:
        return {s} if s else set()
    return {s[i : i + q] for i in range(len(s) - q + 1)}


def jaccard_distance(a: str, b: str, q: int = 2) -> float:
    """Jaccard distance over character q-gram sets. Cheap blocking key + channel."""
    A, B = qgrams(a, q), qgrams(b, q)
    if not A and not B:
        return 0.0
    union = len(A | B)
    if union == 0:
        return 0.0
    return 1.0 - len(A & B) / union


# --- visual channel: confusable-weighted edit distance -----------------------
def visual_distance(a: str, b: str) -> float:
    la, lb = len(a), len(b)
    if la == 0 or lb == 0:
        return float(max(la, lb))
    prev = [float(x) for x in range(lb + 1)]
    for i in range(1, la + 1):
        cur = [float(i)]
        for j in range(1, lb + 1):
            sub = prev[j - 1] + visual_cost(a[i - 1], b[j - 1])
            cur.append(min(prev[j] + 1.0, cur[j - 1] + 1.0, sub))
        prev = cur
    return prev[lb]


def normalized_visual(a: str, b: str) -> float:
    m = max(len(a), len(b))
    return 0.0 if m == 0 else visual_distance(a, b) / m


# --- phonetic channel: distance over phonetic codes --------------------------
def _soundex(s: str) -> str:
    letters = [ch for ch in s.upper() if ch.isalpha()]
    if not letters:
        return ""
    codes = {
        **dict.fromkeys("BFPV", "1"),
        **dict.fromkeys("CGJKQSXZ", "2"),
        **dict.fromkeys("DT", "3"),
        "L": "4",
        **dict.fromkeys("MN", "5"),
        "R": "6",
    }
    first = letters[0]
    out = [first]
    prev = codes.get(first, "")
    for ch in letters[1:]:
        c = codes.get(ch, "")
        if c and c != prev:
            out.append(c)
        if ch not in "HW":
            prev = c
    return (("".join(out)) + "000")[:4]


def _phonetic_code(s: str) -> str:
    try:
        import jellyfish  # optional dependency

        code = jellyfish.metaphone(s)
        if code:
            return code
    except Exception:
        pass
    return _soundex(s)


def phonetic_distance(a: str, b: str) -> float:
    ca, cb = _phonetic_code(a), _phonetic_code(b)
    if not ca and not cb:
        return 0.0
    m = max(len(ca), len(cb))
    if m == 0:
        return 0.0
    return _accel.levenshtein(ca, cb) / m


# --- motor channel: discrete Fréchet distance of keyboard trajectories -------
def _discrete_frechet(P: list[tuple[float, float]], Q: list[tuple[float, float]]) -> float:
    n, m = len(P), len(Q)
    ca = [[0.0] * m for _ in range(n)]
    for i in range(n):
        for j in range(m):
            d = math.hypot(P[i][0] - Q[j][0], P[i][1] - Q[j][1])
            if i == 0 and j == 0:
                ca[i][j] = d
            elif i == 0:
                ca[i][j] = max(ca[0][j - 1], d)
            elif j == 0:
                ca[i][j] = max(ca[i - 1][0], d)
            else:
                ca[i][j] = max(min(ca[i - 1][j], ca[i - 1][j - 1], ca[i][j - 1]), d)
    return ca[n - 1][m - 1]


def keyboard_frechet(a: str, b: str) -> float:
    """Raw discrete Fréchet distance between the two keyboard trajectories."""
    P, Q = trajectory(a), trajectory(b)
    if not P and not Q:
        return 0.0
    if not P or not Q:
        return KEYBOARD_DIAG
    return _discrete_frechet(P, Q)


def normalized_keyboard_distance(a: str, b: str) -> float:
    """Keyboard-Fréchet distance normalized to [0, 1] by the layout diagonal."""
    return min(1.0, keyboard_frechet(a, b) / KEYBOARD_DIAG)


# --- bundle ------------------------------------------------------------------
def channel_distances(a: str, b: str) -> dict[str, float]:
    """All five normalized channel distances, for scoring and explainability."""
    return {
        "edit": normalized_edit(a, b),
        "jaccard": jaccard_distance(a, b),
        "visual": normalized_visual(a, b),
        "phonetic": phonetic_distance(a, b),
        "keyboard": normalized_keyboard_distance(a, b),
    }

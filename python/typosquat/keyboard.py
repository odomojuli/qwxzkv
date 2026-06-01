"""Keyboard geometry: key positions, physical adjacency, and typed trajectories.

Used by two things: the ``keyboard_replace`` / ``keyboard_insert`` transform
families (physically adjacent mis-keys), and the keyboard-Fréchet scoring metric
(a string as the polyline a finger traces over the layout).

Coordinates approximate a staggered QWERTY layout. Only one layout ships in
0.1.0; the model is layout-parametric and others can be added as position maps.
"""

from __future__ import annotations

import math

# (row characters, y, x-offset) — the x-offset encodes the physical row stagger.
_ROWS = [
    ("1234567890", 0.0, 0.0),
    ("qwertyuiop", 1.0, 0.5),
    ("asdfghjkl", 2.0, 0.75),
    ("zxcvbnm", 3.0, 1.25),
]

QWERTY: dict[str, tuple[float, float]] = {}
for _chars, _y, _xoff in _ROWS:
    for _i, _ch in enumerate(_chars):
        QWERTY[_ch] = (_xoff + _i, _y)

# Separators are given nominal off-layout positions so that trajectories of names
# containing them stay defined. They are deliberately excluded from typo-key
# adjacency (you do not "fat-finger" a letter into a hyphen).
_SEPARATOR_POS = {"-": (10.5, 0.0), "_": (10.5, 0.5), ".": (9.0, 3.0)}

KEY_PITCH = 1.0
# Diagonal of the lettered region, used to normalize Fréchet distances to [0, 1].
KEYBOARD_DIAG = math.hypot(10.5, 3.0)

DEFAULT_ADJACENCY_RADIUS = 1.3


def key_pos(ch: str) -> tuple[float, float] | None:
    """Position of a character's key, or None if it is not on the layout."""
    c = ch.lower()
    if c in QWERTY:
        return QWERTY[c]
    return _SEPARATOR_POS.get(c)


def _euclid(p: tuple[float, float], q: tuple[float, float]) -> float:
    return math.hypot(p[0] - q[0], p[1] - q[1])


def neighbors(ch: str, radius: float = DEFAULT_ADJACENCY_RADIUS) -> list[str]:
    """Letter/digit keys physically within ``radius`` of ``ch`` (sorted)."""
    c = ch.lower()
    p = QWERTY.get(c)
    if p is None:
        return []
    out = [other for other, q in QWERTY.items() if other != c and _euclid(p, q) <= radius]
    return sorted(out)


def trajectory(s: str) -> list[tuple[float, float]]:
    """The polyline of key positions for the characters of ``s`` (lowercased).

    Characters with no key position are skipped, so the trajectory is the motor
    path of what is actually typed on the layout.
    """
    pts: list[tuple[float, float]] = []
    for ch in s:
        p = key_pos(ch)
        if p is not None:
            pts.append(p)
    return pts

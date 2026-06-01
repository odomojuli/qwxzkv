"""Acceleration dispatch.

Prefer the compiled Rust kernel (``typosquat._core``) when it is installed; fall
back to the pure-Python reference otherwise. Callers import from here, never from
``_pyref`` or ``_core`` directly, so the choice is transparent.
"""

from __future__ import annotations

from collections.abc import Iterable

from . import _pyref

try:  # pragma: no cover - exercised only when the wheel is built with Rust
    from . import _core  # type: ignore[attr-defined]

    HAVE_RUST = True
except Exception:  # ImportError, or ABI mismatch
    _core = None  # type: ignore[assignment]
    HAVE_RUST = False


def levenshtein(a: str, b: str) -> int:
    if _core is not None:
        return _core.levenshtein(a, b)
    return _pyref.levenshtein(a, b)


def damerau_levenshtein(a: str, b: str) -> int:
    if _core is not None:
        return _core.damerau_levenshtein(a, b)
    return _pyref.damerau_osa(a, b)


def edit_neighborhood(name: str, k: int, alphabet: Iterable[str]) -> set[str]:
    if _core is not None:
        return set(_core.edit_neighborhood(name, k, "".join(sorted(set(alphabet)))))
    return _pyref.edit_neighborhood(name, k, alphabet)

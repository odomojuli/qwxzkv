"""Ecosystem models: the parameter that makes the framework correct per registry.

Each :class:`Ecosystem` carries its normalization ``ν_E`` (how the registry
decides two names are the *same package*) and its validity predicate. The
normalization is what makes, e.g., a ``-``↔``_`` swap a no-op on PyPI but a real
attack on npm — see ``docs/formalization.md`` §1.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class Ecosystem:
    name: str
    normalize: Callable[[str], str]
    is_valid: Callable[[str], bool]
    separators: tuple[str, ...]
    allows_scope: bool = False
    allows_unicode: bool = False
    max_len: int = 214

    def equivalent(self, a: str, b: str) -> bool:
        """True when ``a`` and ``b`` are the same package under this registry."""
        return self.normalize(a) == self.normalize(b)


# --- PyPI (PEP 503 / packaging name normalization) ---------------------------
_PYPI_VALID = re.compile(r"^([a-z0-9]|[a-z0-9][a-z0-9._-]*[a-z0-9])$", re.IGNORECASE)


def _pypi_normalize(s: str) -> str:
    return re.sub(r"[-_.]+", "-", s).lower()


def _pypi_valid(s: str) -> bool:
    return bool(s) and len(s) <= 214 and _PYPI_VALID.match(s) is not None


PYPI = Ecosystem(
    name="pypi",
    normalize=_pypi_normalize,
    is_valid=_pypi_valid,
    separators=("-", "_", "."),
    allows_scope=False,
    allows_unicode=False,
    max_len=214,
)


# --- npm (separators are significant; optional @scope/name) ------------------
_NPM_VALID = re.compile(r"^(@[a-z0-9][a-z0-9._-]*/)?[a-z0-9][a-z0-9._-]*$")


def _npm_normalize(s: str) -> str:
    return s.lower()


def _npm_valid(s: str) -> bool:
    return bool(s) and len(s) <= 214 and _NPM_VALID.match(s) is not None


NPM = Ecosystem(
    name="npm",
    normalize=_npm_normalize,
    is_valid=_npm_valid,
    separators=("-", "_", "."),
    allows_scope=True,
    allows_unicode=False,
    max_len=214,
)


# --- crates.io ( '-' and '_' unified for uniqueness; case-insensitive ) ------
_CRATES_VALID = re.compile(r"^[a-z0-9][a-z0-9_-]*$", re.IGNORECASE)


def _crates_normalize(s: str) -> str:
    return s.lower().replace("_", "-")


def _crates_valid(s: str) -> bool:
    return bool(s) and len(s) <= 64 and _CRATES_VALID.match(s) is not None


CRATES = Ecosystem(
    name="crates",
    normalize=_crates_normalize,
    is_valid=_crates_valid,
    separators=("-", "_"),
    allows_scope=False,
    allows_unicode=False,
    max_len=64,
)


# --- generic permissive ecosystem (also the domain-style fallback) -----------
def _generic_normalize(s: str) -> str:
    return s.lower()


def _generic_valid(s: str) -> bool:
    return bool(s)


GENERIC = Ecosystem(
    name="generic",
    normalize=_generic_normalize,
    is_valid=_generic_valid,
    separators=("-", "_", "."),
    allows_scope=True,
    allows_unicode=True,
    max_len=1000,
)


ECOSYSTEMS: dict[str, Ecosystem] = {e.name: e for e in (PYPI, NPM, CRATES, GENERIC)}


def get(name: str) -> Ecosystem:
    """Look up an ecosystem by name (case-insensitive)."""
    try:
        return ECOSYSTEMS[name.lower()]
    except KeyError as exc:  # pragma: no cover - trivial
        raise KeyError(f"unknown ecosystem {name!r}; known: {sorted(ECOSYSTEMS)}") from exc

"""Pure-Python reference implementations of the hot-path kernels.

These are the source of truth. The optional Rust kernel (``typosquat._core``)
must produce identical results; ``tests/test_parity.py`` enforces that when the
kernel is present. Nothing here has third-party dependencies.
"""

from __future__ import annotations

from collections.abc import Iterable

__all__ = ["levenshtein", "damerau_osa", "one_edits", "edit_neighborhood"]


def levenshtein(a: str, b: str) -> int:
    """Classic Levenshtein edit distance (insert/delete/substitute)."""
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cost = 0 if ca == cb else 1
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost))
        prev = cur
    return prev[-1]


def damerau_osa(a: str, b: str) -> int:
    """Damerau-Levenshtein, Optimal String Alignment variant.

    Allows adjacent transposition as a unit-cost edit but forbids editing any
    substring more than once (the standard, fast restricted form). This is the
    distance used for the ``N_k`` neighborhood in the formalization.
    """
    la, lb = len(a), len(b)
    if not a:
        return lb
    if not b:
        return la
    d = [[0] * (lb + 1) for _ in range(la + 1)]
    for i in range(la + 1):
        d[i][0] = i
    for j in range(lb + 1):
        d[0][j] = j
    for i in range(1, la + 1):
        for j in range(1, lb + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + cost)
            if i > 1 and j > 1 and a[i - 1] == b[j - 2] and a[i - 2] == b[j - 1]:
                d[i][j] = min(d[i][j], d[i - 2][j - 2] + 1)
    return d[la][lb]


def one_edits(s: str, alphabet: Iterable[str]) -> set[str]:
    """All strings reachable from ``s`` by exactly one edit operation.

    Operations: delete, adjacent-transpose, substitute(c), insert(c) for every
    ``c`` in ``alphabet``. The union of these is exactly the radius-1 ball under
    Optimal String Alignment distance (minus ``s`` itself).
    """
    alpha = tuple(dict.fromkeys(alphabet))  # de-dup, stable order
    out: set[str] = set()
    n = len(s)
    for i in range(n):  # deletions
        out.add(s[:i] + s[i + 1 :])
    for i in range(n - 1):  # adjacent transpositions
        if s[i] != s[i + 1]:
            out.add(s[:i] + s[i + 1] + s[i] + s[i + 2 :])
    for i in range(n):  # substitutions
        for c in alpha:
            if c != s[i]:
                out.add(s[:i] + c + s[i + 1 :])
    for i in range(n + 1):  # insertions
        for c in alpha:
            out.add(s[:i] + c + s[i:])
    out.discard(s)
    return out


def edit_neighborhood(name: str, k: int, alphabet: Iterable[str]) -> set[str]:
    """All strings within Optimal String Alignment distance ``k`` of ``name``.

    BFS closure of :func:`one_edits`. With unrestricted ``alphabet`` this is the
    provably complete ``N_k`` neighborhood from the formalization (the edit
    channel's comprehensiveness guarantee).
    """
    alpha = tuple(dict.fromkeys(alphabet))
    seen = {name}
    frontier = {name}
    for _ in range(max(0, k)):
        nxt: set[str] = set()
        for s in frontier:
            for e in one_edits(s, alpha):
                if e not in seen:
                    seen.add(e)
                    nxt.add(e)
        frontier = nxt
        if not frontier:
            break
    seen.discard(name)
    return seen

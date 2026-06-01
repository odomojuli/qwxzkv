"""Transform families — the generative stage.

Each family is a generator ``fn(name, ecosystem) -> Iterator[str]`` that yields
raw candidate strings (one channel of confusion). They never validate, normalize,
or dedupe — :mod:`typosquat.generate` does that, applying the ecosystem's identity
rule. Families are grouped by channel and registered in :data:`FAMILIES`.

See ``docs/taxonomy.md`` for the catalog and the empirical coverage matrix.
"""

from __future__ import annotations

import re
from collections.abc import Iterator

from .confusables import GLYPH_SUBSTITUTIONS, UNICODE_CONFUSABLES
from .ecosystems import Ecosystem
from .keyboard import neighbors

LETTERS = "abcdefghijklmnopqrstuvwxyz"
DIGITS = "0123456789"
VOWELS = "aeiou"

COMMON_AFFIXES = [
    "js", "node", "python", "py", "lib", "core", "cli", "api", "sdk",
    "go", "rs", "2", "3", "io", "ng", "app", "dev", "x",
]


# === Channel A: orthographic =================================================
def omission(name: str, eco: Ecosystem) -> Iterator[str]:
    for i in range(len(name)):
        yield name[:i] + name[i + 1 :]


def duplication(name: str, eco: Ecosystem) -> Iterator[str]:
    for i in range(len(name)):
        yield name[: i + 1] + name[i] + name[i + 1 :]


def transposition(name: str, eco: Ecosystem) -> Iterator[str]:
    for i in range(len(name) - 1):
        if name[i] != name[i + 1]:
            yield name[:i] + name[i + 1] + name[i] + name[i + 2 :]


def substitution(name: str, eco: Ecosystem) -> Iterator[str]:
    """Broad single substitution over [a-z0-9]. Off by default (large output);
    ``keyboard_replace`` covers the high-probability subset."""
    alpha = LETTERS + DIGITS
    for i, ch in enumerate(name):
        low = ch.lower()
        if low.isalnum():
            for c in alpha:
                if c != low:
                    yield name[:i] + c + name[i + 1 :]


def keyboard_replace(name: str, eco: Ecosystem) -> Iterator[str]:
    for i, ch in enumerate(name):
        for c in neighbors(ch):
            yield name[:i] + c + name[i + 1 :]


def keyboard_insert(name: str, eco: Ecosystem) -> Iterator[str]:
    for i, ch in enumerate(name):
        for c in neighbors(ch):
            yield name[:i] + c + name[i:]
            yield name[: i + 1] + c + name[i + 1 :]


def vowel_swap(name: str, eco: Ecosystem) -> Iterator[str]:
    for i, ch in enumerate(name):
        if ch.lower() in VOWELS:
            for v in VOWELS:
                if v != ch.lower():
                    yield name[:i] + v + name[i + 1 :]


# === Channel B: perceptual ===================================================
def homoglyph(name: str, eco: Ecosystem) -> Iterator[str]:
    low = name.lower()
    for src, repls in GLYPH_SUBSTITUTIONS.items():
        start = 0
        while True:
            idx = low.find(src, start)
            if idx == -1:
                break
            for r in repls:
                yield name[:idx] + r + name[idx + len(src) :]
            start = idx + 1


def unicode_confusable(name: str, eco: Ecosystem) -> Iterator[str]:
    if not eco.allows_unicode:
        return
    for i, ch in enumerate(name):
        for u in UNICODE_CONFUSABLES.get(ch.lower(), ()):
            yield name[:i] + u + name[i + 1 :]


def homophone(name: str, eco: Ecosystem) -> Iterator[str]:
    rules = [
        ("ph", "f"), ("f", "ph"), ("c", "k"), ("k", "c"), ("s", "z"),
        ("z", "s"), ("x", "ks"), ("qu", "kw"), ("oo", "u"), ("ea", "ee"),
    ]
    low = name.lower()
    for src, dst in rules:
        start = 0
        while True:
            idx = low.find(src, start)
            if idx == -1:
                break
            yield name[:idx] + dst + name[idx + len(src) :]
            start = idx + 1


# === Channel C: encoding =====================================================
def bitsquat(name: str, eco: Ecosystem) -> Iterator[str]:
    for i, ch in enumerate(name):
        o = ord(ch)
        if o > 127:
            continue
        for bit in range(7):
            c = chr(o ^ (1 << bit))
            if c.isalnum() or c in "-_.":
                yield name[:i] + c + name[i + 1 :]


# === Channel D: package-structural ===========================================
def _tokens(name: str, eco: Ecosystem) -> list[str]:
    seps = "".join(re.escape(s) for s in eco.separators)
    if not seps:
        return [name] if name else []
    return [p for p in re.split(f"[{seps}]", name) if p]


def _primary_sep(name: str, eco: Ecosystem) -> str:
    for c in name:
        if c in eco.separators:
            return c
    return eco.separators[0] if eco.separators else "-"


def separator_swap(name: str, eco: Ecosystem) -> Iterator[str]:
    for i, ch in enumerate(name):
        if ch in eco.separators:
            for s in eco.separators:
                if s != ch:
                    yield name[:i] + s + name[i + 1 :]


def separator_delete(name: str, eco: Ecosystem) -> Iterator[str]:
    seps = set(eco.separators)
    for i, ch in enumerate(name):
        if ch in seps:
            yield name[:i] + name[i + 1 :]


def separator_insert(name: str, eco: Ecosystem) -> Iterator[str]:
    for i in range(1, len(name)):
        if name[i - 1].isalnum() and name[i].isalnum():
            for s in eco.separators:
                yield name[:i] + s + name[i:]


def token_reorder(name: str, eco: Ecosystem) -> Iterator[str]:
    toks = _tokens(name, eco)
    if len(toks) < 2:
        return
    sep = _primary_sep(name, eco)
    for i in range(len(toks) - 1):
        swapped = toks[:]
        swapped[i], swapped[i + 1] = swapped[i + 1], swapped[i]
        yield sep.join(swapped)
    if len(toks) > 2:
        yield sep.join(reversed(toks))


def affix_combo(name: str, eco: Ecosystem) -> Iterator[str]:
    sep = _primary_sep(name, eco)
    for a in COMMON_AFFIXES:
        yield f"{a}{sep}{name}"
        yield f"{name}{sep}{a}"
        yield f"{name}{a}"


def simplification(name: str, eco: Ecosystem) -> Iterator[str]:
    toks = _tokens(name, eco)
    if len(toks) < 2:
        return
    sep = _primary_sep(name, eco)
    stop = set(COMMON_AFFIXES)
    if toks[0] in stop:
        yield sep.join(toks[1:])
    if toks[-1] in stop:
        yield sep.join(toks[:-1])


def scope_manipulate(name: str, eco: Ecosystem) -> Iterator[str]:
    if not eco.allows_scope:
        return
    if name.startswith("@") and "/" in name:
        scope, _, rest = name[1:].partition("/")
        yield rest
        yield f"{scope}-{rest}"
    else:
        for scope in ("types", "npm", "node", "org"):
            yield f"@{scope}/{name}"


def grammatical_number(name: str, eco: Ecosystem) -> Iterator[str]:
    if name.endswith("s"):
        yield name[:-1]
    else:
        yield name + "s"


# === Registry ================================================================
# (family, fn, channel, default_on)
_REGISTRY = [
    ("omission", omission, "orthographic", True),
    ("duplication", duplication, "orthographic", True),
    ("transposition", transposition, "orthographic", True),
    ("substitution", substitution, "orthographic", False),
    ("keyboard_replace", keyboard_replace, "orthographic", True),
    ("keyboard_insert", keyboard_insert, "orthographic", True),
    ("vowel_swap", vowel_swap, "orthographic", True),
    ("homoglyph", homoglyph, "perceptual", True),
    ("unicode_confusable", unicode_confusable, "perceptual", True),
    ("homophone", homophone, "perceptual", True),
    ("bitsquat", bitsquat, "encoding", False),
    ("separator_swap", separator_swap, "structural", True),
    ("separator_delete", separator_delete, "structural", True),
    ("separator_insert", separator_insert, "structural", True),
    ("token_reorder", token_reorder, "structural", True),
    ("affix_combo", affix_combo, "structural", True),
    ("simplification", simplification, "structural", True),
    ("scope_manipulate", scope_manipulate, "structural", True),
    ("grammatical_number", grammatical_number, "structural", True),
]

FAMILIES = {
    name: {"fn": fn, "channel": channel, "default": default}
    for name, fn, channel, default in _REGISTRY
}
DEFAULT_FAMILIES = [name for name, _, _, default in _REGISTRY if default]
ALL_FAMILIES = [name for name, *_ in _REGISTRY]
CHANNELS = sorted({channel for _, _, channel, _ in _REGISTRY})


def families_in_channel(channel: str) -> list[str]:
    return [n for n, _, ch, _ in _REGISTRY if ch == channel]

"""Rust-kernel / pure-Python parity.

Skipped automatically when the compiled kernel is not installed (e.g. the
pure-Python CI job). When it *is* installed, the accelerated path must agree with
the reference bit-for-bit.
"""

import random

import pytest

from typosquat import _accel, _pyref

pytestmark = pytest.mark.skipif(not _accel.HAVE_RUST, reason="Rust kernel not built")


def _rand(n):
    return "".join(random.choice("abcde-_") for _ in range(n))


def test_distance_parity():
    random.seed(1234)
    for _ in range(500):
        a, b = _rand(random.randint(0, 9)), _rand(random.randint(0, 9))
        assert _accel.levenshtein(a, b) == _pyref.levenshtein(a, b)
        assert _accel.damerau_levenshtein(a, b) == _pyref.damerau_osa(a, b)


def test_neighborhood_parity():
    random.seed(99)
    alphabet = set("abc")
    for _ in range(50):
        name = _rand(random.randint(1, 5))
        assert _accel.edit_neighborhood(name, 1, alphabet) == _pyref.edit_neighborhood(
            name, 1, alphabet
        )

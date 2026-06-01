"""Property-based tests (Hypothesis) for the invariants that matter."""

import itertools

from hypothesis import given, settings
from hypothesis import strategies as st

from typosquat import _accel, metrics
from typosquat._pyref import damerau_osa
from typosquat.ecosystems import CRATES, NPM, PYPI

_ALPHABET = "abc"
_names = st.text(alphabet=_ALPHABET, min_size=1, max_size=5)


@given(_names)
@settings(max_examples=120, deadline=None)
def test_edit_neighborhood_equals_damerau_ball(name):
    """The edit generator is exactly the radius-1 OSA ball (formalization §4.1)."""
    nbr = _accel.edit_neighborhood(name, 1, set(_ALPHABET))

    # Soundness: every generated string is exactly distance 1.
    for x in nbr:
        assert damerau_osa(name, x) == 1

    # Completeness: every distance-1 string over the alphabet is generated.
    brute = set()
    for length in range(max(0, len(name) - 1), len(name) + 2):
        for tup in itertools.product(_ALPHABET, repeat=length):
            cand = "".join(tup)
            if cand != name and damerau_osa(name, cand) == 1:
                brute.add(cand)
    assert brute <= nbr


@given(st.text(min_size=0, max_size=8), st.text(min_size=0, max_size=8))
@settings(max_examples=200, deadline=None)
def test_metric_contracts(a, b):
    fns = [
        metrics.normalized_edit,
        metrics.jaccard_distance,
        metrics.normalized_visual,
        metrics.phonetic_distance,
        metrics.normalized_keyboard_distance,
    ]
    for fn in fns:
        d = fn(a, b)
        assert 0.0 <= d <= 1.0 + 1e-9  # bounded
        assert abs(fn(a, b) - fn(b, a)) < 1e-9  # symmetric
        assert fn(a, a) == 0.0  # identity of indiscernibles


@given(st.text(alphabet="abcdef-_", min_size=1, max_size=10))
@settings(max_examples=100, deadline=None)
def test_generate_excludes_target_equivalence_class(name):
    for eco in (PYPI, NPM, CRATES):
        if not eco.is_valid(name):
            continue
        for c in eco_generate(name, eco):
            assert not eco.equivalent(c.name, name)
            assert eco.is_valid(c.name)


def eco_generate(name, eco):
    from typosquat import generate

    return generate(name, ecosystem=eco, do_score=False)

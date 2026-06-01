"""End-to-end generation: the headline correctness properties."""

from typosquat import generate
from typosquat.ecosystems import CRATES, NPM, PYPI


def names(target, eco, **kw):
    return {c.name for c in generate(target, ecosystem=eco, **kw)}


def normalized(target, eco, **kw):
    return {c.normalized for c in generate(target, ecosystem=eco, **kw)}


def test_target_never_appears_as_candidate():
    for eco in (PYPI, NPM, CRATES):
        for c in generate("requests", ecosystem=eco):
            assert not eco.equivalent(c.name, "requests")


def test_separator_swap_is_noop_on_pypi_but_attack_on_npm():
    # PyPI: '-' <-> '_' <-> '.' all normalize together, so swap variants are the
    # SAME package and must be excluded.
    pypi_names = names("cross-env", PYPI)
    for variant in ("cross_env", "cross.env"):
        assert PYPI.normalize(variant) == "cross-env"
        assert variant not in pypi_names

    # npm: separators are significant, so they are genuine squats.
    npm_names = names("cross-env", NPM)
    assert "cross_env" in npm_names
    assert "crossenv" in npm_names  # separator deletion


def test_crates_dash_underscore_equivalence_excluded():
    assert "foo_bar" not in names("foo-bar", CRATES)
    assert CRATES.equivalent("foo-bar", "foo_bar")


def test_known_typosquats_present():
    pypi = names("requests", PYPI)
    assert "requets" in pypi  # omission
    assert "request" in pypi  # trailing-s omission / grammatical
    assert "reqests" in pypi  # omission of 'u'


def test_structural_squats_present_on_npm():
    assert "lodash-js" in names("lodash", NPM)  # combosquat
    assert "router-vue" in names("vue-router", NPM)  # reorder
    assert "@types/react" in names("react", NPM)  # scope


def test_provenance_is_recorded():
    cands = generate("requests", ecosystem=PYPI)
    by_name = {c.name: c for c in cands}
    assert by_name["request"].families  # non-empty provenance
    assert all(isinstance(c.families, set) and c.families for c in cands)


def test_scores_in_unit_interval_and_sorted():
    cands = generate("requests", ecosystem=PYPI)
    assert cands == sorted(cands, key=lambda c: (-c.risk, c.normalized))
    assert all(0.0 <= c.risk <= 1.0 for c in cands)


def test_determinism():
    a = [(c.name, c.normalized, round(c.risk, 9)) for c in generate("express", ecosystem=NPM)]
    b = [(c.name, c.normalized, round(c.risk, 9)) for c in generate("express", ecosystem=NPM)]
    assert a == b


def test_closure_grows_candidate_set():
    base = generate("abc", ecosystem=PYPI)
    closed = generate("abc", ecosystem=PYPI, closure=True, max_edit=1)
    assert len(closed) >= len(base)


def test_popularity_scales_risk():
    low = generate("requests", ecosystem=PYPI, popularity=0.1)
    high = generate("requests", ecosystem=PYPI, popularity=1.0)
    lo = {c.normalized: c.risk for c in low}
    hi = {c.normalized: c.risk for c in high}
    sample = next(iter(lo))
    assert lo[sample] <= hi[sample]

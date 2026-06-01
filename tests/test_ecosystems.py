"""Ecosystem normalization, validity, and identity-equivalence.

These pin the single most important correctness property of the framework: that
name *identity* is registry-specific (formalization §1).
"""

from typosquat.ecosystems import CRATES, NPM, PYPI, get


def test_pypi_normalization_collapses_separators():
    assert PYPI.normalize("Foo.Bar") == "foo-bar"
    assert PYPI.normalize("foo_bar") == "foo-bar"
    assert PYPI.normalize("foo--bar") == "foo-bar"
    assert PYPI.equivalent("foo.bar", "foo_bar")
    assert PYPI.equivalent("Foo-Bar", "foo.bar")


def test_npm_keeps_separators_distinct():
    assert NPM.normalize("cross-env") == "cross-env"
    assert not NPM.equivalent("cross-env", "cross_env")
    assert not NPM.equivalent("cross-env", "crossenv")


def test_crates_unifies_dash_underscore():
    assert CRATES.normalize("foo_bar") == "foo-bar"
    assert CRATES.equivalent("foo_bar", "foo-bar")
    assert CRATES.equivalent("Foo-Bar", "foo_bar")


def test_validity_rules():
    assert PYPI.is_valid("requests")
    assert not PYPI.is_valid("-bad")
    assert not PYPI.is_valid("bad-")
    assert not PYPI.is_valid("")
    assert NPM.is_valid("@scope/name")
    assert not NPM.is_valid("@/name")
    assert CRATES.is_valid("serde")
    assert not CRATES.is_valid("a" * 65)  # crates max length is 64


def test_lookup_is_case_insensitive():
    assert get("PyPI").name == "pypi"
    assert get("NPM").name == "npm"

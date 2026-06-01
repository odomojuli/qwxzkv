"""Per-family generator behavior."""

from typosquat import transforms as T
from typosquat.ecosystems import GENERIC, NPM, PYPI


def _set(gen):
    return set(gen)


def test_omission():
    assert "requets" in _set(T.omission("requests", PYPI))
    assert "request" in _set(T.omission("requests", PYPI))


def test_transposition_skips_equal_pairs():
    out = _set(T.transposition("aab", PYPI))
    assert "aba" in out  # swap positions 1,2
    assert "aab" not in out  # equal adjacent chars do not transpose


def test_duplication():
    assert "reqquests" in _set(T.duplication("requests", PYPI))


def test_keyboard_replace_uses_adjacency():
    out = _set(T.keyboard_replace("a", PYPI))
    assert "s" in out  # physically adjacent
    assert "p" not in out  # far away


def test_vowel_swap():
    out = _set(T.vowel_swap("requests", PYPI))
    assert "raquests" in out
    assert "riquests" in out


def test_homoglyph_multigraph():
    out = _set(T.homoglyph("numpy", PYPI))
    assert "nurnpy" in out  # m -> rn


def test_unicode_confusable_gated_by_ecosystem():
    assert _set(T.unicode_confusable("requests", PYPI)) == set()  # ASCII-only eco
    assert any("е" in c for c in T.unicode_confusable("requests", GENERIC))


def test_separator_families():
    assert "cross_env" in _set(T.separator_swap("cross-env", NPM))
    assert "crossenv" in _set(T.separator_delete("cross-env", NPM))
    assert "cross-env" in _set(T.separator_insert("crossenv", NPM))


def test_token_reorder():
    assert "router-vue" in _set(T.token_reorder("vue-router", NPM))


def test_affix_combo_and_simplification():
    combos = _set(T.affix_combo("lodash", NPM))
    assert "lodash-js" in combos
    assert "node-lodash" in combos
    assert "fetch" in _set(T.simplification("node-fetch", NPM))


def test_scope_manipulate_gated():
    assert _set(T.scope_manipulate("react", PYPI)) == set()  # pypi has no scopes
    npm_out = _set(T.scope_manipulate("react", NPM))
    assert "@types/react" in npm_out
    assert "types-react" in _set(T.scope_manipulate("@types/react", NPM))


def test_registry_is_consistent():
    assert set(T.DEFAULT_FAMILIES) <= set(T.ALL_FAMILIES)
    for name in T.ALL_FAMILIES:
        assert callable(T.FAMILIES[name]["fn"])
        assert T.FAMILIES[name]["channel"] in T.CHANNELS

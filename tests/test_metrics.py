"""Distance-metric correctness and contracts."""

import math

from typosquat import metrics as M


def test_edit_distance_examples():
    assert M.levenshtein("kitten", "sitting") == 3
    assert M.damerau_levenshtein("ca", "ac") == 1  # one transposition
    assert M.levenshtein("ca", "ac") == 2  # plain Levenshtein needs two


def test_normalized_edit_bounds():
    assert M.normalized_edit("abc", "abc") == 0.0
    assert 0.0 < M.normalized_edit("abc", "abd") <= 1.0


def test_jaccard():
    assert M.jaccard_distance("abc", "abc") == 0.0
    assert M.jaccard_distance("abcd", "abce") < 1.0
    assert M.jaccard_distance("ab", "xy") == 1.0


def test_visual_confusables_are_cheaper():
    # 'o'->'0' is a confusable (cheap); 'o'->'q' is not (full cost)
    assert M.visual_distance("logo", "log0") < M.visual_distance("logo", "logq")


def test_phonetic_groups_similar_sounds():
    # same phonetic code -> distance 0
    assert M.phonetic_distance("smith", "smith") == 0.0
    assert M.phonetic_distance("fone", "phone") < M.phonetic_distance("fone", "zzzz")


def test_keyboard_frechet():
    # identical trajectory -> 0; adjacent-key slip is small; far apart is larger
    assert M.keyboard_frechet("asdf", "asdf") == 0.0
    near = M.normalized_keyboard_distance("asdf", "asdg")  # f->g adjacent
    far = M.normalized_keyboard_distance("asdf", "asdp")  # f->p far
    assert near < far
    assert 0.0 <= near <= 1.0 and 0.0 <= far <= 1.0


def test_channel_bundle_keys():
    d = M.channel_distances("requests", "reqests")
    assert set(d) == {"edit", "jaccard", "visual", "phonetic", "keyboard"}
    assert all(0.0 <= v <= 1.0 + 1e-9 for v in d.values())


def test_discrete_frechet_is_symmetric():
    a = M.keyboard_frechet("hello", "world")
    b = M.keyboard_frechet("world", "hello")
    assert math.isclose(a, b)

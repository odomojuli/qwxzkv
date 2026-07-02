"""Empirical coverage matrix.

Every *orthographic or structural* category in the USENIX Security 2023
package-confusion taxonomy (Neupane et al.) must map to at least one *registered*
transform family that actually generates a candidate. An unmapped or non-producing
category among those is a coverage gap. This is the test backing the matrix in
``docs/taxonomy.md``.

Deliberately NOT enforced here (a generator cannot produce them; see
``docs/research/measurement-methodology.md``): Neupane's Semantic substitution (#6),
Asemantic substitution (#7), and Alternate spelling (#10) are the semantic frontier,
and Familiar term abuse (#13) is targetless. Grammatical substitution (#4) is only
partially covered (plural, not verbal forms). These are the bounded frontier, not
silent gaps.
"""

import pytest

from typosquat import transforms as T
from typosquat.ecosystems import GENERIC, NPM, PYPI

# category -> [(family, sample_name, ecosystem), ...]
COVERAGE = {
    "typosquatting": [
        ("omission", "requests", PYPI),
        ("transposition", "requests", PYPI),
        ("keyboard_replace", "requests", PYPI),
    ],
    "combosquatting": [("affix_combo", "lodash", NPM)],
    "simplification": [("simplification", "node-fetch", NPM)],
    "delimiter_modification": [
        ("separator_swap", "cross-env", NPM),
        ("separator_delete", "cross-env", NPM),
    ],
    "sequence_order": [("token_reorder", "vue-router", NPM)],
    "scope_confusion": [("scope_manipulate", "react", NPM)],
    "homophone": [("homophone", "crypto", PYPI)],
    "homographic": [
        ("homoglyph", "numpy", PYPI),
        ("unicode_confusable", "requests", GENERIC),
    ],
    "grammatical_number": [("grammatical_number", "request", PYPI)],
}


@pytest.mark.parametrize("category,entries", list(COVERAGE.items()))
def test_category_has_generating_family(category, entries):
    produced = False
    for family, sample, eco in entries:
        assert family in T.FAMILIES, f"{category}: family {family!r} not registered"
        if list(T.FAMILIES[family]["fn"](sample, eco)):
            produced = True
    assert produced, f"no family generated any candidate for category {category!r}"


def test_all_registered_families_are_documented_channels():
    for name, spec in T.FAMILIES.items():
        assert spec["channel"] in {"orthographic", "perceptual", "encoding", "structural"}

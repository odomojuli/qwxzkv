"""Golden-fixture membership tests.

Stable expectations that must not regress. Membership/exclusion only (not exact
counts), so the fixtures stay robust as families are tuned.
"""

import json
import pathlib

from typosquat import generate
from typosquat.ecosystems import get

_DATA = pathlib.Path(__file__).parent / "data" / "golden_cases.json"


def test_golden_cases():
    cases = json.loads(_DATA.read_text())["cases"]
    assert cases
    for case in cases:
        eco = get(case["ecosystem"])
        cands = generate(case["target"], ecosystem=eco)
        names = {c.name for c in cands}
        norms = {c.normalized for c in cands}
        tag = f'{case["target"]}/{eco.name}'
        for inc in case.get("must_include", []):
            assert inc in names, f"{tag}: expected to generate {inc!r}"
        for exc in case.get("must_exclude", []):
            assert exc not in names, f"{tag}: should not generate {exc!r}"
        for exc in case.get("must_exclude_normalized", []):
            assert exc not in norms, f"{tag}: normalized {exc!r} should be absent"

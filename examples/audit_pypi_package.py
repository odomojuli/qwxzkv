"""Rank the most likely confusion squats of a package name.

    python examples/audit_pypi_package.py requests
"""

from __future__ import annotations

import sys

from typosquat import generate
from typosquat.ecosystems import get


def main(argv: list[str]) -> int:
    target = argv[1] if len(argv) > 1 else "requests"
    ecosystem = get(argv[2]) if len(argv) > 2 else get("pypi")
    cands = generate(target, ecosystem=ecosystem)
    print(f"{len(cands)} candidates for {target!r} on {ecosystem.name}; top 15 by risk:\n")
    for c in cands[:15]:
        sims = c.breakdown.get("similarities", {})
        detail = " ".join(f"{k}={v:.2f}" for k, v in sims.items())
        print(f"  {c.risk:5.3f}  {c.name:24}  [{detail}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

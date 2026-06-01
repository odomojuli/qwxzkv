"""Can a package name be un-typosquatted?

Uses the library as its own adversary: score how attackable a name is, search for
the least-squattable construction, and emit the defensive-registration set that
makes the winner immune in practice.

    PYTHONPATH=python python examples/least_squattable.py
"""

from __future__ import annotations

from typosquat import generate
from typosquat.ecosystems import PYPI


def profile(name: str, eco=PYPI) -> dict:
    """Squattability profile of a name (worst case: target assumed maximally popular)."""
    cands = generate(name, ecosystem=eco, popularity=1.0)
    risks = sorted((c.risk for c in cands), reverse=True)
    top = risks[:10]
    return {
        "name": name,
        "len": len(name),
        "n": len(cands),
        "max": risks[0] if risks else 0.0,
        "mean_top10": (sum(top) / len(top)) if top else 0.0,
    }


# A battery of naming strategies.
BATTERY = [
    # real / word-like names
    "ab", "cat", "data", "flask", "numpy", "pandas", "requests", "express",
    "internationalization",
    # high-entropy, vowel-less, confusable-free, separator-free
    "hjprty", "jrthpy", "thrpyj", "rtyhpj",
    "hjprty347", "thrpy47jr",
    # mixed (contains confusable/keyboard-rich chars on purpose, for contrast)
    "qwxzkv", "kfthx47",
]


def main() -> int:
    rows = [profile(n) for n in BATTERY]
    rows.sort(key=lambda r: (r["max"], r["n"]))  # least squattable first

    print("Squattability leaderboard (PyPI; lower = harder to typosquat)\n")
    print(f"  {'name':22} {'len':>3} {'cands':>6} {'max_risk':>9} {'mean_top10':>11}")
    for r in rows:
        print(
            f"  {r['name']:22} {r['len']:>3} {r['n']:>6} "
            f"{r['max']:>9.3f} {r['mean_top10']:>11.3f}"
        )

    # Impossibility check: is any confusion set empty?
    min_n = min(r["n"] for r in rows)
    print(f"\nSmallest confusion set in the battery: {min_n} candidates.")
    print("No valid name reaches 0 -> strict immunity is impossible.")

    # Winner among *practical* names (length 6-12).
    practical = [r for r in rows if 6 <= r["len"] <= 12]
    winner = practical[0]
    print(
        f"\nLeast-squattable practical name: {winner['name']!r}  "
        f"(len {winner['len']}, {winner['n']} candidates, max risk {winner['max']:.3f})"
    )

    # The deliverable: the high-risk head to pre-register.
    print(f"\nDefensive-registration set for {winner['name']!r} (top 12 by risk):")
    for c in generate(winner["name"], ecosystem=PYPI)[:12]:
        print(f"  {c.risk:5.3f}  {c.name:20}  via {','.join(sorted(c.families))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

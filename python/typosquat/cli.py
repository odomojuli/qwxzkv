"""Command-line interface: ``qwxzkv generate <name> ...``."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Optional, Sequence

from .ecosystems import ECOSYSTEMS
from .generate import generate
from .transforms import ALL_FAMILIES


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="qwxzkv",
        description="Enumerate and rank package-name typosquats.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("generate", help="generate candidate squats for a name")
    g.add_argument("name")
    g.add_argument("-e", "--ecosystem", default="pypi", choices=sorted(ECOSYSTEMS))
    g.add_argument("--max-edit", type=int, default=1)
    g.add_argument(
        "--closure",
        action="store_true",
        help="union in the provably complete edit-distance neighborhood",
    )
    g.add_argument("--families", nargs="*", choices=ALL_FAMILIES, default=None)
    g.add_argument("--top", type=int, default=25, help="0 for all")
    g.add_argument("--json", action="store_true")
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.cmd == "generate":
        eco = ECOSYSTEMS[args.ecosystem]
        cands = generate(
            args.name,
            ecosystem=eco,
            families=args.families,
            max_edit=args.max_edit,
            closure=args.closure,
        )
        shown = cands if args.top == 0 else cands[: args.top]
        if args.json:
            payload = [
                {
                    "name": c.name,
                    "normalized": c.normalized,
                    "risk": round(c.risk, 4),
                    "families": sorted(c.families),
                }
                for c in shown
            ]
            json.dump(payload, sys.stdout, indent=2, ensure_ascii=False)
            sys.stdout.write("\n")
        else:
            print(
                f"# {len(cands)} candidates for {args.name!r} on {eco.name} "
                f"(showing {len(shown)})"
            )
            for c in shown:
                print(f"{c.risk:6.3f}  {c.name:30}  {','.join(sorted(c.families))}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

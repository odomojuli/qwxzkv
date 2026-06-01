# Contributing

Thanks for helping make package ecosystems harder to attack.

## Project shape

- `python/typosquat/` — the reference implementation (pure Python, no hard deps).
- `rust/typosquat_core/` — optional PyO3 acceleration kernel. **Every feature
  must work without it.** The Rust kernel only ever *speeds up* a behavior that
  already has a pure-Python reference in `_pyref.py`.
- `docs/` — the formal model (`formalization.md`), the transform catalog and
  coverage matrix (`taxonomy.md`), and the paper sources.
- `tests/` — unit, property-based (`hypothesis`), and golden-fixture tests.

## Dev setup

```bash
python -m pip install -e ".[dev]"     # needs a Rust toolchain for the kernel
# ...or, no Rust required:
python -m pip install pytest hypothesis jellyfish
pytest -q                              # conftest.py puts python/ on the path
```

## Ground rules

1. **Pure-Python parity.** A new kernel function in Rust needs an identical
   pure-Python implementation in `_pyref.py`, and a test asserting they agree.
2. **New transform family?** Add it to `transforms.py`, register it in the family
   registry, document it in `docs/taxonomy.md`, and add a row to the coverage
   matrix. If it answers an attack category that previously had no family, also
   update `tests/test_coverage.py`.
3. **New metric?** Add it to `metrics.py` with documented range, and a property
   test for its mathematical contract (e.g. identity-of-indiscernibles, symmetry
   where applicable, bounds).
4. **Determinism.** Generation output must be deterministic and sorted. If you
   change ordering, update the golden fixtures intentionally (`tests/data/`).
5. **Run before pushing:** `ruff check python tests && ruff format python tests && pytest -q`.

## Security research note

This tool enumerates *attacker* candidate names so defenders can pre-register or
block them. Do not use generated names to publish packages you do not own.

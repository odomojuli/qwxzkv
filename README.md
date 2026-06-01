# qwxzkv

qwxzkv enumerates every name an attacker could register to impersonate a package
on PyPI, npm, or crates, then ranks each by risk. Transform families generate the
confusion set; edit, Jaccard, visual, phonetic, and keyboard-Fréchet metrics
score it. Ecosystem-aware, provably complete for the typing channel — named for
the one name it can't squat.

`qwxzkv` generates the set of names an attacker could register to be confused
with a target package — across PyPI, npm, and crates.io — and ranks each
candidate by how dangerous it is. It is built to be *comprehensive* (provably
complete for the typing-error channel, empirically complete against the published
attack taxonomy) and *honest about the registry*: the same trick that squats
`cross-env` on npm is a harmless no-op on PyPI, and the model knows the
difference.

> Status: **0.1.0, alpha.** Research preview accompanying a paper-in-preparation.
> The distribution is named `qwxzkv` — fittingly, the least-squattable name the
> tool itself could find, and almost certainly still free on PyPI. The import
> package stays `typosquat` for readability.

## Why another typosquatting tool?

Most tools bolt together a fixed list of string tricks and an edit-distance
threshold. Two problems:

1. **Edit distance is the wrong generator.** Combosquatting (`lodash` →
   `lodash-js`), token reordering (`vue-router` → `router-vue`), and npm scope
   abuse are *far* outside a Levenshtein-2 ball, yet they are the bulk of modern
   campaigns. We **generate constructively** from transform families and use
   distance only to **rank** — never to enumerate.
2. **The registry is ignored.** Name *identity* differs per ecosystem (PyPI
   collapses `-`, `_`, `.`; crates unifies `-`/`_`; npm keeps them distinct).
   We make the ecosystem a first-class parameter, so a transform automatically
   fires or stays silent depending on where you are squatting.

The design is laid out formally in [`docs/formalization.md`](docs/formalization.md)
and cataloged in [`docs/taxonomy.md`](docs/taxonomy.md).

## Architecture

```
                 generate(target, ecosystem)            score(candidate, target)
  target ──▶ ┌─────────────────────────────┐   ┌──────────────────────────────┐
             │  TRANSFORM FAMILIES          │   │  DISTANCE METRICS            │
             │  (generative, recall-first)  │──▶│  (discriminative, rank)      │──▶ ranked
             │  omission, keyboard, homo-   │   │  Damerau–Levenshtein, q-gram │     candidates
             │  glyph, separator, scope,    │   │  Jaccard, visual-confusable, │     + score
             │  combosquat, reorder, …      │   │  phonetic, keyboard-Fréchet  │     breakdown
             └─────────────────────────────┘   └──────────────────────────────┘
                          │                                  ▲
              ecosystem ν_E / valid_E           popularity prior π(target)
        (PEP 503 · npm · crates.io)
```

The two stages are deliberately separate: **generation is comprehensive,
scoring is precise.** See the formalization for why this matters.

- **Pure-Python reference** in `python/typosquat/` — no hard dependencies.
- **Optional Rust kernel** (`rust/typosquat_core/`, PyO3) accelerates the
  hot paths (edit distance, neighborhood closure). Everything works without it;
  the kernel only speeds up behavior that already has a Python reference.

## Install

```bash
# From source, no Rust toolchain needed (pure-Python path):
pip install pytest hypothesis jellyfish     # jellyfish optional, for phonetics
git clone https://github.com/odomojuli/qwxzkv && cd qwxzkv
pytest -q

# With the Rust acceleration kernel (needs a Rust toolchain):
pip install -e ".[dev]"
```

## Quickstart

```python
from typosquat import generate, score
from typosquat.ecosystems import PYPI, NPM

# Enumerate the confusion set for a PyPI package
candidates = generate("requests", ecosystem=PYPI, max_edit=1)
for c in candidates[:10]:
    print(f"{c.name:20} {c.risk:.3f}  via {sorted(c.families)}")

# Separator swap is a no-op on PyPI (same normalized package) ...
assert "request_s" not in {c.name for c in generate("requests", ecosystem=PYPI)}
# ... but a real squat on npm:
npm_cands = {c.name for c in generate("cross-env", ecosystem=NPM)}
assert "crossenv" in npm_cands and "cross_env" in npm_cands
```

CLI:

```bash
qwxzkv generate requests --ecosystem pypi --top 20
qwxzkv generate cross-env --ecosystem npm --json > cross-env.squats.json
```

## What's modeled

Nine+ generative families across four channels — orthographic (typing),
perceptual (visual/phonetic), encoding (bitsquat), and package-structural
(separators, scope, token order, combosquatting) — each mapped to the empirical
attack categories of **Neupane et al., USENIX Security 2023**. Full catalog and
coverage matrix: [`docs/taxonomy.md`](docs/taxonomy.md).

## Repository layout

| Path | What |
|------|------|
| `docs/formalization.md` | the formal model (paper §3–5) |
| `docs/taxonomy.md` | transform catalog + empirical coverage matrix |
| `docs/paper/` | paper outline and related work |
| `python/typosquat/` | reference implementation |
| `rust/typosquat_core/` | optional PyO3 acceleration kernel |
| `tests/` | unit, property-based, and golden-fixture tests |
| `benchmarks/` | enumeration throughput |

## Citing

See [`CITATION.cff`](CITATION.cff).

## License

[Apache-2.0](LICENSE). (Chosen for the explicit patent grant common in security
tooling; change before first release if your venue prefers MIT/BSD.)

## Responsible use

This tool enumerates *attacker* candidate names so defenders can pre-register,
block, or triage them. Do not publish packages under generated names you do not
own.

# Transform Taxonomy & Coverage Matrix

This is the catalog of confusion **channels** and the concrete **transform
families** that generate candidates for each. It pairs with the formal model in
[`formalization.md`](./formalization.md). Every family here is implemented in
`python/typosquat/transforms.py` with the same identifier.

Notation: a family is a generator `T(name, E) → candidates`. "Edit dist." is the
typical Damerau–Levenshtein distance of the output from the input. "E-gated"
means the family's outputs may be silenced by a particular ecosystem's
normalization `ν_E` (see formalization §1).

---

## Channel A — Orthographic (mistyping)

| Family | Definition | Example (`requests`) | Edit dist. | E-gated |
|--------|------------|----------------------|-----------|---------|
| `omission` | delete one character | `requets` | 1 | no |
| `insertion` | insert a character (alphabet-restricted) | `requeasts` | 1 | no |
| `duplication` | double an existing character | `reqquests` | 1 | no |
| `substitution` | replace one character | `reuuests` | 1 | no |
| `transposition` | swap two adjacent characters | `reqeusts` | 1 (DL) | no |
| `keyboard_replace` | substitute with a physically adjacent key (layout `L`) | `reqyests` | 1 | no |
| `keyboard_insert` | insert a physically adjacent key | `reqwuests` | 1 | no |
| `vowel_swap` | replace a vowel with another vowel | `raquests` | 1 | no |

Channel A is **provably complete** for the 1-edit ball when alphabets are
unrestricted (formalization §4.1). The keyboard- and vowel-restricted variants
are the high-probability subset used by default.

## Channel B — Perceptual (misreading / mishearing)

| Family | Definition | Example | Edit dist. | E-gated |
|--------|------------|---------|-----------|---------|
| `homoglyph` | substitute a visually similar glyph or **multigraph** | `m`→`rn`, `w`→`vv`, `d`→`cl`, `l`↔`1`↔`I`, `0`↔`o` | 1–2 | no |
| `unicode_confusable` | TR39 confusable substitution (default-off for ASCII ecosystems) | `requеsts` (Cyrillic е) | 0* | yes |
| `homophone` | phonetic-equivalent respelling | `c`→`k`, `ph`→`f`, `-s`→`-z` | varies | no |

*`unicode_confusable` has zero ASCII edit distance because the change is
sub-character; it is precisely why the visual/phonetic *metrics*, not edit
distance, are needed for scoring this channel.

## Channel C — Encoding

| Family | Definition | Example | Edit dist. | E-gated |
|--------|------------|---------|-----------|---------|
| `bitsquat` | flip one bit of one byte; keep if result is a valid char | `requezts` (`s`=0x73→`z`? per-bit) | 1 | no |

Bitsquatting is weaker for registries than for DNS but is included for
completeness and for the domain setting the engine generalizes to.

## Channel D — Package-structural (ecosystem-specific)

| Family | Definition | Example | Edit dist. | E-gated |
|--------|------------|---------|-----------|---------|
| `separator_swap` | swap among `-` `_` `.` | `cross-env`→`cross_env` | 1 | **yes** (no-op on PyPI/crates) |
| `separator_insert` | insert a separator between tokens | `crossenv`→`cross-env` | 1 | yes |
| `separator_delete` | remove a separator | `cross-env`→`crossenv` | 1 | yes |
| `token_reorder` | permute separator-delimited tokens | `vue-router`→`router-vue` | large | partial |
| `affix_combo` | prepend/append a common term | `lodash`→`lodash-js`, `python-lodash` | large | no |
| `scope_manipulate` | add/drop/alter an npm-style scope | `name`→`@types/name`, `@a/x`→`a-x` | large | **yes** (npm only) |
| `simplification` | drop a stop-affix (`node-`, `-js`, `py`) | `node-fetch`→`fetch` | large | no |
| `grammatical_number` | add/remove trailing `s` | `request`→`requests` | 1 | no |

Channel D is where package squatting **diverges from domain squatting** and where
most modern campaigns live. `separator_*` and `scope_manipulate` are the families
most affected by the ecosystem parameter.

---

## Coverage matrix vs. the empirical taxonomy

Each row is an attack category from **Neupane et al., "Beyond Typosquatting: An
In-depth Look at Package Confusion," USENIX Security 2023** (1232 real attacks).
Every category must map to ≥1 generating family — an unmapped row is a coverage
gap and a failing test (`tests/test_coverage.py`).

| Empirical category | Generating family / families |
|--------------------|------------------------------|
| Typosquatting (1–2 edits) | `omission`, `insertion`, `duplication`, `substitution`, `transposition`, `keyboard_*`, `vowel_swap` |
| Combosquatting (added words) | `affix_combo` |
| Simplification (dropped words) | `simplification` |
| Delimiter / separator modification | `separator_swap`, `separator_insert`, `separator_delete` |
| Sequence / word-order confusion | `token_reorder` |
| Scope confusion (npm) | `scope_manipulate` |
| Homophone / phonetic | `homophone` |
| Homographic / visual | `homoglyph`, `unicode_confusable` |
| Grammatical (singular/plural) | `grammatical_number` |
| Dependency confusion (cross-registry, same name) | *registry dimension* — `scope_manipulate` + the cross-ecosystem mode (roadmap §) |

> Dependency confusion is partly **out of scope of name generation**: it reuses
> an *identical* internal name on a public registry. The library surfaces it via
> the cross-ecosystem mode (same name, different `E`) rather than a name
> transform; tracked explicitly so the matrix has no silent gap.

---

## Scoring channels (not generators)

For completeness, the metrics that *rank* the candidates above (see
formalization §5), implemented in `metrics.py`:

| Metric | Captures | Cost |
|--------|----------|------|
| Damerau–Levenshtein | edit-channel closeness | `O(\|a\|·\|b\|)` |
| q-gram Jaccard distance | order-insensitive lexical overlap; blocking key | `O(\|a\|+\|b\|)` |
| confusable-weighted edit | visual closeness (glyph cost matrix) | `O(\|a\|·\|b\|)` |
| double-metaphone distance | phonetic closeness | `O(\|a\|+\|b\|)` |
| discrete Fréchet (keyboard) | motor/gesture closeness | `O(\|a\|·\|b\|)` |

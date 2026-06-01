# A Formal Model of Package-Name Confusion

This document defines the problem the library solves and the mathematical
framework behind it. It is written to double as the technical core (Section 3–5)
of the accompanying paper. Notation is kept plain so the prose renders as
Markdown; the LaTeX paper source lives in `docs/paper/`.

---

## 1. The ecosystem as a parameter

Typosquatting of package names is **not** one problem — it is one problem per
registry, because each registry decides *name identity* differently. We make the
registry an explicit parameter.

An **ecosystem** is a tuple `E = (Σ_E, ν_E, valid_E, struct_E)`:

- `Σ_E` — the alphabet of characters a name may contain.
- `ν_E : Σ* → Σ*` — the **normalization** (canonicalization) function the
  registry uses to decide whether two names are the *same package*.
- `valid_E : Σ* → {0,1}` — the **validity** predicate (the registry's naming
  rules: allowed characters, length, start/end, scope syntax).
- `struct_E` — structural metadata: the separator set, scope/namespace syntax,
  length bounds, and case rules.

Two names are **identity-equivalent** when they share a normal form:

```
a ≡_E b   ⟺   ν_E(a) = ν_E(b)
```

Names in the same `ν_E`-class resolve to the *same* package. They are therefore
**not** squats of one another, and the generator must exclude them.

The three ecosystems shipped in `ecosystems.py`:

| Ecosystem | Normalization `ν_E(s)` | Effect |
|-----------|------------------------|--------|
| **PyPI** (PEP 503) | `lower(re.sub(r"[-_.]+", "-", s))` | `Foo.Bar ≡ foo-bar ≡ foo_bar` |
| **crates.io** | `lower(s).replace("_", "-")` | `foo_bar ≡ foo-bar`; case-insensitive |
| **npm** | `lower(s)` (separators significant) | `cross-env ≢ crossenv ≢ cross_env` |

**The central consequence.** The *same* lexical transform behaves differently
per ecosystem. Swapping `-`↔`_` is a **no-op on PyPI and crates** (the two names
normalize to one package) but a **real attack on npm** (`cross-env` vs
`crossenv` was a 2017 campaign reaching >700 hosts). A correct model cannot hard-
code one registry's intuitions. Comprehensiveness is always *relative to `E`*,
and the identity-exclusion step (§4.2) is what makes a transform "fire" in one
ecosystem and stay silent in another — automatically, with no special-casing.

---

## 2. The confusion set

Given a target name `t`, we want the **candidate confusion set**

```
C_E(t) = { c ∈ Σ*  :  valid_E(c)  ∧  c ≢_E t  ∧  c is plausibly confusable with t }
```

together with a **risk ranking** `r_E(c, t) ∈ [0, 1]` over its members.

The informal predicate "plausibly confusable" is split into two stages, and
**keeping them separate is the core design principle** of this library:

1. **Generation (enumeration).** *What could an attacker register?*
   Recall-oriented. Must be comprehensive. Produced constructively by
   **transform families** (§3).
2. **Scoring (discrimination).** *How dangerous is each candidate?*
   Precision-oriented. Ranks candidates for action. Produced by **distance
   metrics** (§5).

> **Why the split matters.** A frequent mistake is to use a single edit-distance
> threshold *as the generator* — "all names within Levenshtein 2." This is both
> **incomplete** (combosquatting `lodash → lodash-js` is distance 3; token
> reordering and scope attacks are larger still) and **inefficient** (it implies
> enumerating `Σ*` and filtering). We instead **generate constructively** from
> transform families and use metrics only to **rank**. Distance metrics
> (Levenshtein, Jaccard, visual, phonetic, keyboard) are scoring tools, not
> generators.

---

## 3. Transform families (the generators)

A **transform family** is a relation `T ⊆ Σ* × Σ*`, equivalently a map
`T : Σ* → 2^(Σ*)`. Each family models one *channel* of confusion. Full
definitions, examples, and the empirical-coverage matrix are in
[`taxonomy.md`](./taxonomy.md); the grouping:

- **A. Orthographic / edit channel** (mistyping): omission, insertion,
  duplication, substitution, adjacent transposition, keyboard-adjacency
  substitution & insertion.
- **B. Perceptual channel** (misreading / mishearing): visual homoglyph
  substitution — including *multigraphs* `rn→m`, `vv→w`, `cl→d` — and
  phonetic / homophone substitution.
- **C. Encoding channel**: bitsquatting (a single bit-flip of the byte
  encoding, relevant where a name traverses memory or DNS).
- **D. Package-structural channel** (ecosystem-specific): separator
  substitution / insertion / deletion, scope manipulation, token-order
  permutation, affixation / combosquatting, simplification, grammatical
  number (singular ↔ plural).

Every family is a generator with **provenance**: a produced candidate records
*which* families generated it, so a single name reached by both a keyboard slip
and a homoglyph is scored once but explained fully.

---

## 4. Comprehensiveness, made precise

"Completely comprehensive" is the project's stated goal. We give it two distinct,
defensible meanings — one provable, one empirical — because the channels have
different mathematical structure.

### 4.1 The edit channel: a provable closure

Let the edit-operation set be
`O = { delete, insert(σ), substitute(·→σ), transpose-adjacent }` for `σ ∈ Σ`.
Define the **k-neighborhood** under Damerau–Levenshtein distance `d_DL`:

```
N_k(t) = { x ∈ Σ*  :  d_DL(x, t) ≤ k }
```

**Claim (1-edit completeness).** The union of the orthographic families
{omission, insertion(∀σ∈Σ), substitution(∀σ∈Σ), adjacent-transposition} applied
once to `t` equals `N_1(t) \ {t}`.

*Sketch.* (⊆) every family output applies exactly one operation in `O`, so it
lies in `N_1(t)`. (⊇) every `x` with `d_DL(x,t)=1` differs by one operation of
`O`; that operation, with the appropriate `σ`, is emitted by the matching
family. Iterating the generator `k` times yields `N_k(t)`. ∎

So for the edit channel the generator is **complete** for the `k`-edit ball — the
strong, bounded sense of "comprehensive." The closure is implemented exactly in
the `edit_neighborhood(name, k, alphabet)` kernel and checked by a property test
(*every string at `d_DL ≤ 1` is generated*).

**Cost & control.** Full-alphabet closure is `O(|Σ|^k · |t|^k)`. In practice the
insertion/substitution alphabets are restricted to *plausible* `σ`
(keyboard-adjacent keys, visual confusables), giving `O(|Σ| · |t|)` per level
while preserving the high-probability part of the ball. The exhaustive kernel
remains available when true exhaustiveness is required.

### 4.2 Beyond edit distance: empirical coverage

Families in groups **B, C, D** are deliberately **not** bounded by small edit
distance. Combosquatting `lodash → lodash-utils` has `d_DL = 6`; a token reorder
`vue-router → router-vue` is larger still. For these channels "comprehensive"
cannot mean a metric ball. We instead define the full confusion set as a union
of family images:

```
C_E(t) = ( N_k(t)  ∪  ⋃_{T ∈ perceptual ∪ structural} T(t) )  ∩  valid_E   \   [t]_{≡E}
```

— the bounded edit ball, plus the images of the non-edit families, **restricted
to valid names** and with the target's entire equivalence class `[t]_{≡E}`
removed (this is the step that silences separator swaps on PyPI).

Coverage here is **empirical, not analytic**: we map every attack category in the
USENIX Security 2023 package-confusion taxonomy (Neupane et al., 1232 real-world
attacks) to **at least one** generating family, and maintain that mapping as a
**coverage matrix** in [`taxonomy.md`](./taxonomy.md). A category with no
generating family is a coverage gap and a failing test.

---

## 5. Scoring & ranking

For a candidate `c` and target `t`, each channel yields a normalized distance
`d_i ∈ [0,1]` and similarity `sim_i = 1 − d_i`:

| Channel | Metric `d_i` |
|---------|--------------|
| Edit | Damerau–Levenshtein `/ max(\|c\|,\|t\|)` |
| Lexical (order-insensitive) | **q-gram Jaccard distance** (q=2 default) |
| Visual | confusable-weighted edit distance `/ max len` |
| Phonetic | distance over double-metaphone codes |
| Motor / gesture | **normalized discrete Fréchet distance** of keyboard trajectories |

**Composite risk.**

```
                Σ_i  w_i · sim_i
r(c, t)  =  ( ----------------- ) · π(t)
                  Σ_i  w_i
```

where `π(t) ∈ (0,1]` is a **popularity / exposure prior** for the *target*
(downloads, dependent count): attackers aim at high-traffic packages, so risk
scales with how exposed `t` is. Weights `w_i` are configurable and can be fit by
logistic regression on a labeled corpus (the ecosyste.ms typosquatting dataset;
Backstabber's Knife Collection). The full per-channel breakdown is returned for
explainability — every score is auditable.

### 5.1 The three metrics the project named

- **Jaccard** — q-gram *set* Jaccard distance. Cheap, order-insensitive, ideal
  both as a **blocking key** (cluster candidates before expensive scoring) and as
  one scoring channel. It is **not** a generator.

- **Fréchet** — given a principled home as a **keyboard-trajectory** metric.
  Map each character to its key centroid on a layout `L`; a string becomes a
  *polyline* — the path a finger or stylus traces, exactly as in gesture/swipe
  typing. The **discrete Fréchet distance** between two such polylines measures
  *motor* confusability and catches collisions that character edit distance
  misses (two names that *feel* the same to type). Fréchet is the tight
  "dog-on-a-leash" coupling; **DTW** is offered as a looser alternative. Applying
  curve-similarity to package-name confusability is, to our knowledge, novel and
  is a contribution of this framework. (The project brief named Fréchet distance;
  this section is where it earns its place.)

- **Unicode similarity** — for ecosystems whose *normalized* names are ASCII
  (PyPI, npm, crates), pure-Unicode homoglyph attacks on the identifier are
  largely precluded by `ν_E`; the live perceptual channel is **ASCII multigraph**
  confusion (`rn`/`m`, `vv`/`w`, `cl`/`d`, `l`/`1`/`I`, `0`/`o`). We still
  implement Unicode TR39 *confusables* mapping as a perceptual transform and
  visual-distance input, **default-off** for ASCII ecosystems and **on** for
  contexts that render or accept Unicode (display names, and the domain setting
  the engine generalizes to).

---

## 6. Outputs and intended use

`generate(t, E, …)` returns a deterministic, ranked list of `Candidate` objects,
each carrying its normalized form, generating families (provenance), and per-
channel score breakdown. Intended consumers:

- **Defensive registration** — the high-risk head of the list is what a brand
  owner pre-registers.
- **Blocklisting / firewall rules** — feed candidate names to a registry proxy.
- **Reviewer triage** — rank newly-published names by similarity to popular
  targets (the GuardDog-style use case), oriented by `π(t)`.

Determinism and reproducibility are first-class: identical inputs and config
yield byte-identical output, which the test suite pins with golden fixtures.

---

## 7. Notation summary

| Symbol | Meaning |
|--------|---------|
| `Σ_E` | alphabet permitted by ecosystem `E` |
| `ν_E` | normalization (identity) function |
| `valid_E` | validity predicate |
| `≡_E` | identity-equivalence (`ν_E(a)=ν_E(b)`) |
| `[t]_{≡E}` | equivalence class of the target |
| `T : Σ*→2^(Σ*)` | a transform family (generator) |
| `N_k(t)` | Damerau–Levenshtein `k`-neighborhood of `t` |
| `C_E(t)` | candidate confusion set |
| `d_i`, `sim_i` | per-channel distance / similarity |
| `π(t)` | popularity / exposure prior of the target |
| `r(c,t)` | composite risk score in `[0,1]` |

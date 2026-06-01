# Paper outline (working title)

**A Generative Framework for Comprehensive Package-Name Confusion Enumeration**

Target venue class: applied-security (USENIX Security / ACM CCS / IEEE EuroS&P).
This outline maps directly onto the implementation; §3–6 are drafted in
`docs/formalization.md` and `docs/taxonomy.md`.

## Contributions (claims to defend)

1. **Ecosystem-parametric model.** Name *identity* (`ν_E`) is the right
   parameter; with it, one engine covers PyPI, npm, and crates.io correctly, and
   identity-exclusion makes per-registry behavior fall out automatically instead
   of being special-cased.
2. **Generate/score separation with a comprehensiveness argument.** A *provable*
   closure for the edit channel (the orthographic generator equals the
   Damerau–Levenshtein `k`-ball) plus an *empirical* coverage matrix mapping
   every category of the USENIX'23 package-confusion taxonomy to a generating
   family.
3. **A motor-confusability metric.** Keyboard-trajectory **discrete Fréchet
   distance** — strings as polylines over a key layout — as a scoring channel
   that captures gesture/typing similarity beyond character edit distance. Novel
   in this setting.
4. **A reproducible, dual-language artifact.** Pure-Python reference + optional
   Rust kernel, deterministic output, golden-fixture + property-based tests.
5. **Evaluation on real attack corpora** for recall, ranking quality, and
   throughput against existing tools.

## Section plan

1. **Introduction** — supply-chain threat; why name confusion specifically; the
   two failures of prior tools (edit-distance-as-generator; registry-blindness);
   contributions.
2. **Background & threat model** — package registries; PEP 503 / npm / crates
   naming and normalization; attacker goals (install-time confusion, dependency
   confusion); defender goals (pre-registration, blocklisting, triage).
3. **Formalization** — ecosystem tuple `E`; identity `≡_E`; the confusion set
   `C_E(t)`; the generate-then-score decomposition. *(= formalization §1–2.)*
4. **Transform families** — the four channels; full catalog; provenance.
   *(= taxonomy.md.)*
5. **Comprehensiveness** — 1-edit completeness proof and `k`-closure; empirical
   coverage matrix; explicit handling of dependency confusion. *(= form. §4.)*
6. **Scoring** — per-channel metrics; the keyboard-Fréchet channel; composite
   risk with popularity prior; weight fitting on labeled data. *(= form. §5.)*
7. **Implementation** — architecture; pure-Python/Rust parity; determinism;
   complexity and the alphabet-restriction knobs.
8. **Evaluation**
   - *Datasets:* ecosyste.ms typosquatting-dataset (labeled squat→target pairs);
     Backstabber's Knife Collection (malicious packages); registry top-N lists.
   - *Recall / coverage:* fraction of real squats reproduced by generation, vs.
     `typomania`, `andrew/typosquatting`, GuardDog's rule, `pypi-scan`.
   - *Ranking quality:* do real malicious squats rank near the top? (AUC / recall@k)
   - *Ablations:* contribution of each family and each metric channel.
   - *Throughput:* candidates/sec, pure-Python vs Rust kernel, vs name length.
9. **Case studies** — `crossenv`/`cross-env` (npm, 2017); representative PyPI
   campaigns; a separator/scope example unique to one registry.
10. **Discussion** — limitations (semantic combosquatting is open-ended;
    popularity prior data availability); generalization to domains; ethics and
    responsible use; coordinated disclosure posture.
11. **Related work** — see `related_work.md`.
12. **Conclusion.**

## Reviewer-anticipation notes

- *"Isn't this just dnstwist for packages?"* — No: the generate/score split,
  the ecosystem-parametric identity handling, the structural families
  (scope/separator/reorder/combo), and the Fréchet channel are the deltas.
  Quantify recall gains in §8.
- *"Combosquatting is unbounded."* — Acknowledge; bound it with a curated affix
  lexicon + popularity prior; report recall/precision trade-off.
- *"Why Fréchet over DTW?"* — Ablate both; Fréchet is the tighter coupling and
  models a single continuous gesture; report which wins on the labeled set.

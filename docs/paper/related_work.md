# Related work (draft)

Grouped by theme, with where **this** work differs. Entries marked ✔ were
confirmed against current sources during initial research (June 2026); entries
marked ◦ are from domain knowledge and **must be verified** (exact authors,
venue, year, pages) before submission.

## Package-confusion measurement & taxonomy

- ✔ **Neupane et al., "Beyond Typosquatting: An In-depth Look at Package
  Confusion," USENIX Security 2023.** 1232 real attacks; the taxonomy we adopt as
  our empirical coverage target (combosquatting, simplification, delimiter
  modification, sequence/order, scope, homophone, homographic, etc.).
  <https://www.usenix.org/system/files/usenixsecurity23-neupane.pdf>
- ✔ **Vu, Pashchenko, Massacci et al., "Typosquatting and Combosquatting Attacks
  on the Python Ecosystem," IEEE EuroS&P Workshops 2020.** PyPI-focused
  measurement; motivates the structural families.
- ◦ **Zimmermann et al., "Small World with High Risks: A Study of Security
  Threats in the npm Ecosystem," USENIX Security 2019.** Ecosystem-scale risk.
- ◦ **Ohm et al., "Backstabber's Knife Collection," DIMVA 2020.** Malicious
  package dataset we use for ranking evaluation.
- ◦ **Duan et al., "Towards Measuring Supply Chain Attacks on Package Managers for
  Interpreted Languages," NDSS 2021 (MalOSS).**

*Delta:* prior work largely *measures and classifies* observed attacks. We
provide a *generative* model that enumerates the candidate space ahead of attack,
with a comprehensiveness argument tied to that taxonomy.

## Detection tools

- ✔ **GuardDog (Datadog).** Static analysis + a typosquatting heuristic
  (Levenshtein to top-5000, two-character swap). Practical detector; narrow
  generator. <https://securitylabs.datadoghq.com/articles/guarddog-identify-malicious-pypi-packages/>
- ✔ **typomania (Rust Foundation).** Typosquatting primitives; powers crates.io's
  detection. <https://github.com/rustfoundation/typomania>
- ✔ **andrew/typosquatting (ecosyste.ms).** Multi-ecosystem variant generation +
  existence checks (PyPI, npm, RubyGems, Cargo, Go, Maven, NuGet, …).
  <https://github.com/andrew/typosquatting>
- ✔ **pypi-scan (IQTLabs).** PyPI typosquat scanner.
  <https://github.com/IQTLabs/pypi-scan>
- ✔ **ConfuGuard, arXiv:2502.20528 (2025).** Metadata-based detection of active
  package-confusion at scale. <https://arxiv.org/pdf/2502.20528>
- ◦ **Taylor et al., "SpellBound / typogard: Defending Against Package
  Typosquatting," 2020.** Client-side transformation checks.

*Delta:* these are mostly fixed transformation lists and/or detectors. We unify
them under one formal generator, make the registry a parameter, add the
structural and motor channels, and ship a provable edit-closure.

## Domain typosquatting (the lineage)

- ◦ **Szurdi et al., "The Long Taile of Typosquatting Domain Names," USENIX
  Security 2014.**
- ◦ **Agten et al., "Seven Months' Worth of Mistakes: A Longitudinal Study of
  Typosquatting Abuse," NDSS 2015.**
- ◦ **Nikiforakis et al., "Soundsquatting: Uncovering the Use of Homophones in
  Domain Squatting," ISC 2014.** Motivates the phonetic family.
- ◦ **Dinaburg, "Bitsquatting: DNS Hijacking without Exploitation," Black Hat
  2011.** Origin of the bitsquat family.
- ◦ **dnstwist** and ◦ **URLCrazy** — domain-name permutation engines; the
  conceptual ancestors of package permutation tools.

*Delta:* package identity (`ν_E`), scopes, and combosquatting have no clean
domain analogue; domain tools transfer only partially. We model the
package-specific structure explicitly.

## Distance metrics & foundations

- ◦ **Levenshtein 1966; Damerau 1964** — edit distance with transposition.
- ◦ **Eiter & Mannila 1994, "Computing Discrete Fréchet Distance."** Basis of the
  keyboard-trajectory channel.
- ◦ **Unicode Technical Standard #39 (UTS-39), "Unicode Security Mechanisms" —
  confusables.** Basis of the visual/homoglyph channel.
- ◦ Phonetic encodings: **Soundex; Philips, "Double Metaphone," 2000.**

*Delta:* we repurpose discrete Fréchet distance — normally a curve-similarity
measure — as a *motor-confusability* metric over keyboard trajectories, which we
believe is novel for name-confusion ranking.

## Evaluation datasets

- ✔ **ecosyste.ms typosquatting-dataset.** Curated known squat→target pairs with
  ecosystem + classification; primary recall/ranking benchmark.
  <https://github.com/ecosyste-ms/typosquatting-dataset>

---

### Sources confirmed during research (June 2026)

- Neupane et al., USENIX Security 2023 — <https://www.usenix.org/system/files/usenixsecurity23-neupane.pdf>
- ConfuGuard, arXiv:2502.20528 — <https://arxiv.org/pdf/2502.20528>
- GuardDog — <https://securitylabs.datadoghq.com/articles/guarddog-identify-malicious-pypi-packages/>
- typomania — <https://github.com/rustfoundation/typomania>
- andrew/typosquatting — <https://github.com/andrew/typosquatting>
- ecosyste.ms typosquatting-dataset — <https://github.com/ecosyste-ms/typosquatting-dataset>
- pypi-scan — <https://github.com/IQTLabs/pypi-scan>
- PyPI name normalization (PEP 503) — <https://packaging.python.org/en/latest/specifications/name-normalization/>

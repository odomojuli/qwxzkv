# Brutal gap analysis: where this paper gets attacked

Adversarial read of the qwxzkv / `typosquat` paper as drafted in `outline.md`,
`formalization.md`, and `taxonomy.md`, against the July 2026 threat evidence in
`threat-landscape.md`. Written to be useful, not kind. This is what a hostile USENIX
/ CCS reviewer does to the paper as it stands, followed by what actually survives.

---

## Verdict in one paragraph

The engineering is strong and the core model is genuinely good. The paper is at risk
on two fronts that are both fixable and both fatal if ignored. First, "completely
comprehensive" is falsified on contact: slopsquatting (the single most-written-about
package-confusion topic of 2025-2026) is distinct from real names by construction and
your marquee theoretical result, a provable Damerau-Levenshtein k-ball closure, cannot
reach it. Second, the evaluation is underpowered to the point of being indefensible:
the primary labeled corpus is 143 pairs with a single crates.io row. Fix the framing
and the eval and this is a solid applied-security paper built on one real idea (the
ecosystem-parametric identity model). Leave them and it gets desk-rejected or shredded
in reviews.

---

## Claim by claim (the five contributions in outline.md)

**Contribution 1, ecosystem-parametric identity (nu_E).** This is your real novelty
and the spine of the paper. Keep it, lead with it. The clean move is
identity-exclusion as the generator gate: the same transform fires on npm and stays
silent on PyPI with no special-casing. That is a genuine idea, not engineering
dressing. Only exposure: a reviewer calls normalization handling "just implementing
PEP 503." Rebut with the per-registry recall delta on separator and scope families
(section: eval), where registry-blind tools produce false candidates or miss real
ones. Defensible.

**Contribution 2, generate/score separation plus comprehensiveness.** The separation
is correct and well-argued; the critique of edit-distance-as-generator is right and
you now have concrete foils (GuardDog: short Levenshtein to top-5000 or a two-char
swap; pypi-scan: Levenshtein <= 1 plus Metaphone; both real, both cite-able). The
comprehensiveness claim is where you bleed. Two problems. (a) It is provable only for
the edit channel, which the 2024-2026 corpus shows is the *least* important channel
empirically. (b) Your empirical coverage is "maps every Neupane 2023 category," but
Neupane predates slopsquatting, so mapping a 2023 taxonomy is not comprehensiveness in
2026. Reframe to a defensible tri-part claim: provably complete for the edit channel,
empirically complete against the Neupane taxonomy, and explicitly bounded (with a named
frontier: combosquat affix-openness, semantic, slopsquat) everywhere else. Honesty here
is strength; overclaim here is death.

**Contribution 3, the keyboard-Frechet motor metric.** Your weakest contribution and
your most exposed. Brutal points, in order. The corpus gives zero evidence that "motor
confusability" explains real squats better than plain keyboard-adjacency, which you
already have as a generator family. "Novel to our knowledge" invites a reviewer to
surface prior visual/keyboard-distance work in dnstwist, URLCrazy, and the domain
literature and then dismiss the whole paper as unaware of its field. The Frechet-vs-DTW
discussion is in-the-weeds and no reviewer cares unless it changes a result. Most
likely the ablation shows Frechet adds little over Damerau-Levenshtein plus
keyboard-adjacency. Recommendation: demote it from a headline contribution to one
scored channel evaluated honestly in the ablation. If it wins on the labeled set,
claim it modestly. If it loses, cut it and lose nothing. Do not let the paper's
identity ride on the metric the project brief happened to name.

**Contribution 4, reproducible dual-language artifact.** Good and low-risk, but at
USENIX a clean artifact is table stakes, not a contribution. Keep the Rust-parity and
determinism as engineering merit and artifact-evaluation fodder; do not pad the
contributions list with it. A reviewer who sees a five-item contributions list where
item four is "we wrote tests" discounts the other four.

**Contribution 5, evaluation on real corpora.** The whole ballgame and currently the
thinnest section. The ecosyste.ms typosquatting-dataset is exactly 143 labeled
mappings (PyPI 95, npm 35, Go 8, GitHub Actions 4, crates.io 1). You cannot claim
comprehensiveness or cross-ecosystem generality on a set with one crates.io row.
Backstabber's is 174 packages, access-restricted, and mostly not typosquats. This must
be rebuilt (see priorities). And recall is only half of it: ConfuGuard exists because
pure lexical name-confusion runs ~80% false positives, so a generator that enumerates
the whole edit ball plus structural families produces huge candidate sets. Without a
precision / false-positive analysis against that ~80% baseline, the blocklisting and
triage use cases are unsubstantiated and a reviewer will say so.

---

## Three structural problems above the level of any single claim

**1. "Completely comprehensive" is a liability, not a selling point.** It is in the
project instructions and the README-level framing. You already concede combosquatting
is unbounded, homophone/semantic is open-ended, and slopsquatting is out of model.
Those concessions plus the word "comprehensive" is a contradiction a reviewer will
quote back to you. Purge "all possible typos" and "completely comprehensive" from the
paper and the README. Replace with the tri-part framing. You lose a marketing line and
gain credibility.

**2. Motivation-versus-impact mismatch.** The Introduction motivates with "the
supply-chain threat," but the highest-impact incidents (chalk/debug at 2.6B weekly
downloads, Shai-Hulud, ua-parser-js, event-stream) are account compromise and
maintainer phishing that no name generator prevents. If the intro even implies name
enumeration would have helped there, a reviewer torpedoes the framing. Own the trade
explicitly: name confusion is the high-frequency, low-per-incident-yield channel that
is uniquely defensible by pre-registration and triage, it concentrates on crypto/Web3
and AI targets, and that is the class this tool addresses. Put a number on incident
frequency versus the compromise class. Claim the channel you actually defend.

**3. Dependency confusion is not a name-generation problem.** It reuses an identical
internal name on a public registry; there is nothing to enumerate without the
defender's private package list as input. Your "cross-ecosystem mode" is a reasonable
way to surface it, but the coverage matrix currently reads as if the generator
"covers" dependency confusion, and it does not. Be explicit that this class is
input-driven, and note the awkward fact that it is arguably the highest-yield
name-confusion class (Birsan's $130k+ in 2021, the resurgent 2026 Microsoft/Sberbank
wave). A tool positioned on "supply chain attacks using typosquatting" that quietly
sidesteps the highest-yield class needs to say why on purpose.

---

## Smaller but real

- **Unicode similarity is foregrounded but mostly precluded.** The brief names it; on
  npm/PyPI/crates ASCII normalization structurally blocks Unicode-confusable *name*
  collisions, and the one confirmed 2025 homoglyph case was on NuGet. Either add NuGet
  as a fourth ecosystem (where homoglyphs actually live and where your Unicode channel
  would earn its place) or reframe Unicode as a display/domain-mode feature and stop
  foregrounding it. Precision the paper must get right: capital-I-for-l and rn-for-m
  are ASCII visual confusion that survive normalization as a *distinct* name that only
  looks the same (a scoring problem the confusable-weighted metric handles), which is a
  different thing from Unicode-confusable substitution (blocked by normalization).
  Conflating them will draw a correction from any reviewer who knows the registries.

- **Scoring is uncalibrated and you know it.** Your own project memory records that
  duplications rank as high as the closest typos and the weights are untuned. The
  "ranking quality" sub-claim of contribution 5 depends entirely on fixing this. A
  reviewer who runs the artifact sees the mis-ranking immediately. Fit weights on the
  rebuilt corpus and report the before/after.

- **Novelty claims are over-extended.** "To our knowledge novel" appears for Frechet
  and gestures at the whole approach. dnstwist, URLCrazy, and ecosyste.ms already do
  structural families and visual/keyboard distance. Position the paper as unification
  plus formalization plus the identity parameter, not as first-to-do-X. Reviewers
  punish overclaimed novelty far harder than modest positioning.

- **Candidate-set explosion is unaddressed for the defensive use cases.** The full
  edit ball at k >= 2 combined with structural families is large. For pre-registration
  you register the ranked head, fine; for blocklisting/triage the set size and its
  precision matter. Report candidate-set sizes and a precision/recall curve, not just
  "we generate more candidates than prior tools," which a reviewer reads as "you
  generate more false positives."

---

## What survives and should be the spine

The ecosystem-parametric identity model (contribution 1) is the defensible core. The
generate/score separation as a principled critique of edit-distance-as-generator is
correct and now has concrete, cited foils. Rebuild the paper's spine as: a formal,
ecosystem-parametric model that unifies scattered transform lists under one generator,
plus an honest comprehensiveness account (provable edit closure, empirical Neupane
coverage, explicit slopsquat/semantic frontier), plus an evaluation that finally
measures recall AND false-positive rate on a large labeled corpus and adds a
hallucination channel. That is a real paper. The current framing ("completely
comprehensive, and here is a novel curve metric") is not.

---

## Reviewer one-liners to pre-empt (extend outline.md's reviewer-anticipation)

- "Isn't this ecosyste.ms plus a correctness proof?" Quantify the recall and precision
  delta, especially on scope/separator/dependency-confusion and the crypto cluster, and
  show the identity parameter changing which families fire per registry.
- "Your comprehensiveness excludes the thing the field is writing about in 2026." Add
  the slopsquatting channel or scope it out in one honest paragraph; do not get caught.
- "Edit-ball completeness is trivial and known." It is. Sell it as hygiene, not
  headline. The value is the identity gate and the empirical mapping, not the proof.
- "Frechet is cute but unmotivated." Ablate it honestly and be ready to cut it.
- "143 labeled pairs?" Replace the corpus before anyone counts.
- "Does this prevent attacks or just enumerate names?" Position as pre-registration
  plus triage ranking; report how high real squats rank (recall@k) and the FP cost of
  getting there.

---

## Priority order before submission

1. Delete "completely comprehensive" / "all possible typos" everywhere; adopt the
   tri-part comprehensiveness framing.
2. Rebuild the evaluation corpus from DataDog (17,367 human-vetted), lxyeternal
   (~10k), OSSF malicious-packages, and IntelliRadar (34,313); report recall@k AND
   false-positive rate against the ConfuGuard ~80% lexical baseline; over-sample the
   crypto/Web3 and AI cluster where attacks concentrate.
3. Add a slopsquatting channel seeded and evaluated on the 205,474-name
   Spracks/PackageHallucination corpus, or scope it out explicitly. The channel is the
   stronger paper and aligns with the roadmap's semantic-plausibility-prior note.
4. Demote keyboard-Frechet to an ablated channel; let the labeled set decide whether
   it lives.
5. Fix scoring calibration (duplication over-ranking; fit weights on the new corpus).
6. Reframe dependency confusion as input-driven rather than generated; state plainly
   that it is the highest-yield class and requires the defender's private name list.
7. Fold in the citation corrections and add Ladisa et al., "SoK: Taxonomy of Attacks
   on Open-Source Software Supply Chains," IEEE S&P 2023 (a 107-node taxonomy the draft
   omits and a reviewer will expect).

Sources for every factual claim here are in `threat-landscape.md`.

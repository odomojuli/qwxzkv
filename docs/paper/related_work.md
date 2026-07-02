# Related work (draft)

Grouped by theme, with where **this** work differs. Metadata (authors, venue, year,
pages, DOI/URL) was verified against proceedings, dblp, and arXiv in July 2026.
Entries still needing a check before camera-ready are marked **[verify]**. Full
attack-corpus context and the source for every claim is in
`../research/threat-landscape.md`; the adversarial gap analysis is in
`../research/critique.md`.

## Package-confusion measurement & taxonomy

- **Neupane, Holmes, Wyss, Davidson, De Carli, "Beyond Typosquatting: An In-depth
  Look at Package Confusion," USENIX Security 2023, pp. 3439-3456.** Defines **13**
  categories of package confusion (12 target-based + targetless Familiar term abuse) over
  **1232** documented attacks (integer resolved; the released artifact reports 1,239
  confirmed pairs). Distribution is campaign-skewed: 722/1232 are one RubyGems delimiter
  campaign; 1077/1232 fall in 7 campaigns. Rules 1-11 (semantic-leaning) are 82% of labels,
  43% excluding the RubyGems campaign. Our empirical coverage target; see
  `../research/measurement-methodology.md` for the category-by-category mapping and the
  three categories our generator deliberately does not reach.
  <https://www.usenix.org/conference/usenixsecurity23/presentation/neupane>
- **Vu, Pashchenko, Massacci, Plate, Sabetta, "Typosquatting and Combosquatting
  Attacks on the Python Ecosystem," IEEE EuroS&PW 2020, pp. 509-514.** PyPI-focused
  measurement; motivates the structural families.
  <https://doi.org/10.1109/EuroSPW51379.2020.00074>
- **Zimmermann, Staicu, Tenny, Pradel, "Small World with High Risks: A Study of
  Security Threats in the npm Ecosystem," USENIX Security 2019, pp. 995-1010.**
  Ecosystem-scale risk; transitive-dependency exposure.
  <https://www.usenix.org/system/files/sec19-zimmermann.pdf>
- **Ohm, Plate, Sykosch, Meier, "Backstabber's Knife Collection: A Review of Open
  Source Software Supply Chain Attacks," DIMVA 2020, LNCS 12223, pp. 23-43.** The
  174-package malicious dataset; a ranking-evaluation source.
  <https://doi.org/10.1007/978-3-030-52683-2_2>
- **Duan, Alrawi, Kasturi, Elder, Saltaformaggio, Lee, "Towards Measuring Supply
  Chain Attacks on Package Managers for Interpreted Languages" (MalOSS), NDSS 2021.**
  Cross-ecosystem measurement pipeline (npm, PyPI, RubyGems).
  <https://www.ndss-symposium.org/ndss-paper/towards-measuring-supply-chain-attacks-on-package-managers-for-interpreted-languages/>
- **Ladisa, Plate, Martinez, Barais, "SoK: Taxonomy of Attacks on Open-Source
  Software Supply Chains," IEEE S&P 2023, pp. 1509-1526.** A 107-node attack
  taxonomy that situates name confusion within the broader supply-chain surface;
  reviewers will expect it. <https://doi.org/10.1109/SP46215.2023.10179304>

*Delta:* prior work largely measures and classifies observed attacks. We provide a
generative model that enumerates the candidate space ahead of attack, with a
comprehensiveness argument tied to the Neupane taxonomy and an explicit account of
what lies beyond it (the hallucination channel below).

## Detection tools

- **GuardDog (Datadog).** Static analysis plus a typosquatting heuristic: flags a
  name at short Levenshtein distance to a top-N popular list (Datadog's writeup says
  top 5,000) or with a two-character swap. Practical detector, narrow
  edit-distance-only generator (no combosquat, scope, or hallucination).
  <https://securitylabs.datadoghq.com/articles/guarddog-identify-malicious-pypi-packages/>
- **typomania (Rust Foundation).** Typosquatting primitives (bitflip, omission,
  repetition, transposition, delimiter, version-suffix); a port of the typogard
  transforms. Homoglyph and keyboard maps must be supplied by the integrator (it
  ships none). Powers crates.io detection.
  <https://github.com/rustfoundation/typomania>
- **andrew/typosquatting (ecosyste.ms).** The broadest open-source generator (16
  algorithms including homoglyph, vowel-swap, delimiter, word-order, plural, and a
  fixed-suffix combosquat), multi-ecosystem, with existence checks. Still
  edit-anchored, so no hallucination coverage by construction.
  <https://github.com/andrew/typosquatting>
- **pypi-scan (IQTLabs).** PyPI typosquat scanner: Levenshtein <= 1 plus a Metaphone
  phonetic check. Archived January 2023.
  <https://github.com/IQTLabs/pypi-scan>
- **ConfuGuard (Jiang, Cakar, Lysenko, Davis; Purdue + Socket), arXiv:2502.20528 (v3).**
  Metadata-based detection of active *and stealthy* package confusion across 7 registries.
  Adds a benignity filter (15 metadata rules, LLM-as-Judge on o4-mini) that cuts the
  false-positive rate of pure name-similarity flagging **from 79.9% to 28%** (the 79.9%
  is the benign fraction of a manual sample from Neupane's 640,482 flagged pairs, NPM/
  PyPI/RubyGems — not a 7-registry figure). Extends Neupane's taxonomy with 3 hierarchical
  patterns (impersonation, compound, domain confusion); releases ConfuDB (2,361 triaged
  threats); 630 attacks confirmed in Socket production. Name evolution: v1 **TypoSmart** ->
  v2/v3 ConfuGuard. arXiv-only as of July 2026. <https://arxiv.org/abs/2502.20528>
- **Taylor, Vaidya, Davidson, De Carli, Rastogi, "SpellBound / typogard: Defending
  Against Package Typosquatting," arXiv:2003.03471 (2020).** Client-side
  transformation checks with a popularity gate; reports a 0.5% false-positive rate.
  <https://arxiv.org/abs/2003.03471>

*Delta:* these are mostly fixed transformation lists and/or detectors. We unify them
under one formal generator, make the registry a parameter, add the structural and
motor channels, ship a provable edit-closure, and (see below) treat the FP rate as a
first-class evaluation axis rather than an afterthought.

## Slopsquatting / LLM package hallucination

- **Lanyado (Vulcan Cyber, 2023), "AI package hallucination."** First demonstration
  that code LLMs recommend non-existent package names; the follow-up `huggingface-cli`
  proof of concept (Lanyado, then at Lasso Security) was installed 15,000+ times.
  <https://www.lasso.security/blog/ai-package-hallucinations>
- **"Slopsquatting."** Term coined by Seth Larson (PSF), April 2025; popularized by
  Andrew Nesbitt. Registering a name an LLM hallucinates so an AI-assisted developer
  installs it.
- **Spracklen, Wijewickrama, A.H.M. Nazmus Sakib, Maiti, Viswanath, Jadliwala, "We
  Have a Package for You! A Comprehensive Analysis of Package Hallucinations by
  Code-Generating LLMs," USENIX Security 2025.** 16 models, 576,000 samples;
  hallucination rate ~5.2% commercial / ~21.7% open-source; 205,474 unique
  hallucinated names; 58% repeat across runs. Crucially, most hallucinated names are
  distinct from real names (only 0.17% match deleted PyPI packages), so they are not
  reachable by an edit-distance generator. Public corpus at
  <https://github.com/Spracks/PackageHallucination>. Paper:
  <https://arxiv.org/abs/2406.10279>

*Delta:* this is a target class our provable edit-ball closure cannot reach. We add a
hallucination channel seeded and evaluated on the Spracklen corpus (taxonomy.md,
Channel E), which no prior name-generation tool includes.

## Domain typosquatting (the lineage)

- **Szurdi, Kocso, Cseh, Spring, Felegyhazi, Kanich, "The Long 'Taile' of
  Typosquatting Domain Names," USENIX Security 2014, pp. 191-206.**
  <https://www.usenix.org/conference/usenixsecurity14/technical-sessions/presentation/szurdi>
- **Agten, Joosen, Piessens, Nikiforakis, "Seven Months' Worth of Mistakes: A
  Longitudinal Study of Typosquatting Abuse," NDSS 2015.**
- **Nikiforakis, Balduzzi, Desmet, Piessens, Joosen, "Soundsquatting: Uncovering the
  Use of Homophones in Domain Squatting," ISC 2014, LNCS 8783, pp. 291-308.**
  Motivates the phonetic family. (Distinct venue from Bitsquatting below.)
- **Nikiforakis, Van Acker, Meert, Desmet, Piessens, Joosen, "Bitsquatting:
  Exploiting Bit-Flips for Fun, or Profit?," WWW 2013, pp. 989-998.**
- **Dinaburg, "Bitsquatting: DNS Hijacking without Exploitation," Black Hat USA
  2011.** Origin of the bitsquat family. **[verify]** the media URL (use Wayback if
  it 404s).
- **Moore, Edelman, "Measuring the Perpetrators and Funders of Typosquatting," FC
  2010, LNCS 6052, pp. 175-191.** Typosquatting economics.
- **dnstwist** and **URLCrazy**: domain-name permutation engines, the conceptual
  ancestors of package permutation tools.

*Delta:* package identity (`ν_E`), scopes, and combosquatting have no clean domain
analogue; domain tools transfer only partially. We model the package-specific
structure explicitly, and we do not overclaim novelty for keyboard/visual distance
(the domain lineage used both), positioning our contribution as unification plus the
ecosystem-parametric identity model.

## Distance metrics & foundations

- **Levenshtein 1966,** "Binary Codes Capable of Correcting Deletions, Insertions,
  and Reversals," Soviet Physics Doklady 10(8):707-710 (no DOI); **Damerau 1964,**
  CACM 7(3):171-176, <https://doi.org/10.1145/363958.363994>. Edit distance with
  transposition.
- **Eiter, Mannila 1994, "Computing Discrete Fréchet Distance,"** TU Wien technical
  report CD-TR 94/64 (a technical report, not a conference/journal; no DOI). Basis of
  the keyboard-trajectory channel.
- **Unicode Technical Standard #39 (UTS-39), "Unicode Security Mechanisms."** Cite
  editors (Davis, Suignard) and the revision used. Basis of the visual/homoglyph
  channel (relevant chiefly where names are not ASCII-normalized, e.g. NuGet and
  domains).
- **Philips, "The Double Metaphone Search Algorithm," C/C++ Users Journal 18(6):38-43,
  2000** (print, no DOI); Soundex as the phonetic-encoding predecessor.

*Delta:* we repurpose discrete Fréchet distance, normally a curve-similarity measure,
as a motor-confusability metric over keyboard trajectories. We evaluate it as one
ablated scoring channel rather than a headline claim, and report whether it beats
Damerau-Levenshtein plus keyboard-adjacency on the labeled set.

## Evaluation datasets

The current primary benchmark is too small to carry a comprehensiveness claim; the
evaluation draws on a union of the following.

- **ecosyste-ms/typosquatting-dataset.** 143 labeled squat-to-target pairs (PyPI 95,
  npm 35, Go 8, GitHub Actions 4, crates.io 1). Useful but small and skewed; the
  single crates.io row cannot support cross-ecosystem generality on its own.
  <https://github.com/ecosyste-ms/typosquatting-dataset>
- **DataDog/malicious-software-packages-dataset.** 17,367 human-vetted npm/PyPI
  samples, distinguishing compromised vs purpose-built.
  <https://github.com/DataDog/malicious-software-packages-dataset>
- **lxyeternal/pypi_malregistry.** ~10,000 malicious PyPI packages (ASE 2023 study),
  many typosquat variants of popular libraries.
- **ossf/malicious-packages.** OSV-format aggregate of tens of thousands of reports
  across ecosystems.
- **IntelliRadar (arXiv:2409.15049).** 34,313 malicious npm/PyPI names mined from
  unstructured intel; 7,542 absent from OSV.
- **Spracks/PackageHallucination.** 205,474 LLM-hallucinated names, the seed and eval
  set for the hallucination channel.
- **Backstabber's Knife Collection (Ohm et al. 2020).** 174 packages; access
  restricted to institutional researchers.

*Delta:* we report recall@k on real squats and, unlike prior tools, the
false-positive rate against the ~80% lexical baseline ConfuGuard documents, on a
corpus large enough (and crypto/Web3/AI-weighted enough) to matter.

## Dependency confusion (input-driven, noted for completeness)

- **Birsan, "Dependency Confusion: How I Hacked Into Apple, Microsoft and Dozens of
  Other Companies," independent disclosure, Feb 9, 2021.** Origin of the class;
  public packages shadow private internal names by version precedence. No standalone
  academic citation exists (a genuine gap; the concept lives in the SoK and
  measurement papers above). <https://medium.com/@alex.birsan/dependency-confusion-how-i-hacked-into-apple-microsoft-and-dozens-of-other-companies-4a5d60fec610>

*Delta:* dependency confusion is not a name-generation problem (it reuses an
identical internal name), so we surface it via the cross-ecosystem identity mode with
the defender's private name list as input, and say so plainly rather than implying the
generator "covers" it.

---

### Notes for camera-ready

- Resolve the three **[verify]** items: the exact Neupane attack integer, the
  Dinaburg Black Hat media URL, and the venue/year of Vu et al.'s `py2src` if cited.
- Keep LastPyMile (Vu et al., ESEC/FSE 2021) distinct from the EuroS&PW 2020 paper if
  both are cited.
- ConfuGuard has no peer-reviewed venue as of July 2026; cite as arXiv and update if
  it lands.

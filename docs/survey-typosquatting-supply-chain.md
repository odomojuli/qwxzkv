# Typosquatting in the Software Supply Chain: A State-of-the-Art Survey (2026)

*Compiled June 2026 to situate the `qwxzkv` project within the field. Balanced
academic + operational survey. Emphasis 2020–2026; seminal earlier work included
where foundational. Method: a five-angle fan-out web search with adversarial
cross-checking of load-bearing figures against ≥2 sources; contested numbers and
single-source estimates are flagged inline. Primary sources (peer-reviewed
papers, registry advisories, first-party vendor research) were prioritized over
secondary reporting.*

> **Reading the numbers.** The single most important caveat in this field:
> "malicious package" counts are not comparable across vendors. Sonatype counts
> automated spam and token-farming uploads as malicious and reports **hundreds of
> thousands per year** [52, 53]; ReversingLabs counts *functionally malicious*
> packages and reports **~11,200 across npm/PyPI/RubyGems for 2023** [54] — two to
> three orders of magnitude lower. Download counts (e.g., NuGet's "166K" [46], the
> npm crossenv "700" [36]) are routinely inflated by bots, mirrors, and scanners
> and are **not** victim counts. Treat large figures as telemetry, not impact.

---

## 1. Scope and definitions

**Typosquatting** is the registration of a name deliberately confusable with a
legitimate one so that a human or a build tool selects the malicious artifact.
The modern literature treats classic typosquatting as one member of a broader
family that Neupane et al. call **package confusion** [1]: typosquatting
(misspellings), **combosquatting** [7] (adding words, `lodash` → `lodash-js`),
**delimiter/separator** modification (`-`↔`_`↔`.`), **scope/namespace** confusion,
**sequence/word-order** swaps, **homoglyph/homophone** substitution, and
**dependency confusion** (an *identical* internal name re-registered publicly).
The unifying mechanism is *the name itself* inducing the wrong artifact to be
installed — distinguishing these attacks from code-injection, account-compromise,
or build-system attacks, which the SoK literature catalogs separately [2, 4].

The threat now spans every channel where a name resolves to code: package
registries (npm, PyPI, RubyGems, crates.io, NuGet, Maven, Go) [1, 3], container
registries (Docker Hub) [8], IDE/editor extension marketplaces (VS Code, Open
VSX) [59, 60], browser-extension stores [62], malicious mirrors and fake
registries [58], and — by contrast — mutable-reference attacks on CI systems such
as GitHub Actions [63], which are *not* typosquatting but exploit the same
"developers trust a name/tag" assumption.

---

## 2. Academic state of the art

### 2.1 Measurement and taxonomy

The field's anchor paper is **Neupane et al., "Beyond Typosquatting: An In-Depth
Look at Package Confusion" (USENIX Security 2023)** [1]. From **1,232 documented
attacks** across npm, PyPI, and RubyGems they derive **13 categories** of
confusion and show that many attacks operate **semantically**, not just at the
character level (e.g., `meta-llama` vs `facebook-llama`), which pure edit distance
cannot catch. Their corpus is heavily campaign-skewed — **722 of the 1,232** come
from a single RubyGems campaign — a caveat for anyone treating the distribution as
representative [1].

Two systematizations frame the wider problem space. **Ladisa et al., "SoK:
Taxonomy of Attacks on Open-Source Software Supply Chains" (IEEE S&P 2023)** [2]
builds an attack tree of **107 vectors** linked to **94 real incidents** and **33
safeguards**, validated by **17 domain experts and 134 developers**. **Okafor et
al. (SoK, 2024)** [10] reframes the same space around three secure-design
properties — transparency, validity, and separation.

Earlier empirical foundations remain load-bearing. **Duan et al. (MalOSS, NDSS
2021)** [3] scanned **>1,000,000 packages** and flagged **7 (PyPI), 41 (npm), 291
(RubyGems)** malicious ones, **>82% of which were removed** after disclosure.
**Ohm et al., "Backstabber's Knife Collection" (DIMVA 2020)** [4] manually
dissected **174 malicious packages** (Nov 2015–Nov 2019), concluding that package
repositories are the most-targeted surface, predominantly via **typosquatting and
account compromise**. **Zimmermann et al. (USENIX Security 2019)** [5] showed npm's
structural fragility: a handful of maintainer accounts can reach a *majority* of
all packages — the blast-radius argument that makes squatting popular packages so
valuable.

### 2.2 Datasets and benchmarks

Reproducible evaluation has matured but remains fragmented:

- **Backstabber's Knife Collection** — 174 curated malicious packages in the
  original paper; the live dataset has since grown by integrating others [4].
- **MalOSS** — the Duan et al. labeled set and vetting pipeline [3].
- **ecosyste.ms typosquatting-dataset** — **143 confirmed squat→target mappings**
  with a **17-class taxonomy** (omission, repetition, replacement, transposition,
  addition, homoglyph, vowel-swap, delimiter, word-order, plural, bitsquatting,
  combosquatting, …); by ecosystem PyPI 95 / npm 35 / Go 8 / GitHub Actions 4 /
  crates 1 [15].
- **Datadog malicious-software-packages-dataset** — **17,367 human-vetted** npm+PyPI
  packages, separating compromised-legitimate from purpose-built malware [15, 74].
- **`pypi_malregistry`** (Guo et al., ASE 2023) — **~10,000 malicious PyPI
  packages**, many typosquats of `requests`/`PyTorch`/`BeautifulSoup` [9].
- **OpenSSF `ossf/malicious-packages`** — launched **12 Oct 2023**, OSV-format,
  consumable via OSV.dev/OSV-Scanner/deps.dev; **~35,000 reports** by Aug 2025
  *(growing; point-in-time est.)* [14].
- **IntelliRadar** (arXiv, 2024) compiled **34,313 malicious npm+PyPI names** and
  found **7,542 absent from OSV** and **12,684 absent from Snyk** — direct evidence
  that **no single dataset is complete** [13].

---

## 3. Detection and candidate-generation methods

### 3.1 The two-stage structure

Effective systems separate **candidate generation** (enumerate confusable names —
recall-oriented) from **scoring/filtering** (rank or classify — precision-oriented).
Generation operators, drawn from the taxonomy above, include edit operations
(omission, insertion, duplication, transposition), **keyboard/QWERTY-adjacent**
substitution, **homoglyph/visual** substitution, **phonetic/homophone** rules,
delimiter and word-order manipulation, and **bitsquatting** [15, 18, 24].

### 3.2 Distance and similarity metrics

- **Edit distance** (Levenshtein / Damerau-Levenshtein) is the workhorse but is
  *length-biased and misses semantic squats*; **18 of 40** historical PyPI
  typosquats sat within Levenshtein ≤2 of their target, motivating — but also
  complicating — registration-time blocking [18, 73].
- **q-gram / Jaccard** overlap gives order-insensitive lexical similarity and a
  cheap blocking key.
- **Phonetic** (Soundex/Metaphone) and **QWERTY-distance** checks power tools like
  IQTLabs' `pypi-scan` [24].
- **Visual/Unicode confusables** are standardized by **Unicode UTS-39**, whose
  *skeleton* algorithm maps each character to a confusable representative
  (`confusables.txt`, on the order of thousands of mappings — exact figure
  *contested* across secondary sources) [16].
- **Name embeddings / ML.** Neupane et al. introduced **FastText embeddings** for
  semantic name comparison [1]; **ConfuGuard** (arXiv 2502.20528, 2025) replaces
  plain Levenshtein with a **fine-tuned name-embedding** nearest-neighbor search
  and adds **metadata-based benignity filtering**, cutting false-positive rates
  from **~80% to 28%** (a 52% relative improvement) at ~6.8 s/package across **seven
  registries**, with **630 confirmed attacks** in production [11]. *(This work also
  circulated under the title "TypoSmart"; same arXiv ID — treat as one paper.)*
- **Damerau-Levenshtein extensions.** Truong et al., "You Can't Touch This" (NSS
  2024) report **98.4% accuracy** on a 394-package dataset (93.5–96.0% on external
  sets) [12].

### 3.3 The false-positive problem

At registry scale, naive distance thresholds drown defenders in false positives;
Microsoft's OSSGadget authors name FP reduction as the open problem [23], and
ConfuGuard's central contribution is precisely lowering it with metadata [11].
This is why production detectors layer **popularity priors** (only compare against
"trusted"/high-traffic targets) onto similarity — e.g., ConfuGuard's **5,000
weekly-downloads** trust threshold [11] and GuardDog's comparison against the
**top-5,000** packages [19].

### 3.4 Evaluation

The strongest detector results to date: **SpellBound/TypoGard** (Taylor et al.,
2020) flags up to **99.4%** of known typosquats at a **0.5% warning rate** and
**2.5%** install-time overhead by combining lexical similarity with popularity
[6]; ConfuGuard's 28% FP and 630 confirmed catches [11]; Truong et al.'s 98.4%
accuracy [12]. Cross-comparison remains hard because datasets, ecosystems, and the
generation vs. detection boundary differ between papers.

### 3.5 Tooling landscape

| Tool | Owner | Ecosystems | Approach |
|------|-------|-----------|----------|
| **GuardDog** [19, 74] | Datadog | PyPI, npm, Go, RubyGems, GH Actions, VS Code | Semgrep/YARA source rules + metadata; Levenshtein-to-top-5000 / 2-char swap |
| **typomania** [20, 21] | Rust Foundation | crates.io (generalizable) | Rust port of TypoGard; **powers crates.io** detection as a post-publish job |
| **ConfuGuard** [11] | academic/industry | 7 registries | fine-tuned embeddings + metadata benignity filter |
| **Socket** [22] | Socket | npm, PyPI, … | behavioral/code analysis across 70+ signals; PR-time alerts |
| **OSSGadget `oss-find-squats`** [23] | Microsoft | multi | name-mutation generator |
| **pypi-scan** [24] | IQTLabs | PyPI | QWERTY distance + homophones (archived) |
| **andrew/typosquatting** [18] | ecosyste.ms | 11 ecosystems | variant generation + existence check via names API |
| **dnstwist** [25] | elceef | domains (reused) | permutation engine; IDN/homoglyph; fuzzy-hash page compare |
| **OSV.dev / OSV-Scanner** [27] | Google/OpenSSF | cross-ecosystem | downstream lookup of known-malicious/vuln IDs |
| **OpenSSF Package Analysis** [14] | OpenSSF | npm, PyPI, … | dynamic sandbox; feeds `malicious-packages` |

---

## 4. The operational threat landscape (2017–2026)

A representative, source-traced timeline. Where vendors disagree, both figures are
given; download/telemetry numbers carry the inflation caveat from the preamble.

**npm `crossenv` (Jul–Aug 2017)** — the canonical case: ~36–39 packages
typosquatting popular libs POSTed environment variables to a remote host; npm
estimated **~50 real installs** despite ~700 logged downloads [36, 37].

**RubyGems mass typosquat (Feb 2020)** — **760+ malicious gems** uploaded 16–25 Feb
with clipboard-hijacking crypto-stealers; the standout `atlas-client` (typosquat of
`atlas_client`) drew **~2,100 downloads** before removal on 27 Feb [42, 43].

**PyPI `ctx` + PHP `phpass` (May 2022)** — an expired maintainer **domain
re-registered for ~$5** enabled account takeover and backdoored releases
exfiltrating AWS/env credentials; `ctx` had been dormant since 2014 [38, 39].

**crates.io `rustdecimal` (May 2022, "CrateDepression")** — typosquat of
`rust_decimal` fetching a second-stage payload; RUSTSEC-2022-0042 [44].

**W4SP Stealer on PyPI (Nov 2022–2023)** — an initial **29 packages / >5,700
downloads** [40] grew into a months-long campaign with shifting distribution
methods [41]; an information-stealer for credentials, wallets, and Discord tokens.

**NuGet "Impala Stealer" (Mar 2023)** — JFrog's first major NuGet case: **13
typosquatted packages** running install-time PowerShell; the top three showed
**~166,000 downloads**, which JFrog itself flagged as **likely bot-inflated**
*(contested as an impact figure)* [46].

**npm registry DoS (Apr 2023)** — Checkmarx observed **>15,000** spam/phishing
packages published in hours, degrading the registry [47].

**crates.io Telegram-exfil crates (Aug 2023)** — 8 crates (`postgress`, `oncecell`,
`lazystatic`, …) sending host info to Telegram; logs showed only scanners pulled
them; removed 18 Aug [45].

**PyPI emergency lockdown (Mar 2024)** — a **500+ package** typosquat surge forced
PyPI to **temporarily suspend new project and user registration** on 27–28 Mar
[57]; a parallel campaign used a fake mirror `files.pypihosted.org` and impersonated
"official" Python sites, reportedly reaching ~170,000 users [58].

**BIPClip on PyPI (2024)** — ReversingLabs' **7 packages** targeting BIP-39 wallet
mnemonic phrases [55].

**npm "tea" token-farming flood (2024)** — incentive-driven spam: Sonatype counted
**>15,000** packages by April [48]; researchers estimated tea spam reached **~70%
of all new npm packages** at peak *(est.)*; **Amazon Inspector later attributed
>150,000 packages** to the campaign [49].

**npm Ethereum-C2 typosquats (Oct–Nov 2024)** — **287+ packages** using **Ethereum
smart contracts** to distribute C2 addresses; first flagged 31 Oct [50].

**Lazarus Group (DPRK) (2024–2026)** — recurring BeaverTail/InvisibleFerret droppers
in lookalike/typosquatted npm and PyPI packages; Sonatype attributed **234 malware
packages** to Lazarus in H1 2025 alone *(est.)* [53].

**"IndonesianFoods" npm worm (Nov 2025)** — a self-replicating token-farming worm
that published **tens of thousands** of junk packages over ~2 years (researcher
counts range **43,000–67,500+**; BleepingComputer's headline cites ~150,000) —
a vivid example of why raw counts mislead *(contested)* [51].

**Ecosystem-scale figures.** Sonatype's 2024 report logged **704,102** malicious
packages cumulatively since 2019 (**512,847** in the trailing year, +156%) [52];
its 2025 indices report **454,648** new in 2025 with **~89% concentrated in Q4** —
i.e., dominated by automated spam/worms [53]. ReversingLabs, counting functional
malware, reports the far smaller **~11,200** across npm/PyPI/RubyGems for 2023
(+28% YoY) and a **+73%** rise into 2025 with **npm ≈ 90%** of open-source malware
[54]. Datadog has open-sourced **~1,500** hand-labeled samples and finds **>80% of
malicious PyPI packages** abuse `setup.py`/`setup()` for install-time execution
[74].

---

## 5. Dependency confusion and namespace attacks

Disclosed by **Alex Birsan on 9 Feb 2021** [28], dependency confusion uploads a
package to a **public** registry under the **exact name** of a target's **private
internal** package; hybrid resolvers (e.g., pip's `--extra-index-url` picking the
**highest version** regardless of source) then fetch the attacker's copy. Birsan
achieved code execution at **35+ organizations** — Apple, Microsoft, PayPal,
Shopify, Netflix, Yelp, Uber, Tesla — with **~75% of callbacks from npm**, earning
**$30,000 each from Apple, Shopify, and PayPal and $40,000 from Microsoft** (the
widely-quoted ">$130,000 total" is a press aggregation, not his stated figure)
[28].

It differs from typosquatting in that **no human typo is needed** — resolution
logic does the work — which is why it is grouped under package confusion [1, 28].
The most consequential real instance was **`torchtriton`** (PyTorch-nightly, 25–30
Dec 2022): a malicious PyPI package shadowed the one shipped on PyTorch's own index,
and because **PyPI took precedence** pip installed the malicious copy, which
exfiltrated host data via DNS; the fix renamed the dependency to `pytorch-triton`
and registered a placeholder [31, 32]. Campaigns targeting Amazon, Zillow, Lyft,
and Slack followed in 2021 [35], and as recently as **May 2026** Microsoft found
**33 malicious npm packages** spoofing **nine organizational scopes** with
`postinstall` reconnaissance [33].

**Mitigations** (well-established, ecosystem-specific): scope-lock via `.npmrc`
(`@org:registry=…`) so a scope resolves only to the private registry [30];
prefer pip `--index-url` over `--extra-index-url` [72]; in Artifactory/Nexus use
**exclude patterns** and JFrog's **priorityResolution** to force local-first
ordering [34]; Microsoft's "3 Ways to Mitigate Risk" white paper codifies single
private feed + scoping + client-side verification [29]; Visma's `confused` tool
audits manifests for names unclaimed publicly [26].

---

## 6. Beyond packages: adjacent supply-chain channels

**Container registries.** The first systematic measurement — **Liu et al. (USENIX
Security 2022)** — found **75,312 confusable username pairs on Docker Hub** within
Damerau-Levenshtein distance 1 (119 on Quay.io), and in a 210-day IRB-approved live
experiment uploaded **~4,000 typosquatting images** that drew **>40,000 unwanted
pulls** — empirical proof users make typo-driven pulls [8]. Sysdig separately found
**>1,650 malicious Docker Hub images** (cryptominers most common) using typosquats
like `mongdb`, `ngingx`, `pytohn` [56].

**IDE/editor extensions.** Aqua demonstrated VS Code Marketplace impersonation by
typosquatting the "Dracula Official" theme (a 7M-install target), with names
differing by one character [59]; malicious VS Code extension detections rose from
**27 (2024) to 105** in the first ten months of 2025 [61]. **Open VSX** (used by
Cursor, Windsurf, VSCodium) has weaker vetting: the **GlassWorm** campaign combined
a typosquat wave (Dec 2025) with account-compromise and a ≥72-extension
transitive-dependency wave abusing `extensionDependencies` [60], and **TigerJack**
(Oct 2025) used visually-confusable names (`juanbIanco` with a capital-I) with a
reported ~$500,000 crypto loss *(single-source est.)* [61].

**Browser extensions.** An arXiv study of **5,551 AI-themed Chrome extensions**
flagged 154 previously-undetected malicious ones over nine months, with antimalware
engines catching only ~1% of store-flagged malware [62].

**CI references (contrast, not typosquatting).** The **tj-actions/changed-files**
compromise (CVE-2025-30066, 14–15 Mar 2025) retroactively repointed version **tags**
to a malicious commit, leaking secrets from **>23,000 repositories** [63]. This is
a *mutable-reference* attack, not a name squat — included because the defense
(pin Actions to a full **commit SHA**) is exactly the kind of pinning that also
blunts squatting, and because it shows the "trust a name/tag" assumption recurs
across the supply chain.

---

## 7. Defenses and standards

**Registry-side.**

- **PyPI** enforces **PEP 503 name normalization** (case-fold; treat `-`,`_`,`.` as
  equivalent), collapsing a large class of delimiter typos into one canonical name
  [17]; it launched **Trusted Publishing** (OIDC, no stored secrets) in **Apr
  2023**, adopted by **45,000+ projects** (~1 in 8 uploaded files) by 2025 and since
  copied by crates.io, RubyGems, and npm [66].
- **npm** mandated **2FA for top-100 maintainers since 1 Feb 2022** ("high-impact" =
  >1M weekly downloads or 500 dependents) [64], and since 2017 strips punctuation
  and blocks new names colliding with existing ones [65].
- **crates.io** runs **typomania** (Rust port of TypoGard) as a post-publish job
  since late 2023, catching **4 malicious crates** over ~18 months [20, 21].
- **RubyGems** added Levenshtein checks after 2020 — but attackers evaded them by
  swapping `-`/`_`, illustrating that **distance-1 heuristics miss separator
  substitution** [42].

**Developer-side.** Commit **lockfiles with integrity hashes**, set
**`ignore-scripts=true`** to cut the dominant install-time payload path, pin
dependencies, and use scoped/private registries. The limits are real: **PackageGate
(2025)** found 6 zero-days where pnpm/vlt/Bun stored HTTP-tarball dependencies
**without integrity hashes**, bypassing lockfile protection [68].

**Standards & initiatives.** **OpenSSF** anchors the ecosystem — **Scorecard**
(~18–20 automated checks) [71], **Package Analysis** (dynamic malware sandboxing), and
the **`malicious-packages`/OSV** feed [14, 27]. **SLSA** defines build-provenance
levels (L1–L3) [69]; **Sigstore** (cosign + Fulcio + Rekor transparency log)
provides keyless signing [70]; Microsoft's **S2C2F**, contributed to OpenSSF in
2022, defines 8 practices for securely *consuming* OSS [67]. None of these directly
*prevent* typosquatting, but they raise the cost of weaponizing a successful squat
and shrink the window of undetected abuse.

---

## 8. Open problems and research gaps

1. **Semantic and structural squats** (combosquatting, scope, word-order) defeat
   edit-distance generators; embedding- and metadata-based methods help but are new
   and not yet independently reproduced at scale [1, 11].
2. **False positives at registry scale** remain the gating constraint on
   registration-time blocking [11, 23].
3. **Ecosystem-parametric correctness.** Name *identity* differs per registry
   (PyPI collapses `-_.`; crates unifies `-`/`_`; npm keeps them distinct), so a
   detector tuned on one registry mis-fires on another — under-treated in the
   literature and a motivation for the `qwxzkv` framework.
4. **Metric incommensurability.** No shared benchmark spans generation *and*
   detection; reported precision/recall use different datasets [6, 11, 12].
5. **Beyond packages.** Container, extension-marketplace, and browser-store
   squatting are under-measured relative to npm/PyPI [8, 60, 62].
6. **Counting methodology.** "Malicious package" tallies conflate spam/token-farming
   with weaponized malware, inflating headline numbers by 100–1000× [52, 53, 54].

---

## 9. Methodology and confidence notes

Built via a five-angle parallel web search (academic foundations; detection methods
& tooling; real-world campaigns; dependency confusion; beyond-packages channels &
defenses), with load-bearing figures cross-checked against ≥2 sources. **High
confidence:** Neupane's 1,232/13 [1]; Ladisa's 107/94/33 [2]; MalOSS removal rates
[3]; Birsan's date and bounty structure [28]; npm's 2022 2FA rule [64]; PyPI
Trusted Publishing adoption [66]; the Docker Hub measurement [8]. **Flagged
estimate/contested:** all download/telemetry counts (bot inflation); Sonatype vs.
ReversingLabs scale figures (methodology); IndonesianFoods package count; the
TigerJack ~$500K loss (single source); ConfuGuard↔"TypoSmart" title identity
(inference); UTS-39 confusable-table size (secondary). Several preprints (ConfuGuard,
IntelliRadar, Okafor SoK) await or have recently completed peer review; cite with
care.

---

## Bibliography

1. Neupane, Holmes, Wyss, Davidson, De Carli. *Beyond Typosquatting: An In-Depth Look at Package Confusion.* USENIX Security 2023. https://www.usenix.org/system/files/usenixsecurity23-neupane.pdf
2. Ladisa, Plate, Martinez, Barais. *SoK: Taxonomy of Attacks on Open-Source Software Supply Chains.* IEEE S&P 2023. https://arxiv.org/abs/2204.04008
3. Duan, Alrawi, Kasturi, Elder, Saltaformaggio, Lee. *Towards Measuring Supply Chain Attacks on Package Managers for Interpreted Languages (MalOSS).* NDSS 2021. https://arxiv.org/abs/2002.01139
4. Ohm, Plate, Sykosch, Meier. *Backstabber's Knife Collection: A Review of Open Source Software Supply Chain Attacks.* DIMVA 2020. https://arxiv.org/abs/2005.09535
5. Zimmermann, Staicu, Tenny, Pradel. *Small World with High Risks: A Study of Security Threats in the npm Ecosystem.* USENIX Security 2019. https://www.usenix.org/system/files/sec19-zimmermann.pdf
6. Taylor, Vaidya, Davidson, De Carli, Rastogi. *SpellBound: Defending Against Package Typosquatting (TypoGard).* 2020. https://arxiv.org/abs/2003.03471
7. Vu, Pashchenko, Massacci, Plate, Sabetta. *Typosquatting and Combosquatting Attacks on the Python Ecosystem.* IEEE EuroS&PW 2020. https://ieeexplore.ieee.org/document/9229803
8. Liu, Gao, Wang, Sun. *Exploring the Unchartered Space of Container Registry Typosquatting.* USENIX Security 2022. https://www.usenix.org/conference/usenixsecurity22/presentation/liu-guannan
9. Guo et al. *An Empirical Study of Malicious Code in PyPI (pypi_malregistry).* ASE 2023. https://github.com/lxyeternal/pypi_malregistry
10. Okafor, Schorlemmer, Torres-Arias, Davis. *SoK: Analysis of Software Supply Chain Security by Establishing Secure Design Properties.* 2024. https://arxiv.org/abs/2406.10109
11. *ConfuGuard: Using Metadata to Detect Active and Stealthy Package Confusion Attacks Accurately and at Scale.* arXiv:2502.20528, 2025. https://arxiv.org/abs/2502.20528
12. Truong, Gardner, et al. *You Can't Touch This (Damerau-Levenshtein typosquat detection).* NSS 2024. https://link.springer.com/chapter/10.1007/978-981-96-3531-3_8
13. *IntelliRadar: Pinpointing Malicious Package Information from Cyber Intelligence.* arXiv:2409.15049, 2024. https://arxiv.org/abs/2409.15049
14. OpenSSF. *ossf/malicious-packages (OSV-format malicious-package DB).* 2023–. https://github.com/ossf/malicious-packages · launch: https://openssf.org/blog/2023/10/12/introducing-openssfs-malicious-packages-repository/
15. ecosyste.ms (Nesbitt). *typosquatting-dataset.* 2025. https://github.com/ecosyste-ms/typosquatting-dataset
16. Unicode Consortium. *UTS #39: Unicode Security Mechanisms (confusables / skeleton).* https://www.unicode.org/reports/tr39/
17. Python Packaging Authority. *PEP 503 / Name Normalization.* https://peps.python.org/pep-0503/ · https://packaging.python.org/en/latest/specifications/name-normalization/
18. Nesbitt. *Typosquatting in Package Managers.* 2025. https://nesbitt.io/2025/12/17/typosquatting-in-package-managers.html
19. Datadog. *GuardDog.* https://github.com/DataDog/guarddog · https://securitylabs.datadoghq.com/articles/guarddog-identify-malicious-pypi-packages/
20. Rust Foundation. *typomania.* https://github.com/rustfoundation/typomania
21. Alpha-Omega. *Package typosquatting detection in {Rust,Dust,Trust,Rut}.* 2025. https://alpha-omega.dev/blog/package-typosquatting-detection-in-rustdusttrustrut/
22. Socket. *How Socket Combats Typosquatting.* https://socket.dev/blog/how-socket-combats-insidious-typosquatting-supply-chain-attacks
23. Microsoft. *OSSGadget (oss-find-squats).* https://github.com/microsoft/OSSGadget
24. IQTLabs. *pypi-scan.* https://github.com/IQTLabs/pypi-scan
25. elceef. *dnstwist.* https://github.com/elceef/dnstwist
26. Visma Product Security. *confused.* https://github.com/visma-prodsec/confused
27. Google / OpenSSF. *OSV.dev and OSV-Scanner.* https://osv.dev/
28. Birsan. *Dependency Confusion: How I Hacked Into Apple, Microsoft and Dozens of Other Companies.* 2021. https://medium.com/@alex.birsan/dependency-confusion-4a5d60fec610
29. Microsoft. *3 Ways to Mitigate Risk When Using Private Package Feeds.* 2021. https://azure.microsoft.com/en-us/resources/3-ways-to-mitigate-risk-using-private-package-feeds/
30. GitHub Security Blog. *Avoiding npm substitution attacks.* 2021. https://github.blog/security/supply-chain-security/avoiding-npm-substitution-attacks/
31. PyTorch. *Compromised PyTorch-nightly dependency chain (torchtriton).* 2022. https://pytorch.org/blog/compromised-nightly-dependency/
32. Wiz. *Malicious PyTorch dependency 'torchtriton' on PyPI.* 2023. https://www.wiz.io/blog/malicious-pytorch-dependency-torchtriton-on-pypi-everything-you-need-to-know
33. Microsoft Security Blog. *33 malicious npm packages abuse dependency confusion.* 2026. https://www.microsoft.com/en-us/security/blog/2026/05/29/33-malicious-npm-packages-abuse-dependency-confusion-profile-developer-environments/
34. JFrog. *Going Beyond Exclude Patterns: Safe Repositories With Priority Resolution.* https://jfrog.com/blog/going-beyond-exclude-patterns-safe-repositories-with-priority-resolution/
35. BleepingComputer. *Malicious npm packages target Amazon, Slack with new dependency attacks.* 2021. https://www.bleepingcomputer.com/news/security/malicious-npm-packages-target-amazon-slack-with-new-dependency-attacks/
36. npm Inc. *crossenv malware on the npm registry.* 2017. https://blog.npmjs.org/post/163723642530/crossenv-malware-on-the-npm-registry
37. The Register. *This typosquatting attack on npm went undetected for 2 weeks.* 2017. https://www.theregister.com/2017/08/02/typosquatting_npm/
38. Sonatype. *PyPI Package 'ctx' and PHP Library 'phpass' Compromised.* 2022. https://www.sonatype.com/blog/pypi-package-ctx-compromised-are-you-at-risk
39. BleepingComputer. *Popular Python and PHP libraries hijacked to steal AWS keys.* 2022. https://www.bleepingcomputer.com/news/security/popular-python-and-php-libraries-hijacked-to-steal-aws-keys/
40. The Hacker News. *Researchers Uncover 29 Malicious PyPI Packages (W4SP Stealer).* 2022. https://thehackernews.com/2022/11/researchers-uncover-29-malicious-pypi.html
41. ReversingLabs. *W4SP continues to nest in PyPI.* 2022. https://www.reversinglabs.com/blog/w4sp-continues-to-nest-in-pypi-same-supply-chain-attack-different-distribution-method
42. Help Net Security. *760+ malicious packages found typosquatting on RubyGems.* 2020. https://www.helpnetsecurity.com/2020/04/17/typosquatting-rubygems/
43. ReversingLabs. *Mining for malicious Ruby gems.* 2020. https://www.reversinglabs.com/blog/mining-for-malicious-ruby-gems
44. RustSec. *RUSTSEC-2022-0042: malicious crate rustdecimal.* 2022. https://rustsec.org/advisories/RUSTSEC-2022-0042.html
45. Rust Project. *crates.io Postmortem: User Uploaded Malware.* 2023. https://blog.rust-lang.org/inside-rust/2023/09/01/crates-io-malware-postmortem/
46. JFrog. *Analysis of the First NuGet Malicious Package Attack (Impala Stealer).* 2023. https://jfrog.com/blog/impala-stealer-malicious-nuget-package-payload/
47. Help Net Security (Checkmarx). *Flood of malicious packages results in NPM registry DoS.* 2023. https://www.helpnetsecurity.com/2023/04/05/flood-of-malicious-packages-results-in-npm-registry-dos/
48. Sonatype. *Devs Flood npm with 15K Packages to Receive Tea Tokens.* 2024. https://www.sonatype.com/blog/devs-flood-npm-with-10000-packages-to-reward-themselves-with-tea-tokens
49. AWS Security Blog. *Amazon Inspector detects over 150,000 malicious packages linked to token farming.* 2024. https://aws.amazon.com/blogs/security/amazon-inspector-detects-over-150000-malicious-packages-linked-to-token-farming-campaign/
50. The Hacker News (Checkmarx). *Malware Campaign Uses Ethereum Smart Contracts to Control npm Typosquat Packages.* 2024. https://thehackernews.com/2024/11/malware-campaign-uses-ethereum-smart.html
51. BleepingComputer. *New 'IndonesianFoods' spammer floods npm with 150,000 packages.* 2025. https://www.bleepingcomputer.com/news/security/new-indonesianfoods-spammer-floods-npm-with-150-000-packages/
52. Sonatype. *2024 State of the Software Supply Chain.* 2024. https://www.sonatype.com/state-of-the-software-supply-chain/2024/scale
53. Sonatype. *Open Source Malware Index Q4 2025.* 2025. https://www.sonatype.com/blog/open-source-malware-index-q4-2025-automation-overwhelms-ecosystems
54. ReversingLabs. *2026 Software Supply Chain Security Report (73% increase).* 2026. https://www.reversinglabs.com/press-releases/reversinglabs-2026-software-supply-chain-security-report-identifies-73-increase-in-malicious-open-source-packages
55. ReversingLabs. *BIPClip: Malicious PyPI packages target crypto wallet recovery passwords.* 2024. https://www.reversinglabs.com/blog/bipclip-malicious-pypi-packages-target-crypto-wallet-recovery-passwords
56. BleepingComputer (Sysdig). *Docker Hub repositories hide over 1,650 malicious containers.* 2022. https://www.bleepingcomputer.com/news/security/docker-hub-repositories-hide-over-1-650-malicious-containers/
57. Check Point. *PyPI Inundated by Malicious Typosquatting Campaign.* 2024. https://blog.checkpoint.com/securing-the-cloud/pypi-inundated-by-malicious-typosquatting-campaign/
58. Checkmarx. *Over 170K Users Affected by Attack Using Fake Python Infrastructure.* 2024. https://checkmarx.com/blog/over-170k-users-affected-by-attack-using-fake-python-infrastructure/
59. Aqua Security. *Can You Trust Your VSCode Extensions?* 2024. https://www.aquasec.com/blog/can-you-trust-your-vscode-extensions/
60. Cloud Security Alliance Labs. *GlassWorm: Open VSX Transitive Dependency Supply-Chain Escalation.* 2026. https://labs.cloudsecurityalliance.org/research/csa-research-note-glassworm-open-vsx-transitive-dependency-a/
61. WebProNews. *How a Typosquatting Campaign Exploited Open VSX Registry (TigerJack).* 2025. https://www.webpronews.com/how-a-typosquatting-campaign-exploited-open-vsx-registry-to-compromise-developer-environments/
62. *A Study on Malicious Browser Extensions in 2025.* arXiv:2503.04292, 2025. https://arxiv.org/html/2503.04292
63. CISA. *Supply Chain Compromise of tj-actions/changed-files (CVE-2025-30066).* 2025. https://www.cisa.gov/news-events/alerts/2025/03/18/supply-chain-compromise-third-party-tj-actionschanged-files-cve-2025-30066-and-reviewdogaction
64. Borins (GitHub Blog). *Top-100 npm package maintainers now require 2FA.* 2022. https://github.blog/security/supply-chain-security/top-100-npm-package-maintainers-require-2fa-additional-security/
65. npm Blog. *New Package Moniker Rules.* 2017. https://blog.npmjs.org/post/168978377570/new-package-moniker-rules.html
66. PyPI Blog. *Introducing 'Trusted Publishers'.* 2023. https://blog.pypi.org/posts/2023-04-20-introducing-trusted-publishers/
67. Microsoft Security Blog. *Microsoft contributes S2C2F to OpenSSF.* 2022. https://www.microsoft.com/en-us/security/blog/2022/11/16/microsoft-contributes-s2c2f-to-openssf-to-improve-supply-chain-security/
68. Koi Security. *PackageGate: 6 Zero-Days in JS Package Managers.* 2025. https://www.koi.ai/blog/packagegate-6-zero-days-in-js-package-managers-but-npm-wont-act
69. OpenSSF. *SLSA — Supply-chain Levels for Software Artifacts.* https://slsa.dev/
70. Sigstore. https://www.sigstore.dev/
71. OpenSSF. *Scorecard.* https://github.com/ossf/scorecard
72. PyPA. *pip issue #11694 — `--extra-index-url` dependency-confusion warning.* https://github.com/pypa/pip/issues/11694
73. PyPI. *Warehouse issue #9527 — typosquatting "social distancing".* https://github.com/pypi/warehouse/issues/9527
74. Datadog Security Labs. *Finding malicious PyPI packages (GuardDog) & the malicious-software-packages-dataset.* 2024. https://securitylabs.datadoghq.com/articles/guarddog-identify-malicious-pypi-packages/

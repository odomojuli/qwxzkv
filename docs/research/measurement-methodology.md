# Measurement methodology: Neupane 2023 and ConfuGuard (research notes)

Research memo for the qwxzkv / `typosquat` paper. A deep methodology pull on the two
measurement papers our comprehensiveness and evaluation claims lean on: Neupane et al.
(USENIX Security 2023) and ConfuGuard (arXiv:2502.20528). Verified against the primary
sources in July 2026 (Neupane full text via the authors' lab mirror; ConfuGuard v3 HTML).
Companion to `methods-and-eval.md`, `threat-landscape.md`, `threat-model.md`, and
`critique.md`. This memo exists to fix load-bearing errors: our coverage matrix does not
actually reproduce Neupane's taxonomy, and our "80% false positive" figure is misattributed.

## 1. Neupane et al., "Beyond Typosquatting" (USENIX Sec 2023, pp. 3439-3456)

### 1.1 Dataset and its dominant caveat

The corpus is **1232 documented attacks** (not "1200+"; the exact integer resolves the
`[verify]` in `related_work.md`). Built by searching six advisory programs from 2016
onward (CVE/NVD, Snyk, GitHub advisories, npm advisories, the PyPI advisory database,
RubyGems advisories) plus a large ReversingLabs contribution, with manual vetting to
saturation. Ecosystems: npm, PyPI (pip), RubyGems.

The single most important measurement fact, absent from all our current docs: **the
distribution is campaign-dominated.** Neupane defines a *confusion campaign* as a
coordinated upload of 10+ packages by one entity. **7 campaigns account for 1077 of 1232
incidents (87%)**, and **722 of 1232 (59%) come from one RubyGems delimiter campaign**
(ReversingLabs). Named campaigns: Azure scope confusion, Chinese-IP-address upload,
Ethereum mining, Hacktask typosquatting, package-info exfiltration, Ruby delimiters,
system-info exfiltration. Consequence for us: any recall number computed on this corpus
must be **stratified by campaign**, or it silently reports "did we catch the RubyGems
delimiter campaign."

### 1.2 The real 13 categories (this replaces our coverage matrix)

Table 2 of the paper, in the paper's **priority order** (higher = more specific; ties in
labeling break toward the higher-priority category). Two codes were merged during coding:
*Brandsquatting* -> Familiar term abuse, and *Keyboard locality* -> 1-step D/L (because
keyboard adjacency is layout-dependent). The mapping to our generator families, with an
honest coverage disposition, is the payload:

| # | Neupane category | Definition (example) | Our family | Disposition |
|---|------------------|----------------------|-----------|-------------|
| 1 | Prefix/suffix augmentation | add prefix/suffix: ecosystem, language, function, version (`dateutil` -> `python3-dateutil`) | `affix_combo` | covered (bounded by lexicon) |
| 2 | Sequence reordering | reorder consistent segments (`python-nmap` -> `nmap-python`) | `token_reorder` | covered |
| 3 | Delimiter modification | add/remove/swap delimiters (`active-support` -> `activesupport`) | `separator_*` | covered (E-gated) |
| 4 | Grammatical substitution | different grammatical form: number **or verbal** (`serialize` -> `serializes`, `learnlib` -> `learninglib`) | `grammatical_number` | **partial** (we do plural only; Neupane lemmatizes) |
| 5 | Scope confusion | unscoped mimics scoped (`@cicada/render` -> `cicada-render`) | `scope_manipulate` | covered (npm) |
| 6 | Semantic substitution | swap a token for a synonym (`bz2file` -> `bzip`) | none | **frontier** (needs embeddings) |
| 7 | Asemantic substitution | swap for a familiar but unrelated term (`libcurl` -> `pycurl`) | none | **frontier** (needs knowledge) |
| 8 | Homophonic similarity | sounds the same (`async` -> `asinc`) | `homophone` | covered |
| 9 | Simplification | drop a segment, meaning preserved (`urllib3` -> `urllib`) | `simplification` | covered |
| 10 | Alternate spelling | regional spelling (`colorama` -> `colourama`) | none | **frontier** (needs spelling lexicon) |
| 11 | Homographic replacement | ASCII look-alikes (`jellyfish` -> `jeilyfish`) | `homoglyph` | covered |
| 12 | 1-step Damerau/Levenshtein | one edit; fallback category (`crypto` -> `crypt`) | Channel A | covered (provable closure) |
| 13 | Familiar term abuse | brand/tech term, **no target package** (`plutov-slack-client`) | none | **out of scope** (targetless) |

So of 13: **8 covered, 1 partial, 3 semantic frontier (6, 7, 10), 1 targetless (13).**
Our current `taxonomy.md` matrix instead lists ~10 rows, silently omits 6/7/10/13, and
adds a **"Dependency confusion" row attributed to Neupane, which is not one of the 13**
(dependency confusion is Birsan, not Neupane). That is the falsifiable error a reviewer
will find first. `related_work.md` already treats dependency confusion correctly (as an
input-driven class surfaced via the cross-ecosystem mode); the matrix must match it.

### 1.3 Prevalence, quantified

Neupane's headline: package confusion is **not** mostly typos. **Rules 1-11 (the
semantic-leaning categories) are 82% of labels, dropping to 43% once the RubyGems
delimiter campaign is excluded** (composite attacks carry multiple labels, so labels
exceed attacks). Per-category ground-truth counts are only plotted (Figure 2), not
tabulated, but Table 3's `#TP + #FN` is a faithful proxy for graded positives per
category:

| Category | TP+FN (graded positives) | Detector P / R / F1 |
|----------|--------------------------|----------------------|
| Delimiter modification | 741 | 1.00 / 0.97 / 0.98 |
| Scope confusion | 208 | 1.00 / 0.90 / 0.95 |
| Prefix/suffix augmentation | 30 | 0.95 / 0.70 / 0.81 |
| Simplification | 11 | 0.58 / 0.64 / 0.61 |
| Sequence reordering | 8 | 0.88 / 0.88 / 0.88 |
| Grammatical substitution | 8 | 0.88 / 0.88 / 0.88 |
| Homographic replacement | 8 | 0.50 / 0.88 / 0.64 |
| Semantic substitution | 5 | 1.00 / 0.40 / 0.57 |
| Asemantic substitution | 4 | 0.75 / 0.75 / 0.75 |
| Homophonic similarity | 4 | 0.07 / 0.75 / 0.13 |
| Alternate spelling | 2 | 1.00 / 1.00 / 1.00 |

(1-step D/L and Familiar term abuse are excluded by the authors from detection, see 1.4.)
Two campaign-driven categories, **Delimiter + Scope, are 949 of 1029 graded positives
(92%)**. The three categories our generator cannot reach (Semantic 5 + Asemantic 4 +
Alternate spelling 2 = **11 of 1029, ~1.1%**). This yields a defensible, quantified
comprehensiveness claim: **generation reaches ~98.9% of Neupane's graded category
instances**, and the missed tail is purely semantic, low-count, and conceptually the
same openness we already scope out (and the same place slopsquatting lives). State it
with the campaign-skew caveat, not as a bare percentage.

Note a minor artifact discrepancy to footnote: the paper measures **1232** attacks; the
released dataset (NeupaneDB, used by ConfuGuard) reports **1,239** confirmed pairs. Cite
1232 for the paper's measurement, 1,239 for the released artifact.

### 1.4 Detection methodology (directly comparable to our generators)

Neupane's detectors are the closest prior art to our generate-then-score split, and two
of their assets are reusable:

- **Jargon corpus.** They ran ~1.9M PyPI+npm names through a token-extraction pipeline
  (split on delimiters, then an English word segmenter), dropped tokens appearing in <100
  names, and kept **10,425 unique tokens with frequencies; 5,110 are not standard
  English** ("js", "db", "lib", "html"). This is a ready-made, frequency-annotated
  token/affix lexicon (relevant to the combosquat-lexicon problem).
- **Uncommon-token rule.** Their Prefix/Suffix detector fires only when every target
  token is "uncommon" (frequency < 15% of the most common token) and the confuser is
  < 2x the target length, both length > 3. This is exactly the **bounding mechanism** a
  combosquat generator needs to stay finite and precise.
- **Delimiterless tokenization (Algorithm 1).** Forward/backward sliding-window matching
  against English (NLTK) + jargon corpora, with a mode-length and most-common-subsequence
  tie-break. Needed because names omit delimiters (`html5lib`, `setuptools`).
- **Alternate-spelling lexicon.** A **1,706-pair British->American** spelling table drives
  the Alternate spelling detector. Seeds our missing family #10.
- **Semantic detectors** use pre-trained FastText token embeddings (the semantic channel
  is a scoring prior, never a generator).
- **Excluded from measurement: 1-step D/L and Familiar term abuse.** The authors treat
  1-step edit as a trivial fallback "for cases where no semantic mechanism is apparent"
  and do not measure it. **This is our opening:** our provable Damerau-Levenshtein k-ball
  closure formalizes and bounds exactly the channel Neupane declined to measure. The two
  works are complementary, not competing: we make the edit fallback rigorous; they measure
  the semantic tail.
- **Precision-first** (base-rate fallacy), with a recall >= 33% floor for categories with
  < 5 samples. npm-wide validation via Snyk found **278 malicious of 275,910 flagged**
  (~0.1% base rate); the online survey rated **77% of matches potentially/highly confusing
  (18% highly)** at **< 1 warning per 100M package pairs**.

## 2. ConfuGuard (arXiv:2502.20528)

### 2.1 Provenance and the "80%" correction

Authors: Wenxin Jiang, Berk Cakar, James C. Davis (Purdue) with Mikola Lysenko (Socket);
the unnamed "industry partner" is **Socket**. arXiv-only as of July 2026. Title evolution
confirms our memory: v1 **TypoSmart** -> v2 "ConfuGuard: A Low False-Positive System..."
-> v3 "ConfuGuard: Using Metadata to Detect Active and Stealthy Package Confusion Attacks."

Our current claim ("~80% false positives across 7 registries") is wrong on scope. The
actual chain: ConfuGuard sampled **626 of the 640,482 false positives Neupane's lexical
detector produced** (npm/PyPI/RubyGems), of which 601 were still accessible; manual review
found **480 benign (79.9%)** and 121 stealthy (20.1%). So **"80%" is the benign fraction
of a name-similarity flagger's output on Neupane's 3-registry data**, not a 7-registry
generation-FP rate. ConfuGuard drives it to **28%** (a 52-point improvement) using
metadata. "7 registries" is ConfuGuard's *coverage*, a separate axis. Correct usage:
"pure name-similarity flagging is ~80% benign on Neupane's data (Socket/ConfuGuard);
metadata filtering cuts it to 28%." The **630 confirmed real attacks** is Socket's
production count, also separate.

### 2.2 Pipeline (six parts; the parts we should mirror or cite)

1. **Metadata DB** over 7 SPRs (npm, PyPI, RubyGems, Maven, Golang, Hugging Face, NuGet;
   >8M packages), refreshed weekly.
2. **Trusted resources** = popularity gate. Thresholds: **5,000 weekly downloads**
   (npm/PyPI/RubyGems/NuGet), 1,000 (Hugging Face), ecosyste.ms `avg_ranking` 10 for
   Maven/Golang (later 4 for Golang). "More trusted than t" = >=10x downloads **or** >=2x
   ecosyste.ms score. Directly informs our `pi(t)` and the target set we generate against.
3. **Name embeddings.** Fine-tuned FastText (from `cc.en.300.bin`) on ~9.1M names,
   delimiters stripped, hierarchical names split into author/package parts; 24 GB pgvector
   store, HNSW ANN.
4. **Confusion search.** Levenshtein **<= 2** plus cosine **>= 0.93** (grid-searched,
   AUC 0.94); hierarchical names tightened to 0.99 (package) / 0.9 (author) to catch
   compound squatting; retrieve **top-2 neighbors**. Their empirical naming stats are
   strong support for our k-ball being recall-first: across 1,239 real pairs, **median
   Levenshtein 1, mean 2.54, 77.7% at distance <= 2**, mean cosine 0.95. The ~22% beyond
   distance 2 is the semantic/structural tail (categories 6/7/10 and multi-edit combsquat).
5. **Benignity filter.** 11 metadata rules from the FP analysis + **R12-R15 added in
   production** = 15 rules (Table 3 of their paper), run as **LLM-as-Judge (OpenAI o4-mini)**,
   which beat a rule-based prompt (NeupaneDB 0.83 vs 0.82; ConfuDB 0.68 vs 0.53 - the
   rule-based prompt overfit). Rules worth stealing for our precision story: R2 distinct
   purpose (`lodash-utils` vs `lodash`), R7 adversarial name (length diff > 30% => unrelated),
   R13 org allow-list, R14 domain proxy/mirror, R15 NuGet registered prefix.
6. **Alerting** to human analysts, whose decisions tune thresholds/prompts.

### 2.3 Baselines, datasets, taxonomy extension

- **Baselines they run:** Levenshtein (Vu et al.) and **Typomind (Neupane's tool)**.
  **OSSGadget** (Microsoft; lexical permutation + existence check) they rule out as
  lexical-only and too slow. For *us* the priorities invert: OSSGadget is the closest
  generator baseline and must be included; Typomind is the semantic-detection SOTA.
  Name check: Neupane's tool is **Typomind** (`github.com/ldklab/typomind-release`), which
  is **not** the same as `typomania` (Rust Foundation) already in our related work. Keep
  both, labeled distinctly.
- **Ground-truth corpora (both public, both bigger than our current primary):**
  **NeupaneDB** = 1,840 packages (1,239 confirmed attacks + 601 labeled), **ConfuDB** =
  2,361 analyst-triaged threats across 7 registries. These should be our primary
  confusion-specific benchmarks; the 143-pair ecosyste.ms set is not load-bearing.
- **Taxonomy extension** for hierarchical registries (beyond Neupane's 13): **Impersonation
  squatting** (fake author/groupId), **Compound squatting** (simultaneous scope+delimiter
  edits), **Domain confusion** (Go URL-path mimicry). Our `scope_manipulate` and
  `token_reorder` partially reach these; worth a matrix note if we add Maven/Go/NuGet.
- **Stealth:** of 240 NPM true positives, **13.3% (32/240) injected malware >= 5 days after
  release** - support for the execution-tier / time-to-malware discussion in `threat-model.md`.

## 3. Corrections to apply to our docs

1. **`taxonomy.md` coverage matrix (flagship fix):** replace with the 13-row table in 1.2;
   mark 6/7/10 as the semantic frontier and 13 as targetless; delete the
   "Dependency confusion = Neupane category" row (surface it separately, as
   `related_work.md` does). Add the campaign-skew and ~98.9%-of-instances framing.
2. **`tests/test_coverage.py` docstring** overclaims ("*every* category must map to a
   family"). The `COVERAGE` dict is already the honest 9; soften the docstring to
   "every *orthographic/structural* category," and add an `xfail`/comment naming the
   3 semantic + 1 targetless categories as deliberately out of generator scope.
3. **`formalization.md` sec 4.2:** scope the claim "a category with no generating family is
   a failing test" to the coverable subset; state that Semantic/Asemantic substitution,
   Alternate spelling, and Familiar term abuse are out of the generator by construction and
   handled as the bounded frontier (this is the tri-part framing made precise).
4. **`methods-and-eval.md` sec 3 and `related_work.md`:** fix the "80% across 7 registries"
   wording per 2.1; promote NeupaneDB/ConfuDB to primary corpora; add Typomind + OSSGadget
   as baselines and distinguish Typomind from typomania; record ConfuGuard's Lev<=2 /
   cosine>=0.93 thresholds and the median-1 / mean-2.54 / 77.7%-<=2 naming statistics as
   empirical support for the recall-first k-ball.
5. **`related_work.md`:** resolve the Neupane `[verify]` to **1232**; sharpen the ConfuGuard
   entry (authors incl. Socket, 80%->28%, ConfuDB 2,361, o4-mini benignity filter).

## 4. What this unlocks for the combosquat/affix-lexicon problem (next candidate)

The measurement pull hands us the raw material for bounding the open combosquat/semantic
channel honestly: Neupane's **10,425-token frequency-annotated jargon corpus** (an
empirical affix lexicon), the **< 15%-of-max-frequency "uncommon token" rule** (a finite
bounding predicate for `affix_combo`), the **1,706-pair British/American spelling table**
(the missing Alternate-spelling family #10), and the finding that the semantic categories
we cannot generate (6, 7) are ~1% of instances - so a curated-affix + spelling-lexicon
generator plus an embedding **scoring** prior (not a generator) closes most of the gap,
with the residual scoped out explicitly. That is the shape of the next memo.

## References (primary URLs)

Neupane, Holmes, Wyss, Davidson, De Carli, "Beyond Typosquatting: An In-depth Look at
Package Confusion," USENIX Security 2023, pp. 3439-3456.
<https://www.usenix.org/conference/usenixsecurity23/presentation/neupane> ;
full text <https://ldklab.github.io/assets/papers/usenix23-confusion.pdf> ;
artifact <https://github.com/ldklab/typomind-release>.
Jiang, Cakar, Lysenko, Davis, "ConfuGuard: Using Metadata to Detect Active and Stealthy
Package Confusion Attacks Accurately and at Scale," arXiv:2502.20528 (v3).
<https://arxiv.org/abs/2502.20528> ; HTML <https://arxiv.org/html/2502.20528v3>.

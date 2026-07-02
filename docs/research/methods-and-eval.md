# Identity model, distance prior art, and evaluation (research notes)

Research memo for the qwxzkv / `typosquat` paper. Verified against primary specs and
literature, July 2026. Feeds the Formalization, Scoring, Related-work, and Evaluation
sections. Companion to `threat-landscape.md`, `threat-model.md`, and `critique.md`.

## 1. Registry identity model, verified against primary specs

The paper's central claim is that name identity `ν_E` is the right parameter. The
current specs confirm the three shipped ecosystems and let us extend cleanly.

**PyPI (PEP 503, confirmed verbatim July 2026).** Valid name regex (with
`re.IGNORECASE`): `^([A-Z0-9]|[A-Z0-9][A-Z0-9._-]*[A-Z0-9])\Z`. Charset is ASCII
letters, digits, period, underscore, hyphen; must start and end alphanumeric.
Normalization: `re.sub(r"[-_.]+", "-", name).lower()`, so `Friendly-Bard`,
`friendly.bard`, `friendly_bard`, `friendly--bard` are all one name. Note a spec fix
in August 2025 changed the validation regex terminator from `$` to `\Z` (the old form
wrongly accepted a trailing newline); use `\Z`. Source: packaging.python.org
name-normalization; peps.python.org/pep-0503. This matches `formalization.md` exactly.

**npm.** Name length at most 214 characters including the scope; new packages must be
lowercase; URL-safe characters only; cannot start with `.` or `_`; scoped form
`@scope/name`. The canonical validator is `github.com/npm/validate-npm-package-name`.
Separators are significant (npm does not collapse `-`/`_`/`.`), which is why
`cross-env` and `crossenv` are distinct packages. Confirms `ν_npm = lower(s)`.

**crates.io.** Max length 64 characters; ASCII alphanumeric, hyphen, underscore only;
compared case-insensitively AND with hyphen/underscore treated as equivalent, so
publishing a crate that differs from an existing one only by case or by `-` vs `_` is
blocked; reserved names prohibited (Windows device names like `nul`, etc.);
first-come-first-served. Source: doc.rust-lang.org, rust-lang/crates.io. Confirms
`ν_crates = lower(s).replace("_","-")`. Important nuance the paper should state: crates
collapses the separator *substitution* dimension but NOT separator *removal*, which is
why the Sept 2025 `faster_log` vs `fast_log` malicious crate was publishable.

**Extension registries (for a NuGet or multi-ecosystem section).**
- **NuGet:** case-insensitive comparison, but the identifier charset **permits
  non-ASCII / Unicode**, which is the structural reason Unicode-homoglyph NAME attacks
  concentrate on NuGet (the Oct 2025 `Netherеum` Cyrillic-e case). Opt-in ID-prefix
  reservation. This is the single most important cross-registry fact for the Unicode
  channel: it is precluded on npm/PyPI/crates and live on NuGet.
- **Go:** module path is a VCS location; uppercase letters are bang-encoded (`!`) in
  the proxy, so case is preserved but escaped; the module proxy is immutable-cached.
- **Maven:** `groupId:artifactId` coordinates, case-sensitive; the Central Portal now
  requires namespace (groupId) verification, which does not stop artifactId squatting
  within a verified namespace.
- **RubyGems:** hyphen and underscore are distinct (unlike crates), so `atlas-client`
  vs `atlas_client` are different gems, which is exactly the 2020 wave's mechanism.

**Comparison table (the identity axes that decide which transforms fire).**

| Registry | Collapses case | Collapses `-`/`_`(/`.`) | Permits non-ASCII | Unicode-homoglyph NAME attack possible? |
|----------|----------------|--------------------------|-------------------|------------------------------------------|
| PyPI | yes | yes (all of `-_.` to `-`) | no | no |
| npm | yes (new pkgs) | no | no | no |
| crates.io | yes | partial (`-`≡`_`, not removal) | no | no |
| RubyGems | mostly | no | no | no |
| NuGet | yes | no | **yes** | **yes** |
| Maven | no | no | limited | limited |
| Go | escaped | no | limited | limited |

Takeaway for the paper: the identity-exclusion step silences separator swaps on PyPI
and crates automatically, and the "Unicode similarity" concern from the project brief
is real only on NuGet and in the domain setting. This is the empirical backing for
making Unicode default-off on the three shipped registries.

## 2. Distance-metric prior art (position the scoring channels honestly)

**Trajectory / curve similarity is a mature field.** The standard trajectory-similarity
measures are DTW, discrete Fréchet distance, Fréchet distance, LCSS, and EDR, long used
in signature verification and handwriting recognition. Critically, **DTW has already
been applied to keyboard/typing trajectories** to compare typed-word sequences. So a
curve-similarity measure over keyboard paths is not new as a metric.

**Blunt verdict on the keyboard-Fréchet contribution.** The metric is not novel;
keyboard-geometry distance is standard (dnstwist's `replacement`/`insertion` already
use keyboard adjacency, and DTW has been used on typing trajectories). Applying
*discrete Fréchet over key centroids* specifically to package-name confusability
*ranking* may be a minor novelty, but it will not survive as a headline contribution.
Recommendation stands: demote it to one ablated scoring channel and report whether it
beats Damerau-Levenshtein plus keyboard-adjacency on the labeled set; if it does not,
cut it. Do not claim "novel" without narrowly scoping the claim to the package-name
ranking application, and cite the DTW/Fréchet trajectory lineage so a reviewer does not
surface it against you.

**Visual channel: cite the standard.** UTS-39 defines `confusables.txt` (~6,565
mapped characters) and a `skeleton()` function that maps a string to a canonical
confusable form; the standard technique is dual canonicalization (script-preserving
plus a script-agnostic skeleton) and whole-script-confusable detection, as deployed in
Chrome and Firefox IDN defenses. The project's confusable-weighted edit distance is a
variant of this; frame it as such and cite UTS-39 skeleton rather than claiming a new
visual metric.

**Phonetic channel: the family.** Beyond Double Metaphone, the standard encoders are
Soundex, Metaphone, Metaphone 3, NYSIIS, Caverphone, Match Rating Approach, and
Beider-Morse; Editex is a phonetic edit distance. Nikiforakis et al. soundsquatting is
the security-relevant precedent for homophone-driven confusion.

**dnstwist delta (state it precisely).** dnstwist's fuzzers are: addition,
bitsquatting, cyrillic, homoglyph, hyphenation, insertion, omission, plural,
repetition, replacement, transposition, vowel-swap, subdomain, and dictionary. The
tool matches essentially all of these on the orthographic/perceptual/encoding side.
The defensible delta over dnstwist and URLCrazy is: (1) the ecosystem-parametric
identity `ν_E` (domain tools have no registry identity), (2) the package-structural
families with no domain analogue (separator-as-identity-gated, scope manipulation,
token reorder, affix/combosquat, simplification, grammatical number), (3) the
generate/score separation, and (4) the provable edit-closure. State this list; do not
claim novelty for the permutation families dnstwist already has.

## 3. Evaluation protocol (make the eval defensible)

Three distinct measurements, because the paper conflates them at the moment:

1. **Generation recall.** Fraction of known real squats reproduced by
   `generate(target, E)`. Requires a squat-to-target mapping. Report per family and per
   ecosystem. This is the "comprehensiveness" evidence.
2. **Ranking quality.** Given a target, does the real malicious squat rank near the top
   of the generated-and-scored candidates? Report recall@k and AUC. Needs the
   popularity prior `π(t)`.
3. **Precision / false-positive rate.** Sample generated candidates and measure how many
   are benign existing packages vs plausible-malicious. Frame the baseline precisely (see
   `measurement-methodology.md`): ConfuGuard found that **79.9% of a manual sample from
   Neupane's 640,482 name-flagged pairs were benign** (NPM/PyPI/RubyGems), and cut that
   false-positive rate to **28%** with metadata filtering. "~80%" is the benign fraction
   of pure name-similarity flagging, not a 7-registry figure; the 7 registries are
   ConfuGuard's coverage, and the 630 confirmed attacks are Socket's production count.
   That 80%->28% arc is the baseline our scoring (the precision stage) must beat, and
   reporting it is what separates this from "we generate more candidates."

Baselines to run: **OSSGadget** (Microsoft; lexical permutation + existence check — the
closest generator baseline, and the one ConfuGuard rules out but we should not),
**Typomind** (Neupane's own detector, `ldklab/typomind-release` — the semantic-detection
SOTA; note this is NOT `typomania`, the separate Rust Foundation tool), dnstwist (adapted
to package names), `typomania`, ecosyste.ms `andrew/typosquatting`, the GuardDog rule
(short Levenshtein to top-5000 or a two-char swap), and pypi-scan. Report both recall and
candidate-set size (a precision proxy).

Ground-truth corpus (union, deduplicated; the 143-pair ecosyste.ms set alone is too
small, see `critique.md`). Primary confusion-specific benchmarks, both public and both
larger than the ecosyste.ms set: **NeupaneDB** (1,840 packages = 1,239 confirmed attacks
+ 601 labeled; `ldklab/typomind-release`) and **ConfuDB** (2,361 analyst-triaged threats
across 7 registries; released with ConfuGuard). Stratify recall by campaign — 722 of
Neupane's 1232 attacks are a single RubyGems delimiter campaign. Broader malicious-name
corpora: DataDog malicious-software-packages (17,367 human-vetted,
distinguishes compromised vs purpose-built), lxyeternal/pypi_malregistry (~10k, ASE
2023), ossf/malicious-packages (OSV format, tens of thousands), IntelliRadar
(arXiv:2409.15049, 34,313 names), ecosyste.ms typosquatting-dataset (143 clean labeled
pairs), Backstabber's Knife Collection (174, access-restricted). Over-sample the
crypto/Web3 and AI cluster where attacks concentrate.

## 4. Data sources (concrete, with endpoints)

**deps.dev (Google Open Source Insights) is the single best cross-ecosystem source.**
docs.deps.dev/api/v3 (JSON/HTTP and gRPC). Indexes Cargo, Go, Maven, npm, NuGet, PyPI,
RubyGems plus GitHub/GitLab/Bitbucket and OSV advisories. Gives a **dependents count**
(public dependents, treat as relative popularity not exact) and the project's OpenSSF
Scorecard, with batch endpoints (`GetVersionBatch`, `GetProjectBatch`). The v3alpha API
exposes **`GetSimilarlyNamedPackages`**, a ready-made similar-name oracle useful both as
a baseline and as an existence check. This is the recommended base for `π(t)`
(dependents, uniform across all seven ecosystems).

**Download-volume signals (supplement `π(t)`).**
- PyPI: BigQuery `bigquery-public-data.pypi.file_downloads` (populated by Linehaul;
  fields include timestamp, package, version, python version, installer, country);
  1 TB/month free tier; `pypinfo` CLI; lighter use via pypistats.org. Source:
  docs.pypi.org/api/bigquery.
- npm: `api.npmjs.org/downloads/point/{period}/{pkg}` and `/range/`.
- crates.io: `crates.io/api/v1/crates/{name}` (downloads field).
- ecosyste.ms packages API: downloads and dependent counts per registry, plus a
  `package_names` prefix/postfix search that is directly useful for squat discovery.

**Confirmed-malicious ground truth.** OSV.dev and `ossf/malicious-packages` use the OSV
schema: each report's `affected[].package` gives `{ecosystem, name}` and
`affected[].versions`/`ranges` give the malicious versions; the format is extensible
with IOCs and classification. Batch access via the osv.dev API. Extract malicious names
here, then map to targets via the labeled datasets above.

Licensing/limits: BigQuery free tier is 1 TB/month; deps.dev and OSV are public; attach
per-source attribution. None of these require the auth-gated connectors.

## 5. Recommendations that fall out of this

- Build `π(t)` as: deps.dev dependents (cross-ecosystem base) times an execution-tier
  multiplier (`threat-model.md`: install-auto-exec ecosystems rank higher) times a
  target-domain multiplier (crypto/Web3/AI, per `threat-landscape.md` §3), with raw
  downloads (BigQuery/npm API) as a secondary signal. This is more defensible than raw
  downloads alone and directly reflects where attacks land.
- Use `GetSimilarlyNamedPackages`, typomania, and ecosyste.ms as baselines; report
  recall AND candidate-set precision against ConfuGuard's ~80% lexical-FP framing.
- Demote keyboard-Fréchet to an ablated channel; cite the DTW/Fréchet trajectory
  lineage and UTS-39 skeleton so novelty claims are narrow and defensible.
- Add NuGet if the Unicode-homoglyph channel is to matter; it is precluded on the three
  currently shipped registries by ASCII normalization.

## References (primary URLs)

packaging.python.org/en/latest/specifications/name-normalization; peps.python.org/pep-0503,
pep-0508; github.com/npm/validate-npm-package-name; doc.rust-lang.org/cargo/reference/
(crate naming); learn.microsoft.com/nuget (identifiers, prefix reservation); go.dev/ref/mod;
maven.apache.org (coordinates); guides.rubygems.org.
unicode.org/reports/tr39 (confusables + skeleton); github.com/elceef/dnstwist (fuzzer list).
docs.deps.dev/api/v3 and /api/v3alpha; docs.pypi.org/api/bigquery; packaging.python.org/
guides/analyzing-pypi-package-downloads; github.com/ossf/osv-schema; github.com/ossf/
malicious-packages; osv.dev; packages.ecosyste.ms/docs.
Distance lineage: DTW / discrete Fréchet trajectory-similarity literature (signature and
handwriting), Eiter & Mannila 1994 (discrete Fréchet); UTS-39 skeleton; phonetic encoders
(Soundex, Metaphone/Double Metaphone, NYSIIS, Caverphone, Beider-Morse, Editex).

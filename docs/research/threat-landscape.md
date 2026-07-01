# The Typosquatting Supply-Chain Threat Landscape

Research memo for the qwxzkv / `typosquat` paper. Compiled July 2026 from primary
sources (vendor threat-research blogs, registry blogs, official advisories, CISA,
academic proceedings). Every scale figure is attributed to its reporting source;
most download counts are researcher estimates and several are attacker-inflated,
flagged inline. This memo feeds the paper's Introduction, Background/Threat model,
Case studies, and Related work. The companion file `critique.md` is the adversarial
gap analysis against the paper's own claims.

Purpose framing: this is defensive research. The corpus below documents publicly
reported attacks so the tool can enumerate the candidate space a defender should
pre-register, blocklist, and triage. Nothing here is operational guidance for
attackers; every incident is already public.

---

## 0. Read this first: five findings that should reshape the paper

1. **Most catastrophic OSS supply-chain incidents are NOT name confusion.** The
   headline npm events of 2018-2025 (event-stream, eslint-scope, ua-parser-js,
   coa/rc, @solana/web3.js, lottie-player, the Sept 2025 chalk/debug compromise at
   ~2.6B weekly downloads, the Shai-Hulud worms) are maintainer-account hijacks,
   maintainer phishing, or worms. Name enumeration prevents none of them. The paper
   must scope this honestly or a USENIX reviewer will call the motivation inflated.

2. **Name-confusion attacks are high-frequency, low-yield, and concentrated.** The
   genuine typosquat/combosquat/dependency-confusion campaigns are numerous but
   mostly low-download and short-lived, and from 2022 on they overwhelmingly target
   **crypto/Web3 and AI/ML** packages. That concentration is the tool's real market
   and should drive the popularity prior and the evaluation.

3. **Slopsquatting is a coverage gap by construction.** LLM-hallucinated package
   names are mostly NOT edit-distance neighbours of real names (Spracklen et al.,
   USENIX Security 2025: only 0.17% match deleted packages; "most are distinct from
   existing packages"). The paper's marquee theoretical contribution, a provable
   closure of the Damerau-Levenshtein k-ball, defends a channel that the
   fastest-growing target class sidesteps entirely.

4. **The integrity stack does not cover naming, and says so.** SLSA, Sigstore, npm
   provenance, PyPI PEP 740 attestations, and OpenSSF Scorecard all answer "is this
   the authentic artifact its publisher built?" They will faithfully attest a
   typosquat built and signed by its malicious author. SLSA's threat model
   explicitly lists typosquatting as out of scope. That un-owned gap is the tool's
   niche and should be the opening move of the Introduction.

5. **Unicode homoglyph name attacks are largely precluded on the three target
   registries.** npm, PyPI, and crates normalize to lowercase ASCII, which
   structurally blocks Unicode-confusable *name* squats. The confirmed 2025
   homoglyph case (`Netherеum` with a Cyrillic e) was on **NuGet**, which permits
   Unicode. "Unicode similarity," named in the project brief, is a scoring concern
   for display strings and a real attack only where names are not ASCII-normalized.
   Foreground it only where it bites.

---

## 1. Taxonomy reality check: name confusion vs everything else

Split every incident into two buckets. The paper's tool addresses only the first.

**Name-confusion class (the tool's scope).** Attacker registers a *new* deceptive
name: typosquat (`crossenv` for `cross-env`), combosquat (`ethers-web3`),
simplification (`node-fetch` to `fetch`), separator/scope tricks
(`@typescript_eslinter/eslint`), homophone, order, and dependency confusion
(identical internal name on a public registry). Value of a name-generation tool:
high for pre-registration and triage.

**Compromise class (out of scope, must be scoped out honestly).** Attacker seizes
an *existing* trusted name: maintainer-account hijack (ua-parser-js, coa/rc),
maintainer phishing (chalk/debug via `npmjs.help`, eslint-config-prettier via
`npnjs.com`), stolen CI tokens/worms (Shai-Hulud), malicious insider/protestware
(node-ipc), social engineering (DPRK Contagious Interview / Jade Sleet). No name
generator helps here.

Blunt implication: by download-weighted impact, the compromise class dominates. By
raw incident count and by "defensible with pre-registration," the name-confusion
class dominates. The paper should state this trade explicitly and claim the second,
not gesture at the first.

---

## 2. Attack corpus (the wide part)

Technique tags: `typo`, `combo` (combosquat), `simpl` (simplification), `sep`
(separator), `scope`, `homoglyph`, `homophone`, `order`, `depconf` (dependency
confusion), `brand` (brandjack/impersonation), `starjack`. Entries marked
"compromise" are the out-of-scope class, kept as labeled contrast cases.

### 2.1 npm

**2017 - crossenv campaign (`typo`/`combo`).** npm account `hacktask` published ~40
packages squatting popular libs; flagship `crossenv` for `cross-env`, plus
`mongose`, `babelcli`, `ffmepg`, `nodemailer.js`. Each re-exported real
functionality and ran a `package-setup.js` that POSTed environment variables to
`npm.hacktask.net`. npm estimated at most ~50 real `crossenv` installs; live ~2
weeks. Attribution is only the banned `hacktask` account. Correction to prior
drafts: not "nekohackers." (blog.npmjs.org crossenv-malware; theregister 2017/08/02)

**2018 - eslint-scope (compromise).** Reused-password takeover of an ESLint
maintainer account (no 2FA); trojanized `eslint-scope@3.7.2` pulled a pastebin
payload that exfiltrated `.npmrc` tokens. Contained by mass token revocation.
Landmark for the token-harvesting worm concept. (eslint.org postmortem)

**2018 - event-stream / flatmap-stream (compromise).** `right9ctrl`
social-engineered publish rights, added dependency `flatmap-stream@0.1.1` with an
AES-256 payload keyed to the string "A Secure Bitcoin Wallet" so it decrypted and
ran only inside the Copay wallet build, targeting wallets over 100 BTC.
event-stream ran ~2M downloads/week; malicious dependency lived ~2.5 months.
(blog.npmjs.org event-stream; theregister 2018/11/26)

**2020 - twilio-npm (`brand`).** `-npm` appended to the `twilio` brand; opened a
reverse shell to an ngrok endpoint. 371 downloads. (sonatype twilio-npm brandjacking)

**2020-2021 - Discord token-stealer cluster (`typo`/`brand`).** `fallguys`,
`discord.dll`, CursedGrabber family; fake game/Discord APIs stealing Discord tokens.
Hundreds of downloads each. (sonatype fallguys; threatpost)

**Feb 2021 - dependency confusion, Birsan (`depconf`, foundational).** Alex Birsan
uploaded public packages matching *internal private* names of 35+ orgs; npm/pip/gem
and Artifactory virtual repos resolved the higher public version. PayPal was the
origin (leaked internal `package.json`); Apple, Microsoft, Shopify, Netflix, Yelp,
Uber, Tesla named. ~$130k+ aggregate bounties. Correct date is Feb 9, 2021 (the
Medium page's later meta-date of 2023 is an edit artifact). Birsan is independent,
not "Ophion Security" (that is Rojan Rijal, a separate researcher). (medium Birsan;
sonatype 35-orgs; MSRC CVE-2021-24105)

**Feb-Mar 2021 - copycat wave (`depconf`).** Three distinct clusters routinely
conflated: (a) benign bounty PoCs, 150 rising to 700+ in weeks (Sonatype); (b)
genuinely malicious `amzn`, `zg-rentals` reading `/etc/shadow` and opening reverse
shells to `comevil.fun`; (c) a vigilante flood (`RemindSupplyChainRisks`) of ~5,000
packages, of which PyPI removed 3,653 and npm 1,500+. No primary source confirms any
third party actually breached a company via copycats. (sonatype 150-malicious;
sonatype bash-history; sonatype 5000-copycats)

**Oct 2021 - noblox.js-proxy / -proxies (`typo`).** Squats of `noblox.js`
(700k+ dls); UAC-bypass, Defender exclusions, Discord token stealer, prank
ransomware. Note the *legitimate* variant is `noblox.js-proxied` (with a d).
(sonatype noblox ransomware)

**Oct-Nov 2021 - ua-parser-js, then coa + rc (compromise).** Account hijacks of
packages at ~7M and ~23M combined weekly downloads; XMRig miner plus a credential
stealer (`sdd.dll` from `pastorcryptograph.at`). The linking malware is **DanaBot**,
not "qnodejs." CISA issued an alert for ua-parser-js. (github ua-parser-js #536;
cisa alert; therecord coa/rc)

**Dec 2021 - JFrog "17 malicious npm packages" (`typo`/`depconf`).** Exactly 17:
mostly `discord.js` token grabbers (`discord-selfbot-v14`, `discord-lofy`), env-var
stealers (`wafer-*`), and one dependency-confusion package. (jfrog 17-packages)

**Mar 2022 - node-ipc protestware (compromise/insider).** Maintainer inserted code
(v10.1.1/10.1.2) that overwrote files with a heart emoji for Russia/Belarus IPs.
CVE-2022-23812. Reached Vue via `@vue/cli`. (snyk peacenotwar; NVD)

**Jul 2022 - IconBurst (`typo`/`homoglyph`).** ReversingLabs found two-dozen-plus
packages squatting icon/UI libs (`icon-package`, `swiper-bundIe` with a capital I),
hooking `ajax()` to exfiltrate form data. 27,000+ downloads total. Correction: not
"100+ packages." (reversinglabs IconBurst)

**Jul 2022 - CuteBoi (flooding, not name confusion).** 1,200+ randomly-named XMRig
clones via ~1,000 auto-created accounts. Random names, so not typosquats; a scale
data point for automated abuse. (checkmarx CuteBoi)

**Oct 2022 - LofyGang (`typo`/`starjack`).** ~200 packages over a year stealing
cards, Discord tokens, gaming accounts; some patched the installed Discord client.
(checkmarx LofyGang)

**Jul-Nov 2023 - DPRK Jade Sleet / Contagious Interview (compromise/social-eng).**
GitHub-attributed North-Korea campaigns using malicious npm *package pairs*
(stage-1 writes a token, stage-2 reads it) and fake-recruiter lures delivering
BeaverTail then InvisibleFerret. Names are plausible lures, not misspellings.
(github.blog Jade Sleet; unit42 two-campaigns)

**Jun 2023 - Manifest Confusion (registry-integrity flaw).** Darcy Clarke showed npm
serves registry manifest metadata independently of the tarball `package.json` with
no validation, enabling hidden deps/scripts. Content confusion, a parallel to name
confusion. (darcyclarke.me)

**Oct-Nov 2024 - 287-package Ethereum-C2 wave (`typo`/`combo`, the flagship 2024
typosquat campaign).** Squats of Puppeteer (`pupeter`), bignumber.js, and Web3 libs
whose install script *queries an Ethereum smart contract for the current C2 IP*
(takedown-resistant) then pulls a platform-specific stealer. 287 packages (Phylum),
active ~1 week. A widely-cited ~$26M drain figure traces to a single community post;
do not state as fact. (socket ethereum-smart-contracts; checkmarx; phylum)

**Oct-Nov 2024 - MUT-8694 (`typo`, cross-ecosystem).** One actor squatting across
npm (18) and PyPI (42), 60 packages, Blank Grabber / Skuld Stealer. (datadog MUT-8694)

**Nov-Dec 2024 - @typescript_eslinter/eslint (`sep`/`scope`).** Underscore-for-hyphen
squat of `@typescript-eslint/eslint-plugin`; clipboard/credential exfil, WebSocket
C2. ~3,030 downloads, 43 versions in ~2 weeks. A clean separator/scope example.
(socket typescript-eslint)

**Dec 2024 - @solana/web3.js (compromise).** Spear-phish of a publish account;
malicious 1.95.6/1.95.7 hooked `Keypair.fromSecretKey` to exfiltrate keys.
CVE-2024-54134; ~$160k (674.86 SOL) stolen; live ~5 hours. DPRK attribution
circulated but is unconfirmed. (anza.xyz root-cause; GHSA-jcxm-7wvp-g6p5)

**Jan 2025 - Hardhat/Nomic scope confusion (`scope`, disclosed Jan 2, 2025).**
`@nomicsfoundation` (extra s), `@nomisfoundation` (dropped c) squatting
`@nomicfoundation`; malicious plugins harvest `hre.PRIVATE_KEY`. The cleanest
scope-confusion example. (socket ethereum-developers)

**Jul 2025 - eslint-config-prettier (compromise via `npnjs.com` phishing).** Maintainers
phished via a lookalike domain; malware pushed into packages at ~30M weekly
downloads. CVE-2025-54313. The *vector* is domain name confusion. (snyk prettier)

**Sep 8, 2025 - chalk/debug "qix" (compromise, largest-reach npm attack ever).**
Maintainer phished via `npmjs.help`; malicious versions of ~18 core packages at
~2.6B combined weekly downloads; browser crypto-clipper payload; live ~2 hours.
Despite the reach the crypto haul was roughly a few hundred to ~$1,000. The story is
reach vs payout, and the vector is domain-name confusion. (aikido chalk/debug; jfrog)

**Sep 15-16 & Nov 21-24, 2025 - Shai-Hulud waves 1 and 2 (worm, compromise).**
First self-replicating npm worm; entry via `@ctrl/tinycolor` plus ~40 packages;
TruffleHog secret-scan, auto-trojanize via stolen npm tokens, exfil to public
"Shai-Hulud" GitHub repos. Wave 1 grew to 500+ packages (incl. 9 CrowdStrike
packages), CISA alert Sep 23; wave 2 ("Second Coming") 600-800 packages, 25,000+
repos, a destructive dead-man's-switch, and a reported ~$8.5M Trust Wallet heist.
Combined 1,000+ packages (ReversingLabs). Not name confusion, but the reason npm
killed classic tokens. A widely-repeated "$50M" figure is unconfirmed; do not use.
(cisa 2025/09/23; datadog shai-hulud-2.0; securityweek 8.5M)

**Oct 2025 - PhantomRaven (`slopsquat`-adjacent + Remote Dynamic Dependencies).**
126 npm packages, 86,000+ installs, active since Aug 2025. Core novelty is listing
an HTTP URL as a dependency so npm fetches and executes the payload at install
(invisible to dependency-tree scanners); *some* names were chosen to match
AI-hallucinated names. Do not present as a pure slopsquatting campaign. (thehackernews
phantomraven; koi.ai)

**Mar 2026 - Solana/Ethereum key-theft squats (`typo`).** 5 packages (`raydium-bs58`,
`ethersproject-wallet`, etc.) hooking the exact Base58/ethers function keys pass
through, exfil to a Telegram bot. (socket 5-malicious 2026)

**Apr-May 2026 - dependency/scope confusion resurgence (`depconf`/`scope`).**
`@genoma-ui/components` and peers beaconing recon (safedep, Apr 2026); Microsoft's
33-package wave under corporate-mirror scopes including `sberpay-widget` for
Sberbank's SberPay (May 29, 2026). Evidence the depconf channel is still live at
scale in 2026. (safedep genoma; microsoft 33-packages)

### 2.2 PyPI

**2017-2018 - colourama (`typo`).** British-spelling squat of `colorama` (~1M
dls/day); Windows crypto clipboard hijacker. The canonical PyPI clipboard-hijack
typosquat. No credible tie to Slovakia; drop that attribution. (bertusk medium;
in-toto catalog)

**2019 - jeIlyfish (`homoglyph`) + python3-dateutil (`combo`).** `jeIlyfish` swaps a
capital I for the l in `jellyfish`; `python3-dateutil` imported it. Exfiltrated SSH
and GPG keys. `jeIlyfish` lived ~1 year. (sysdig; dateutil #984; bleepingcomputer)

**May 2022 - ctx (compromise via lapsed domain).** Dormant `ctx` hijacked by
re-registering the maintainer's expired domain; exfiltrated AWS env vars. Paired with
a PHP `phpass` GitHub hijack. Maintainer takeover, not name confusion, but cataloged
alongside squats. (cloudsecurityalliance; thehackernews 2022/05)

**Jul-Dec 2022 - W4SP stealer wave (`typo`/`combo`/`starjack`).** 30+ modules
squatting popular libs using StarJacking (fake GitHub repo URLs) and steganography;
W4SP info-stealer to a Discord webhook. Attributed to "billythegoat356." (phylum
w4sps-nest; checkmarx; reversinglabs)

**May 2023 - registration suspension (registry response).** PyPI temporarily
suspended new user and project registration because malicious volume outpaced
response. Landmark defensive event. (bleepingcomputer; checkmarx)

**Mar 2024 - 500+/566 typosquat flood (`typo`, second sign-up halt).** One automated
account; Check Point counted 500+, RH-ISAC 566 packages (requests 36 variants,
colorama 35, tensorflow 29) carrying zgRAT; PyPI again suspended registration Mar 28.
(checkpoint pypi-typosquatting; rhisac)

**2024 - crytic-compilers, solana-py, browser-cookies3 (`typo`).** Pluralization and
cross-platform-name squats (the GitHub name `solana-py` registered on PyPI where the
real package is `solana`), version-spoofed to look newer, dropping Lumma/stealers.
(sonatype crytic-compilers; sonatype solana-py; socket browser-cookie3)

**2025 - SilentSync (`typo`), Bittensor staking squats (`typo`), chimera-sandbox
(`depconf`-flavor).** `termncolor` for `termcolor`; `bitensor`/`qbittensor` for
`bittensor`; `chimera-sandbox-extensions` impersonating internal tooling to steal AWS
and CI/CD secrets. (zscaler silentsync; gitlab bittensor; csoonline chimera)

**2026 (verify before print) - TrapDoor and a Shai-Hulud PyPI copycat.** TrapDoor:
34+ packages / 384+ versions across PyPI, npm, crates, with plausible-name lures and
planted `.cursorrules`/`CLAUDE.md` PRs to trick coding assistants (socket trapdoor).
Shai-Hulud PyPI copycat (Jun 2026): `rlask`/`tlask` (Flask), `rsquests` (Requests),
`nhmpy` (NumPy), using `.pth`-file auto-execution at interpreter startup (gitlab
shai-hulud-copycat).

### 2.3 RubyGems

**Aug 2019 - rest-client hijack (compromise).** Maintainer account compromised;
malicious v1.6.10-1.6.13 siphoned env vars, backdoor in Rails production.
CVE-2019-15224. (theregister 2019/08; rest-client #713)

**Feb 2020 - ~760 typosquatted gems (`sep`).** Uploaded over ~one week; hyphen for
underscore swaps; Windows crypto clipboard hijacker. Flagship `atlas-client` for
`atlas_client`, ~2,100 downloads. Correction: this 700-gem wave is 2020, distinct
from the 2019 rest-client hijack. (thehackernews 2020/04; helpnetsecurity)

**Dec 2020 - pretty_color / ruby-bitcoin (`brand`).** Brandjacked `colorize`, same
clipboard hijacker, taunt aimed at the ReversingLabs analyst. (sonatype rubygems-bitcoin)

**2025 - Fastlane plugin squats (`typo`), 60-gem Korea campaign (`brand`).**
`fastlane-plugin-proxy_teleram` (transposed "teleram") exfiltrating CI/CD secrets
(socket); 60 gems, 275,000+ cumulative downloads, Korean-language infostealers
(socket 60-gems).

### 2.4 crates.io

**May-Sep 2025 - faster_log + async_println (`typo`, the strongest crates case).**
Squats of `fast_log`; published May 25, 2025, deleted 15:34 UTC Sep 24, 2025; 7,181
and 1,243 downloads (official crates.io figures). Scanned source/log files for
Ethereum and Solana secrets. Runtime-only, no build script, no dependents. Note this
is exactly the separator-removal case crates.io's hyphen/underscore normalization
does NOT catch. (blog.rust-lang.org 2025/09/24; socket two-crates)

### 2.5 NuGet (the home of homoglyph name attacks)

**Oct 2025 - Nethereum homoglyph (`homoglyph`, the clean landmark).** `NethereumNet`
(combo) then `Netherеum.All` with a Cyrillic e (U+0435); XOR-decoded C2; download
count artificially inflated to 11.7M via scripted version-downloads. NuGet does not
restrict identifiers to ASCII, which is *why* homoglyph name attacks concentrate
here rather than on npm/PyPI/crates. (socket nethereum; thehackernews 2025/10)

**Feb 2026 (verify) - StripeApi.Net (`typo`/`sep`).** Squat of `Stripe.net`,
exfiltrating the Stripe API token; download count inflated to 180,000+ across 506
versions. Signals a shift from blockchain to fintech targeting on NuGet.
(reversinglabs stripe; thehackernews 2026/02)

### 2.6 Go, 2.7 Maven, 2.8 Docker Hub (breadth, lower incident-resolution)

Go: BoltDB backdoor (`github.com/boltdb-go/bolt` for `boltdb/bolt`, 3+ years
undetected, disclosed Feb 2025); `github.com/shopsprint/decimal` for
`shopspring/decimal`, benign ~6 years then a v1.3.3 backdoor; a 7-package loader
wave (Mar 2025). Go import paths bind to VCS hosts, so squats imitate
owner/repo paths and exploit the immutable module proxy for persistence. (socket
boltdb; socket; thehackernews 2025/03)

Maven: `scribejava-core` OAuth impersonation, time-bombed to fire on the 15th
(disclosed Mar 2025); a Jan 2026 Jackson lookalike using groupId
`org.fasterxml.jackson.core` for the legitimate `com.fasterxml.jackson.core`, a
TLD-style prefix swap directly analogous to domain typosquatting. (socket scribejava;
aikido maven-jackson)

Docker Hub: repository-name confusion (e.g., `node-official` for the official
`node`), aggregate research finding millions of malicious-or-typosquatted repos,
~70% cryptominers. Pull counts are unreliable; treat as illustrative. (sysdig;
unit42 cryptojacking)

---

## 3. Cross-cutting patterns (the analysis that should drive design)

**Target concentration.** From 2022 on, name-confusion payloads overwhelmingly aim
at crypto/Web3 (wallet keys, Solana/Ethereum secrets, clipboard hijack) and, from
2024, AI/ML tooling (`claudeai-eng`, `gptplus`, MCP-server impersonation like
`postmark-mcp`). Design consequence: the popularity/exposure prior pi(t) should not
be raw downloads alone; a crypto/AI target multiplier matches where real attacks
land. The evaluation should over-sample this cluster.

**Technique drift.** Roughly: pure typo (2017-2019) to combosquat and starjacking
(2022) to dependency/scope confusion at enterprise scale (2021, resurgent 2026) to
slopsquatting (2025-2026). Install-time execution (setup.py / postinstall / build.rs
/ .pth / pre-install) is the near-universal delivery mechanism, and C2 is
increasingly takedown-resistant (Ethereum smart contract, blockchain, GitHub Pages,
Telegram). The generator families in `taxonomy.md` cover the *naming* techniques;
they do not and cannot cover delivery, which is fine but should be stated.

**Scale is mostly small and inflated.** Real install counts for individual squats
are usually in the hundreds to low thousands and dwell time is often hours to weeks.
Download counters are attacker-inflatable (NuGet 11.7M and 180,000+ cases are
scripted). Any recall/impact claim in the paper should use install or dependent
counts where available and treat raw downloads skeptically.

**Homoglyph is a NuGet/domain phenomenon.** Reiterated because the project brief
names Unicode similarity: on the three shipped registries, ASCII normalization
precludes Unicode-confusable *name* collisions. ASCII-range visual confusion
(capital-I for l, rn for m) still works because it survives as a *distinct*
normalized name that merely *looks* the same, which is a scoring problem (the
confusable-weighted metric), not a normalization bypass.

**Fake popularity as an amplifier.** Starjacking (borrowing a real repo's stars) and
scripted download inflation both manufacture trust. A defender-facing tool could flag
the *inverse*: a high-similarity candidate whose popularity signal is anomalously
inflated relative to age. Worth a sentence in Discussion.

---

## 4. Defenses, and why none of them own the naming problem

**Registry controls.** PyPI flags potential typosquats at upload using Levenshtein
distance <= 2 against roughly the top 1,000 packages after PEP 503 normalization
(warehouse #9527); that rule caught only 18 of 40 historical squats, so >50% miss,
and it is blind to combosquat, homoglyph, separator-removal, and semantic variants.
PyPI also mandates 2FA (since Jan 2024), Trusted Publishing/OIDC, quarantine (PEP
792 status markers), archival (Jan 2025), and PEP 708 to mitigate cross-index
dependency confusion (the one deployed standard aimed at any confusion class). npm
has 2FA on high-impact packages, provenance/Sigstore attestations, scopes (the main
structural defense, still leaving the flat unscoped namespace first-come), and in
2025 killed classic tokens. crates uses hyphen/underscore/case equivalence (which
missed `faster_log`). RubyGems still ships no automated similarity gate. NuGet offers
opt-in ID-prefix reservation, which does nothing against a lookalike prefix.

**Detectors and their name-confusion generator.** This is where the paper's "prior
tools use edit-distance-as-generator" claim must be precise, because it is correct
but the specifics matter:

- **GuardDog (Datadog):** flags a name at short Levenshtein distance to a top-N list
  (Datadog's own description says top 5,000) or a two-character swap. Pure edit
  distance; misses combosquat, scope, slopsquat.
- **typomania (Rust Foundation, powers crates.io):** bitflip, omission, repetition,
  transposition, delimiter, version-suffix; homoglyph/keyboard only if the integrator
  supplies a map (it ships none). No combosquat, no scope.
- **andrew/typosquatting (ecosyste.ms):** the broadest OSS generator (omission,
  repetition, keyboard replacement, transposition, addition, homoglyph, vowel swap,
  delimiter, word order, plural, misspelling, numeral, bitflip, adjacent insertion,
  double hit, and a fixed-suffix combosquat). Still edit-anchored, so no slopsquat by
  construction; combosquat is a fixed suffix set.
- **pypi-scan (IQTLabs):** Levenshtein <= 1 plus Metaphone phonetic. Archived Jan
  2023.
- **Socket / ConfuGuard:** lexical candidate generation plus a metadata false-positive
  filter. ConfuGuard exists precisely because pure lexical name confusion runs ~80%
  false positives (arXiv:2502.20528; note it was earlier titled "TypoSmart").

Every deployed generator is anchored on existing real names and emits string-edit
neighbours. That is simultaneously the paper's opening (prior art is a fixed
transform list) and its trap (so is the tool's edit channel, plus structural families
that a reviewer will note ecosyste.ms already has).

**Standards do not cover naming and say so.** OpenSSF Scorecard has ~19 hygiene
checks, none for name similarity. SLSA (current v1.2, Nov 2025) explicitly excludes
typosquatting in its threat model and published a 2024 "Defender's Perspective" post
conceding it needs additional capabilities. Sigstore/cosign and PEP 740 attest
identity and integrity, not name choice. One-line framing for the Introduction: the
entire supply-chain integrity stack answers "did the claimed publisher build this
unmodified artifact?" and will happily attest a typosquat built by its malicious
author. "Is this name impersonating another?" is un-owned. That is the gap.

---

## 5. Slopsquatting and AI-hallucinated names: the new target class

**Origin.** "AI package hallucination" demonstrated by Bar Lanyado at Vulcan Cyber
(2023); the `huggingface-cli` empty-package PoC (Lanyado, then at Lasso Security)
was installed 15,000+ times over ~3 months. The term "slopsquatting" was coined by
Seth Larson (PSF) in April 2025 and popularized by Andrew Nesbitt. (lasso
ai-package-hallucinations; fosstodon sethmlarson)

**Measurement (the load-bearing citation).** Spracklen et al., "We Have a Package
for You!", USENIX Security 2025: 16 models, 576,000 code samples, average
hallucination rate ~5.2% commercial and ~21.7% open-source, **205,474 unique
hallucinated package names**. Persistence is the danger: 43% of hallucinations
recur in all 10 re-runs and 58% repeat more than once, so the set is finite,
stable, and pre-registerable. Crucially for this project, hallucinated names are
mostly NOT edit-distance typos: only 0.17% matched packages deleted from PyPI
2020-2022, 8.7% of hallucinated Python names are actually valid JavaScript packages
(cross-language bleed), and the authors state most are "substantively different from
existing package names." A 2026 replication ("The Range Shrinks, the Threat
Remains," arXiv 2605.17062) reports rates compressing to ~5-6% on frontier models
while the absolute surface persists; verify its exact figures against the PDF.
(arxiv 2406.10279; usenix spracklen)

**Real-world exploitation.** PhantomRaven (Oct 2025) is the strongest data point and
it is only partial: its core novelty is Remote Dynamic Dependencies, with
hallucinated-name selection as one naming strategy. No verified, named,
mass-scale, purely-slopsquatting campaign exists yet; treat any such claim as
unconfirmed.

**Why it matters to this tool.** A generator whose comprehensiveness argument is a
Damerau-Levenshtein k-ball cannot reach a target class that is distinct from real
names by construction. Either the paper adds a hallucination channel (seed and
evaluate against the public 205,474-name corpus at github.com/Spracks/
PackageHallucination; model command-to-package and cross-language name bleed; add a
plausibility prior) or it explicitly scopes slopsquatting out and stops claiming
"completely comprehensive." The first option is the stronger paper and aligns with
the roadmap note about a semantic plausibility prior.

---

## 6. Verified bibliography (corrections folded in)

Confirmed against proceedings, dblp, arXiv, publisher pages. Corrections to the
current `related_work.md` in bold-equivalent notes.

Package-confusion measurement and taxonomy:
- Neupane, Holmes, Wyss, Davidson, De Carli. "Beyond Typosquatting: An In-depth Look
  at Package Confusion." USENIX Security 2023, pp. 3439-3456. usenix.org/system/
  files/usenixsecurity23-neupane.pdf. Note: 13 confusion categories; the "1232
  attacks" figure is in the body (abstract says "1200+"), verify the exact integer.
  No DOI.
- Vu, Pashchenko, Massacci, Plate, Sabetta. "Typosquatting and Combosquatting
  Attacks on the Python Ecosystem." IEEE EuroS&PW 2020, pp. 509-514.
  doi.org/10.1109/EuroSPW51379.2020.00074. Keep distinct from the same group's
  LastPyMile (ESEC/FSE 2021, not MSR) and py2src (venue unverified).
- Zimmermann, Staicu, Tenny, Pradel. "Small World with High Risks: A Study of
  Security Threats in the npm Ecosystem." USENIX Security 2019, pp. 995-1010.
- Ohm, Plate, Sykosch, Meier. "Backstabber's Knife Collection." DIMVA 2020, LNCS
  12223, pp. 23-43. doi.org/10.1007/978-3-030-52683-2_2. The 174-package dataset.
- Duan, Alrawi, Kasturi, Elder, Saltaformaggio, Lee. "Towards Measuring Supply Chain
  Attacks on Package Managers for Interpreted Languages" (MalOSS). NDSS 2021.
- Ladisa, Plate, Martinez, Barais. "SoK: Taxonomy of Attacks on Open-Source Software
  Supply Chains." IEEE S&P 2023, pp. 1509-1526. doi.org/10.1109/SP46215.2023.10179304.
  The 107-node attack taxonomy; a strong SoK anchor the current draft omits.

Detection and recent measurement:
- Jiang, Cakar, Lysenko, Davis. "ConfuGuard: Using Metadata to Detect Active and
  Stealthy Package Confusion Attacks Accurately and at Scale." arXiv:2502.20528
  (2025; formerly titled "TypoSmart"). arXiv-only, no venue as of July 2026.
- Taylor, Vaidya, Davidson, De Carli, Rastogi. "SpellBound / typogard: Defending
  Against Package Typosquatting." arXiv:2003.03471 (2020). Reports 0.5% FP; the
  typomania port descends from typogard.
- Spracklen, Wijewickrama, A.H.M. Nazmus Sakib, Maiti, Viswanath, Jadliwala. "We
  Have a Package for You! A Comprehensive Analysis of Package Hallucinations by
  Code-Generating LLMs." USENIX Security 2025. arXiv:2406.10279. Use 19.6% (or the
  5.2%/21.7% split), not 19.7%; 205,474 unique names.

Dependency confusion:
- Birsan. "Dependency Confusion: How I Hacked Into Apple, Microsoft and Dozens of
  Other Companies." Independent disclosure, Feb 9, 2021. Cite as the origin of the
  class; no standalone academic citation exists (a genuine gap, not a missing find).

Domain-squatting lineage:
- Szurdi et al. "The Long Taile of Typosquatting Domain Names." USENIX Security 2014,
  pp. 191-206 ("Taile" is the deliberate spelling).
- Agten, Joosen, Piessens, Nikiforakis. "Seven Months' Worth of Mistakes." NDSS 2015.
- Nikiforakis et al. "Soundsquatting: Uncovering the Use of Homophones in Domain
  Squatting." ISC 2014 (not WWW).
- Nikiforakis et al. "Bitsquatting: Exploiting Bit-Flips for Fun, or Profit?" WWW
  2013, pp. 989-998.
- Dinaburg. "Bitsquatting: DNS Hijacking without Exploitation." Black Hat USA 2011
  (verify the media URL, use Wayback if it 404s).
- Moore, Edelman. "Measuring the Perpetrators and Funders of Typosquatting." FC 2010,
  LNCS 6052, pp. 175-191.

Foundations:
- Levenshtein 1966 (Soviet Physics Doklady 10(8):707-710, no DOI); Damerau 1964 (CACM
  7(3):171-176, doi.org/10.1145/363958.363994); Eiter, Mannila 1994, "Computing
  Discrete Frechet Distance," TU Wien tech report CD-TR 94/64 (a report, not a venue,
  no DOI); UTS-39 (cite editors Davis and Suignard plus the revision used); Philips
  2000, "The Double Metaphone Search Algorithm," C/C++ Users Journal 18(6):38-43
  (print, no DOI).

Evaluation datasets (expanded; the current draft only lists ecosyste.ms):
- ecosyste-ms/typosquatting-dataset: exactly **143** labeled squat-to-target
  mappings (PyPI 95, npm 35, Go 8, GitHub Actions 4, crates.io 1). Too small and too
  skewed to be the primary recall benchmark; crates coverage is a single row.
- ossf/malicious-packages: OSV-format aggregate, tens of thousands of reports.
- lxyeternal/pypi_malregistry: ~10,000 malicious PyPI packages (ASE 2023 study).
- DataDog/malicious-software-packages-dataset: 17,367 human-vetted npm/PyPI samples,
  distinguishing compromised vs purpose-built.
- IntelliRadar (arXiv:2409.15049): 34,313 malicious npm/PyPI names from unstructured
  intel; 7,542 not in OSV.
- Spracks/PackageHallucination: the 205,474 hallucinated-name corpus for a slopsquat
  channel.

---

## 7. Concrete corrections to the current docs

For `related_work.md`: promote the four ✔-plus-unverified entries to verified with
the metadata in section 6; add Ladisa SoK 2023, Spracklen USENIX 2025, Taylor
SpellBound, and the expanded dataset list; fix Soundsquatting to ISC 2014; mark
Eiter-Mannila as a tech report; note ConfuGuard is arXiv-only and was formerly
"TypoSmart."

For `taxonomy.md` and the case-study plan in `outline.md`: the `crossenv` attacker is
`hacktask`; add a technique-class column separating name-confusion from compromise so
the empirical coverage matrix is not read as covering account hijacks; add a
slopsquatting row (currently absent) and either map it to a new generating family or
mark it an explicit out-of-scope gap; use the 2024-2026 crypto/Web3 campaigns
(287-package Ethereum-C2, Hardhat scope confusion, faster_log, Nethereum homoglyph)
as the modern case studies rather than only `crossenv` (2017).

Key numeric corrections to reuse anywhere: Spracklen 19.6% not 19.7%; Neupane 13
categories; IconBurst two-dozen-plus packages / 27,000+ downloads not "100+";
coa/rc malware is DanaBot not qnodejs; RubyGems 700-gem wave is 2020 not 2019;
JarkaStealer (`gptplus`, `claudeai-eng`) was PyPI not npm.

---

## References (primary URLs)

Corpus: blog.npmjs.org (crossenv, event-stream); eslint.org postmortem; theregister
typosquatting npm; github.blog Jade Sleet; unit42.paloaltonetworks.com two-campaigns
and npm-supply-chain; cisa.gov 2021 ua-parser-js and 2025/09/23 npm alerts;
jfrog.com 17-packages; snyk.io peacenotwar and prettier; reversinglabs.com IconBurst
and w4sp; checkmarx.com CuteBoi, LofyGang, pypi-typosquatting; socket.dev
(ethereum-smart-contracts, typescript-eslint, ethereum-developers, nethereum,
trapdoor, two-crates, browser-cookie3, 5-malicious 2026); phylum.io w4sps-nest and
puppeteer; sonatype.com (twilio-npm, fallguys, 35-orgs, copycats, crytic-compilers,
solana-py, rubygems-bitcoin); datadog securitylabs (MUT-8694, tenacious-pungsan,
shai-hulud-2.0); aikido.dev (chalk/debug, maven-jackson); anza.xyz web3-js; blog.
rust-lang.org 2025/09/24; gitlab.com (bittensor, shai-hulud-copycat); zscaler
silentsync; safedep genoma; microsoft.com 33-packages and shai-hulud guidance;
sysdig colourama and docker; cloudsecurityalliance ctx.

Defenses and standards: github.com/pypi/warehouse issue 9527; blog.pypi.org
(2fa-enforcement, quarantine, archival, wheel-archive-confusion); peps.python.org
708, 740, 503, 792; github.blog npm provenance and 2025 token changes; slsa.dev
spec v1.0 threats and 2024/08 dep-confusion blog; docs.sigstore.dev; scorecard.dev;
github.com/rustfoundation/typomania; github.com/andrew/typosquatting; github.com/
IQTLabs/pypi-scan; arxiv.org/abs/2502.20528.

Academic: usenix.org (neupane, zimmerman, spracklen); doi.org (EuroSPW Vu, DIMVA Ohm,
S&P Ladisa, CACM Damerau); ndss-symposium.org (Duan MalOSS, Agten); arxiv.org/abs/
2406.10279, 2003.03471, 2409.15049; github.com/ecosyste-ms/typosquatting-dataset;
github.com/Spracks/PackageHallucination.

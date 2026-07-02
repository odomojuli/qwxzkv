# Install-time execution: the model that sets risk priority

Research memo for the qwxzkv / `typosquat` paper's threat-model section. Verified
against primary docs, July 2026. Defensive framing: this establishes why a registered
squat becomes code execution, and why some registries make a squat immediately
dangerous while others leave it latent, which is what a risk-ranking (the popularity
prior pi(t)) should encode.

## The core question

Registering a typosquatted name is uniformly cheap and unvetted on every registry.
What differs, and what decides whether a squat is immediately dangerous or merely
latent, is **when the attacker's code first executes** after a victim pulls the name.
Three tiers:

| Tier | Trigger | Ecosystems |
|------|---------|------------|
| A: auto-exec at INSTALL | the install command alone detonates | npm (default); PyPI **sdist**; RubyGems **native-extension** gems; NuGet **packages.config** (legacy) |
| B: exec at BUILD/COMPILE | first build/compile/test detonates | Cargo (`build.rs` + proc-macros); Maven **plugins**; NuGet **PackageReference** (MSBuild targets) |
| C: import-only / run-only | code runs only when imported and the program/tests run | Go; PyPI **wheel**; RubyGems pure-Ruby; Maven plain **dependencies** |

The nuance the paper must get right: **tier is set by artifact type and toolchain era,
not by ecosystem alone.** PyPI is Tier A or C depending on sdist vs wheel; NuGet is A or
B depending on packages.config vs PackageReference; RubyGems is A or C depending on
native-extension vs pure-Ruby. A risk model keyed only on "which registry" is wrong.

## Per-ecosystem execution model

**npm: auto-exec at INSTALL (default, transitive).** Lifecycle scripts
`preinstall`/`install`/`postinstall` in `package.json` run automatically on
`npm install` for every dependency including transitive ones; a `binding.gyp` triggers
`node-gyp rebuild` with no explicit script. Opt-out is `--ignore-scripts`. RFC #868
proposes flipping the default to opt-in in npm v12 (announced around July 2026); as of
current stable (v11) scripts still run by default. **State the live default as
opt-out (scripts run); re-check v12 GA at final draft.** Highest risk multiplier.
docs.npmjs.com/cli/v11/using-npm/scripts; github.com/npm/rfcs/pull/868

**PyPI/pip: split.** An sdist (`.tar.gz`) must be built before install, invoking the
build backend, which is arbitrary Python; legacy `setup.py` is code execution at
install-from-source. **PEP 517 build isolation does not prevent this**: it isolates
what is importable in the build env, not whether attacker code runs. A wheel (`.whl`,
PEP 427) installs by unzipping into site-packages and contains no setup.py, so the
payload runs only at first import (Tier C). pip prefers wheels but "will default to
finding source archives" when no compatible wheel exists, so an attacker publishing an
**sdist-only** squat forces build-time execution on a default `pip install`.
`--only-binary=:all:` forces wheels-only. packaging.python.org binary-distribution-format;
peps.python.org/pep-0517

**RubyGems: split.** Native-extension gems (`spec.extensions`, e.g. `extconf.rb`) are
"run when the gem is installed, causing the C (or whatever) code to be compiled on the
user's machine": arbitrary Ruby at `gem install`. Pure-Ruby gems run on `require`.
`post_install_message` is display-only. Edge case: `rubygems_plugin.rb` loads on the
next `gem` invocation. guides.rubygems.org/gems-with-extensions,
guides.rubygems.org/specification-reference

**Cargo/crates.io: exec at BUILD (not at add/fetch).** A `build.rs` "will cause Cargo
to compile that script and execute it just before building the package"; proc-macros
"run during compilation" with compiler privileges. `cargo add` only edits `Cargo.toml`
and `cargo fetch` only downloads; neither runs crate code. Detonation is the next
`cargo build`/`test`/`run`. Build-script warnings are suppressed unless the build
fails, and Cargo does not sandbox build scripts or proc-macros. doc.rust-lang.org/cargo/
reference/build-scripts.html; doc.rust-lang.org/reference/procedural-macros.html

**Go modules: import-only / run-only (lowest).** Explicit toolchain security goal:
"neither fetching nor building code will let that code execute, even if it is untrusted
and malicious." `go get` resolves and downloads, no execution; code runs only when a
package is imported into a program that is then built and run (package `init()` fires at
program runtime), and `go test` runs test code. No compile-time package-code execution
(no proc-macro analogue). go.dev/blog/supply-chain; go.dev/ref/mod

**NuGet: split.** Legacy packages.config runs `install.ps1`/`init.ps1` automatically.
The modern default (PackageReference, SDK-style, `dotnet add package`) disables those
install scripts "because of security reasons" but auto-imports package-supplied
MSBuild `.props`/`.targets`, so a package can execute custom `<Target>`/`<Task>` at
build time. A validly signed package can still ship hostile targets. learn.microsoft.com/
nuget/consume-packages/migrate-packages-config-to-package-reference;
learn.microsoft.com/nuget/concepts/msbuild-props-and-targets

**Maven: plugins exec at build; plain deps do not (until exercised).** A plugin goal is
a Mojo whose `execute()` runs when its bound lifecycle phase is reached, so a squatted
plugin coordinate is arbitrary Java at build. A plain dependency is only placed on a
classpath; it runs when exercised, with two compile/test exceptions: an annotation
processor registered via `META-INF/services` is executed by `javac` during `mvn
compile`, and test code runs under Surefire during `mvn test`. maven.apache.org/guides/
introduction/introduction-to-the-lifecycle.html

## Risk-multiplier summary

| Ecosystem | Auto-exec | One-line risk |
|-----------|-----------|---------------|
| npm | INSTALL (default, transitive) | Highest: install alone detonates, on every dep, today |
| PyPI sdist | BUILD (during install-from-source) | High: pip builds the sdist; attacker ships sdist-only to force it |
| PyPI wheel | none at install (import-only) | Low at install: unzip; payload waits for first import |
| RubyGems native-ext | INSTALL | High: extconf.rb compiled/run at `gem install` |
| RubyGems pure-Ruby | none at install (require-only) | Low-moderate: runs on `require` |
| Cargo | BUILD/COMPILE (not add/fetch) | Moderate-high: first `cargo build` runs build.rs + proc-macros, unsandboxed |
| Go | none (import + build + run only) | Lowest: inert until imported and the program/tests run |
| NuGet packages.config | INSTALL (legacy) | High: install.ps1/init.ps1 auto-run |
| NuGet PackageReference | BUILD (MSBuild targets) | Moderate: install scripts off, but package targets run at build |
| Maven plugin | BUILD | High: squatted plugin runs Mojo execute() at build |
| Maven plain dep | none until exercised | Low-moderate: compile-time exec only via annotation processor |

**Headline argument.** npm, PyPI-via-sdist, RubyGems-native-ext, and legacy NuGet make
a squat immediately dangerous (install-time detonation puts dev-workstation and CI
credentials one step away). Cargo, Maven plugins, and modern NuGet are build-time, one
workflow step removed but effectively certain to fire in CI. Go, wheels, pure-Ruby, and
plain Maven deps are latent, requiring the squat to be imported and the path reached,
which gives defenders time and shrinks blast radius. A registry where install
auto-executes is a categorically higher-priority target for typosquat defense, and pi(t)
should carry an ecosystem-and-artifact execution-tier multiplier, not just download
counts.

## Attacker economics

Cost and friction approach zero; payoff is a full pipeline compromise. Publisher
accounts are free and self-service, publishing is automated and unvetted, so one
operator can script hundreds of typo-permuted uploads in hours. The multiplier is
install/build-time auto-execution. The prize is not the workstation but the secrets in
dev and CI environments (GitHub PATs, cloud keys, SSH keys, and especially registry
publish tokens, which enable self-propagation as in the 2025 Shai-Hulud npm worm).
Dependency confusion sharpens this: a public package matching a private internal name
at a high version is auto-preferred, with no typo and no social engineering. Because one
squat is pulled by many downstream victims and the register-to-execute-to-harvest-to-
republish chain is scriptable, the attack scales like software rather than manual
intrusion.

Measured figures (attribute carefully; vendor telemetry, not independent):
- ~512,847 malicious OSS packages Nov 2023 to 2024, +156% YoY, npm ~98.5% (Sonatype 10th
  SSSC, 2024).
- >454,600 new malicious packages in 2025, cumulative >1.233M, >99% on npm (Sonatype 2026),
  the npm share inflated by mass spam like the tea.xyz flood.
- Counter-trend: classic simple typosquats declined >70% 2023 to 2024 and PyPI malware
  fell sharply (ReversingLabs 2025 retrospective) as attackers shifted to account
  takeover and token farming. Do not present a single "typosquat share" as settled; the
  Sonatype-rising and ReversingLabs-declining numbers are compatible under different
  definitions.
- 45,816 exposed secrets across npm/PyPI/NuGet/RubyGems in 2024, npm+PyPI ~95%
  (ReversingLabs).

## Caveats to carry into the paper

- npm v12 opt-in default flip is announced, not confirmed GA; state the live default as
  scripts-run and re-check.
- "Typosquat share" is definition- and vendor-dependent; report ranges, not point claims.
- Unverified against primary docs (do not assert): Sigstore artifact signing for
  RubyGems/crates consumer build-provenance; exact `init.ps1`-under-PackageReference 2026
  wording; a first-party Maven dependency-verification tool. Trusted Publishing / OIDC is
  the confirmed 2025 hardening for crates, RubyGems, and NuGet.
- A few verbatim block quotes were paraphrased from primary-domain text under fetch
  rate-limiting; re-lift exact quotes from the cited pages before camera-ready.

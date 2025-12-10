# Package Publication Workflow

This document describes the step-by-step process for publishing Promethium packages to their respective registries.

## Pre-requisites

All packages must pass their test suites before publication.

| Package | Test Command | Status |
|---------|--------------|--------|
| promethiumR | `devtools::test()` | Passed (67/67) |
| Promethium.jl | `Pkg.test()` | Passed (44/44) |
| promethium-scala | `sbt test` | Passed |

---

## R: CRAN Submission

### Build Tarball

```bash
cd packages/promethiumR
R -q -e "devtools::build(path = '../dist')"
```

This produces `dist/promethiumR_1.0.4.tar.gz`.

### CRAN Check (Requires Rtools on Windows)

```bash
R CMD check --as-cran dist/promethiumR_1.0.4.tar.gz
```

### Submission

**Human Action Required:**

1. Navigate to [CRAN Submission Portal](https://cran.r-project.org/submit.html)
2. Upload `promethiumR_1.0.4.tar.gz`
3. Provide maintainer email matching `DESCRIPTION`
4. Complete email verification
5. Address any reviewer feedback (typically 2-10 business days)

---

## Julia: General Registry

### Create Release Tag

```bash
git tag -a v1.0.4 -m "Promethium.jl v1.0.4"
git push origin v1.0.4
```

### Register with JuliaRegistrator

**Human Action Required:**

1. Navigate to the tagged commit on GitHub
2. Comment: `@JuliaRegistrator register`
3. Wait for automated checks
4. Monitor and merge the PR to [Julia General Registry](https://github.com/JuliaRegistries/General)

---

## Scala: Maven Central

### Configure Credentials

Create `~/.sbt/1.0/sonatype.sbt`:

```scala
credentials += Credentials(
  "Sonatype Nexus Repository Manager",
  "s01.oss.sonatype.org",
  "<username>",
  "<password>"
)
```

### Configure GPG

```bash
gpg --full-generate-key
gpg --keyserver keyserver.ubuntu.com --send-keys <KEY_ID>
```

### Publish

```bash
cd packages/promethium-scala
sbt +publishSigned
sbt sonatypeBundleRelease
```

**Human Action Required:**

1. Configure Sonatype OSSRH credentials
2. Generate and publish GPG signing key
3. Close and release staging repository at [Sonatype Nexus](https://s01.oss.sonatype.org/)

---

## Post-Publication Verification

After publication, verify package availability:

| Package | Verification URL |
|---------|------------------|
| promethiumR | https://CRAN.R-project.org/package=promethiumR |
| Promethium.jl | https://juliahub.com/ui/Packages/Promethium |
| promethium-scala | https://search.maven.org/artifact/io.github.olaflaitinen/promethium-scala_2.13 |

Once verified, update `docs/distribution.md` status and README badges.

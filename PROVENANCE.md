# Provenance Register

## Scope

This register covers the files in the SasteraTech Agent Runtime public source
candidate. It records origin categories and verification limits; it is not a
legal opinion or a guarantee that no third party will ever assert a claim.

## Project-authored material

- `src/sasteratech_runtime/**`: project-authored Python implementation,
  normalized from the private predecessor's internal namespace before first
  public release.
- `tests/**`: project-authored unit, regression and contract tests.
- `evals/**`: project-authored synthetic fixtures and thresholds. They contain
  no known customer or provider response corpus.
- `schemas/**`, `roles/**`, `skills/**`: project-authored machine-readable
  contracts and examples.
- `scripts/**`, `config/**`, `container/**`: project-authored operational and
  verification utilities.
- Markdown documentation other than quoted licence text: project-authored
  synthesis informed by the references listed in `SOURCE_REGISTER.md`.

An internal normalized-line comparison against installed Pydantic AI,
Pydantic AI Harness, Pydantic Graph and Pydantic Evals packages found no
matching local code sequence at the tested six-line and ten-line thresholds.
This is useful negative evidence, not proof against every possible source.

## Externally sourced text and metadata

- `LICENSE`: Apache License 2.0 licence text from the Apache Software
  Foundation, with the standard appendix notice completed for this work.
- `THIRD_PARTY_NOTICES.md` and `sbom.cdx.json`: generated from the hashed
  runtime lock and locally installed distribution metadata.
- URLs and framework names in `SOURCE_REGISTER.md`: factual citations and
  attribution; referenced source code is not vendored by those citations.

## AI assistance

AI tools assisted with architecture, drafting, mechanical namespace migration,
tests and review. The copyright owner remains responsible for human review,
provenance, licence selection and publication decisions. AI output is not
assumed to be unique merely because it was generated.

## Deliberately excluded material

The public candidate excludes private evidence, live provider responses,
credential identifiers, OS-keyring contents, API tokens, local databases,
machine-specific state, virtual environments, generated caches and evidence
bundles. Those exclusions are enforced by `scripts/verify_public_release.py`.

## Contribution requirement

Every contributor must have the right to submit their contribution. Copied or
adapted third-party material must identify its source, licence and required
notices. Material with unclear provenance must not be merged.


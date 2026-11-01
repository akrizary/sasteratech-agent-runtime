# Contributing to SasteraTech Agent Runtime

## Contribution status

This source candidate is prepared for an eventual public repository. External
contributions may be accepted only after the repository enables a private
security-reporting route and publishes its maintainer workflow.

## Before contributing

- Read `README.md`, `SECURITY.md`, `TRADEMARKS.md`, and
  `docs/OPEN_CORE_AND_COMMERCIAL_BOUNDARY.md`.
- Use an issue or proposal before a large architectural change.
- Never submit provider keys, local API tokens, credential identifiers, private
  prompts/responses, personal data, local databases, or evidence bundles.
- Report security vulnerabilities privately through the route documented in
  `SECURITY.md`; do not open a public security issue.

## Contribution workflow

1. Make a focused change with a clear purpose.
2. Add or update tests for changed behaviour.
3. Run the package validation and relevant focused tests.
4. Describe behavioural, security, compatibility, and rollback impact.
5. Disclose material AI assistance and confirm that a human reviewed the final
   contribution for correctness, provenance, secrets, and third-party copying.
6. Use a `Signed-off-by` line to certify that you have the right to submit the
   contribution under the project's contribution terms.

The public repository uses the Developer Certificate of Origin process
documented at <https://developercertificate.org/> unless the project owner
adopts a different written contributor agreement.

## Licence of contributions

Contributions intentionally submitted for inclusion are provided under the
Apache-2.0 inbound contribution terms in section 5 unless the contributor and
maintainer state a separate written agreement. A contribution does not
transfer a trademark or place private/commercial modules into the public core.

## Brand use

Contribution acceptance does not grant ownership of or permission to present a
fork, service, package, or organisation as the official SasteraTech Agent Runtime product.
See `TRADEMARKS.md`.

## Review standard

Changes may be rejected or held when evidence is missing, risk boundaries are
unclear, tests do not cover the change, provenance is uncertain, or the change
would expose private state or weaken fail-closed behaviour.

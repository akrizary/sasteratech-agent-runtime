# Changelog

## v1.1.0a2 — 2026-11-02

- Added the dependency-free SasteraTech Capability Gate for bounded local skill
  contract, permission, prompt-injection, dangerous-code and provenance checks.
- Added deterministic JSON and SARIF output with fail-closed `REJECT` and
  `INCOMPLETE` verdicts.
- Added adversarial skill-security fixtures and made bundled-skill scanning part
  of the offline public-release gate.
- Added an isolated release-CI job for NVIDIA SkillSpector, pinned to an exact
  upstream revision with LLM analysis disabled and no provider credentials.
- Kept remote ingestion, arbitrary-path MCP scanning, automatic repair and LLM
  semantic scanning disabled.

## v1.1.0a1 — 2026-11-01

- Added the installed `sasteratech-runtime` CLI with read-only `doctor` and
  redacted `status` commands.
- Added a local stdio MCP adapter for Codex and Claude Code with exactly three
  read-only tools and no provider dispatch, credential access, network action,
  or mutation capability.
- Added portable, non-creating state-directory discovery and public onboarding
  documentation.
- Added the MCP SDK as an exact optional dependency and cross-platform contract
  coverage using the hashed runtime environment.

## v1.1.0a0 — 2026-10-30

- Created as a separate working package; v1.0 remains an immutable evidence release.
- Added Windows-local BYOK control-plane primitives: credential-store abstraction, budget reservations, redacted hash-chained audit events, persistent kill switches, and DeepSeek Flash allowlisting.
- Added offline tests using an in-memory credential-store double; no real credential or live provider call is used by the test suite.
- LiteLLM, Keycloak, OPA, OpenBao, hosted tenancy, and external write tools remain deferred to later phases.

## v1.0.0 — 2026-10-30

- Created from v0.9.6 only after the imported DeepSeek evidence run passed the v1 gate with no blockers.
- Retained the accepted imported evidence, attestation, run manifest, and birth certificate.
- This release artifact does not authorize deployment or publication.

## v0.9.6 — 2026-10-30

- Preserved the failed v0.9.5 run as immutable evidence.
- Aligned the no-tool provider-matrix token budget with the approved 512-token operational probe budget while retaining the 45-second timeout and every smoke limit.

## v0.9.5 — 2026-10-30

- Restored the verified hash-locked runtime dependency file as a tracked canonical artifact.
- Made offline package validation fail when the runtime lock is absent.
- Preserved v0.9.4 as an immutable predecessor; no live provider run was attempted from it.

## v0.9.4 — 2026-10-30

- Preserved the failed v0.9.3 DeepSeek run as a separate historical record; it cannot be overwritten or exported as passing evidence.
- Added immutable named live-run directories and run manifests with no-retry provenance.
- Bound evidence export, import, and gate evaluation to one selected imported run.
- Normalized live evidence provenance to v0.9.4 and retained the approved smoke limits unchanged.

## v0.9.3 — 2026-10-30

- Preserved v0.9.2 and its rejected live evidence as a frozen predecessor.
- Excluded `LIVE_ATTESTATION.json` from its own evidence-source hash map.
- Restored importable self-consistent evidence bundles.

## v0.9.2 — 2026-10-30

- Preserved v0.9.1 and its incomplete live evidence as a frozen predecessor.
- Raised bounded total-token budgets for DeepSeek operational and real-shadow calls.
- Persisted structured real-shadow failure evidence instead of only throwing a traceback.
- Required a hashed runtime lock and approved local SLO policy before live provider calls.

## v0.9.1 — 2026-10-30

- Preserved v0.9 as a frozen predecessor and introduced a separate v0.9.1 artifact.
- Added DeepSeek credential-presence evidence without collecting secret values.
- Replaced static real-shadow execution with a no-tool live generation path.
- Rejected pre-written shadow proposals and required generated-proposal provenance.
- Configured approved birth/smoke SLO limits with fail-closed cost evidence.

## v0.9 — 2026-10-30
- Added Live Validation Pack and evidence contract.
- Added isolated Linux/macOS and Windows bootstrap scripts.
- Added live environment capture without secret values.
- Added frozen no-tool live trajectory policy dataset.
- Added provider matrix and controlled live failover runners.
- Added operational baseline/SLO collection with fail-closed unconfigured thresholds.
- Added live evidence export/import with manifest and file hash verification.
- Added v1 evidence gate evaluator; it never authorizes deployment.
- Added v0.9 live-validation regression tests.
- Production remains blocked until external live evidence is collected.

## v0.8 — 2026-10-29
- Added production release gate separating offline candidate readiness from production readiness.
- Added exact verified top-level Pydantic runtime pins (2.63.0 / Harness 0.63.0).
- Added hashed transitive lock generator and non-root container recipe.
- Added runtime-import and live-provider compatibility probes.
- Added crash/recovery and migration/rollback drills.
- Hardened non-idempotent EffectLedger replay after VERIFIED state.
- Added deterministic provider failover logic and tests.
- Added real-shadow evaluator including high-risk false-negative detection.
- Added SLO framework that leaves latency/error/retry/cost targets unconfigured until measured.
- Added machine-readable Birth Candidate report.
- Production remains blocked pending live runtime, real shadow, hashed lock, live failover and operational SLO evidence.

## v0.7 — 2026-10-29
- Replaced flat keyword router with Domain × Procedure × Action/Risk routing.
- Separated risk mentions from explicit risky action intent.
- Added actual deterministic SkillRouter and used it in skill-reach evaluation.
- Added temporal memory validity, supersession, transaction-time and scope semantics.
- Added SQLite temporal memory repository and schema v5.
- Added frozen v0.6 corpus SHA-256 enforcement.
- Added v0.7 multi-axis and temporal-memory evals.
- Corrected shadow fixture interpretation without changing its frozen data.
- Removed Python cache artifacts from canonical ZIP.

## v0.6 — 2026-10-29
- Added dependency-free executable T0–T7 evaluation framework.
- Added routing corpus with risk-word negative controls.
- Added classification and skill-reach metrics: entrypoint, reachability, MRR, F1, redundancy and abstention.
- Added deterministic trajectory evaluator.
- Added adversarial, memory and safety core probes.
- Added regression thresholds/gates and frozen dataset hashing.
- Added production-shadow evaluator with synthetic fixture.
- Added model/provider A-B experiment design.
- Added eval_runs/eval_results persistence; SQLite schema v4.
- Added generated EVAL_REPORT.json and EVAL_SCORECARD.md.
- Live provider/model experiments and real production shadow remain unexecuted.

## v0.5 — 2026-10-29
- Added ToolGateway as mandatory side-effect boundary.
- Added durable ApprovalService and approval_requests table.
- Hardened R2-R4 authorization to human-issued grants only.
- Added executable tool runtime specs with validators/readback verification.
- Added semantic risk judge interface with BLOCK/ESCALATE semantics.
- Added prompt-injection defender and untrusted-data wrappers.
- Added secret detection/redaction and network exfiltration blocking.
- Added tool effect ledger, idempotency and replay protection.
- Added reconciliation API and post-action verification.
- Added structured contradiction scanner.
- Upgraded persistence schema to v3.
- Added security/adversarial regression tests.
- Bound R2-R4 grants to run + action + tool + resource + expiry.
- Blocked understated tool risk and out-of-scope resources.
- Enforced readback contract for R2+ side effects by default.
- Added tested v2→v3 database migration path.
- Added fail-closed handling when a required semantic judge is unavailable.
- No production or external mutation performed by build process.

## v0.4 — 2026-10-29
- Added model/provider registry with role constraints and environment-resolved model IDs.
- Added RuntimeAdapter/RuntimeRegistry and typed runtime contracts.
- Added deterministic MockRuntimeAdapter.
- Added lazy reasoning-only Pydantic AI adapter.
- Mapped SasteraTech budgets to documented Pydantic UsageLimits and run timeout surfaces.
- Added ORCHESTRATOR role with coordination-only direct tools.
- Added runtime call persistence and schema version 2.
- Added framework-neutral SasteraTech checkpoints.
- Added NervousSystem execution, delegation and bounded fan-out.
- Added telemetry sinks, secret redaction and optional OpenTelemetry bridge.
- No model mutation tools enabled.
- Live Pydantic import/provider call not claimed because dependencies could not be installed in the build environment.

## v0.3 — 2026-10-29
- Added nine capability-based worker roles.
- Added machine-readable role manifests and schema.
- Added immutable TaskPacket + TaskBudget.
- Added DelegationEngine with depth/risk/tool/budget/scope narrowing.
- Added ActionIntent and CapabilityGuard.
- Added independent verification contract.
- Added deterministic OrganRouter.
- Added role/delegation/capability regression tests.
- No model API, network mutation or deployment enabled.

## v0.2 — 2026-10-29
- SQLiteStore with WAL, foreign keys and migration table.
- RunRepository.
- Dependency-aware PlanGraph with cycle detection.
- Budgeted ContextAssembler.
- Append-only hash-chained EventLog.
- ArtifactRegistry with SHA-256 verification.
- ConfigLoader with deterministic environment overrides.
- Persistent-cell documentation and regression tests.
- No external mutation/deployment.

## v0.1 — 2026-10-29
- Initial genome, router, policy, evidence/memory contracts, runtime adapter boundary and deterministic zygote.

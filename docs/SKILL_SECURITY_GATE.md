# Skill Security Gate

## Purpose

Agent skills are executable capability packages, not trusted documentation.
SasteraTech requires two independent review lines before a bundled skill is
eligible for release:

1. **SasteraTech Capability Gate** — deterministic, dependency-free contract
   and policy analysis implemented by this project.
2. **NVIDIA SkillSpector** — an external static scanner executed in an isolated
   release-CI job at an exact source revision.

Neither scanner is a sandbox, a signature verifier, or proof that a skill is
safe. Runtime permission enforcement and human review remain authoritative.

## Local deterministic scan

```powershell
sasteratech-runtime scan-skill .\skills\example_research
sasteratech-runtime scan-skill .\skills\example_research --format sarif
python scripts\verify_skill_security.py
```

The command accepts only an existing local directory. It does not clone URLs,
download archives, execute target code, import target Python, call a provider,
or access the network. Reports contain relative inventory paths and content
hashes, not absolute machine paths.

Verdicts:

- `PASS` — complete bounded analysis with no medium-or-higher finding.
- `CAUTION` — complete analysis with a medium finding; manual review required.
- `REJECT` — a high or critical policy violation was found.
- `INCOMPLETE` — some relevant content could not be inspected; fail closed.

The CLI exits zero only for `PASS`, one for every other verdict, and two when
the scanner itself cannot start or its policy is invalid.

## What the internal gate checks

- required `SKILL.md`, `skill.json`, and `evals.jsonl` files;
- manifest types, risk ceiling, tool conflicts, and wildcard permissions;
- positive and negative route-evaluation coverage;
- bounded file count, size, depth, UTF-8 decoding, and unsupported content;
- symlinks, hidden Unicode controls, encoded payloads, hidden instructions,
  prompt override, credential exfiltration, and destructive commands;
- Python AST calls for dynamic evaluation, subprocess and shell execution;
- mismatch between observed capabilities and declared `allowed_tools`; and
- capabilities that exceed the declared risk ceiling.

Static analysis can produce false positives and false negatives. A clean scan
does not replace code review, sandboxing, permission checks, provenance, or
runtime observability.

## External SkillSpector boundary

The external job is not a runtime dependency and is not imported by the
SasteraTech package. It runs on an ephemeral standard GitHub-hosted Ubuntu
runner with:

- `contents: read` only;
- checkout credentials disabled;
- no LLM analysis or provider key;
- an exact upstream source commit;
- dependency installation from that commit's frozen `uv.lock`;
- `--fail-on-findings`, `--fail-on-incomplete`, and full canonical coverage;
  any finding therefore stops unattended CI until it is reviewed; and
- report files confined to the runner temporary directory.

Even with `--no-llm`, SkillSpector may send declared dependency coordinates to
OSV.dev for vulnerability lookup. Therefore this external job is intentionally
separate from `offline-core`. It must never receive BYOK credentials, release
tokens, private evidence, or customer data.

## Combined policy

| Internal gate | External gate | Release result |
|---|---|---|
| PASS | PASS | Eligible for the remaining release gates |
| CAUTION | PASS | Manual review required |
| PASS | CAUTION | Manual review required |
| REJECT | Any | Blocked |
| Any | Rejecting result | Blocked |
| INCOMPLETE/ERROR | Any | Blocked |
| Any | INCOMPLETE/ERROR | Blocked |

An exception must identify the exact finding fingerprint, owner, justification,
and expiry. Broad or permanent suppressions are not accepted by this phase.

## Deferred surfaces

- Arbitrary-path scanning through MCP is not exposed in this phase.
- Remote URL ingestion and archive extraction are not implemented internally.
- LLM semantic scanning requires separate data-risk and cost approval.
- Automated installation, repair, suppression, or deletion is forbidden.

## Third-party identity and licence

SkillSpector is an NVIDIA project licensed under Apache License 2.0. It is used
as an unmodified external CI tool and is not bundled, forked, or represented as
a SasteraTech product. “NVIDIA” and “SkillSpector” identify their respective
third-party project only.

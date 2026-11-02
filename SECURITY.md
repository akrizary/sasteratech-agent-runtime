# Security Policy

## Current status

SasteraTech Agent Runtime v1.1 is an alpha source candidate. It is not a hosted
service and does not authorise production deployment.

The first public release is blocked until a private vulnerability-reporting
route is configured. Do not place vulnerability details, credentials, local
tokens, personal data, or exploit instructions in a public issue.

## Planned reporting route

The public GitHub repository must enable private vulnerability reporting before
its first release. Report vulnerabilities through the repository's **Security**
tab and private-reporting form. Do not open a public issue containing exploit,
credential, personal-data or tenant-boundary details. If private reporting is
not available, the maintainer must publish a private security contact before
releasing a package.

Expected private-reporting route after publication:
<https://github.com/akrizary/sasteratech-agent-runtime/security/advisories/new>

## Credential incident response

If a provider key, local API token, or other secret may have been exposed:

1. revoke or rotate it at the issuing provider immediately;
2. stop the affected local service;
3. do not paste the secret into an issue, log, screenshot, or chat;
4. remove the secret from working files and candidate release history;
5. run the clean-export secret scan; and
6. record only non-secret incident evidence and remediation status.

Deleting a secret from the latest file is not sufficient if it entered Git
history or a published artifact.

## Security boundaries

- BYOK secrets must remain outside client-visible state and public artifacts.
- The local API binds to loopback by default.
- Provider dispatch and mutation capabilities are disabled unless explicitly
  enabled by a separately validated policy and approval path.
- Missing cost, permission, identity, or evidence information fails closed.
- A green offline test does not prove hosted, multi-tenant, or production
  security.

## Agent-skill intake

Bundled skills must pass the deterministic SasteraTech Capability Gate and the
independent external release-CI scan described in `docs/SKILL_SECURITY_GATE.md`.
An incomplete scan is not a clean scan. Neither scanner executes target code,
and neither replaces sandboxing, provenance review, runtime permissions, or
human review of high-impact capabilities.

The external scanner runs without LLM credentials. It may query OSV.dev with
declared dependency names and versions, so private skills and customer content
must not be placed in that public-repository workflow.

## Supported versions

No released version is currently supported. The first GitHub release must add
a supported-version table before claiming security support.

## No bounty or SLA

There is currently no bug bounty, paid reward, guaranteed response time, or
security SLA.

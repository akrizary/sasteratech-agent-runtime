# Public Source Candidate Readiness

**Assessment date:** 2026-11-02
**Candidate version:** `1.1.0a2`
**Release status:** `PUBLISHED_GITHUB_PRERELEASE`
**Publication authorised:** Exact scoped GitHub prerelease only
**Production deployment authorised:** No

## Verified

- Public identity: **SasteraTech Agent Runtime**.
- Distribution name: `sasteratech-agent-runtime`.
- Import namespace: `sasteratech_runtime`.
- Project-authored source licence: Apache-2.0.
- Copyright notice: Mohammad Akri bin Eddy Akhyar, 2026.
- Publishable manifest: 298 files at the immutable release tag.
- Offline test suite: 139 tests executed; 138 passed and one loopback HTTP
  integration test was explicitly skipped because the execution sandbox
  forbids local client sockets.
- Runtime lock: 98 packages with required hashes; the dependency set is
  unchanged from the accepted `1.1.0a0` lock.
- SBOM: all 98 locked packages represented with non-empty licence metadata.
- Private-material exclusion: no evidence tree, state tree, local database,
  virtual environment, credential bundle, cache or release archive is present.
- Tag `v1.1.0a2` and the GitHub prerelease point to exact commit
  `e251282f66d2111b83ccd64d04417d11e6d451ec`.
- Wheel: two independent builds and the asset downloaded back from the public
  release produced the same SHA-256:
  `adb689e9a75c1b80e473e740ba4e09ae21a55b84145e30e7be363fc10c29edb3`.
- Anonymous public installation: the checksum-bound GitHub Release URL
  installed version `1.1.0a2` in a clean virtual environment.
- Installed CLI: `doctor` and `status` returned bounded JSON without creating
  a state directory or attempting network access.
- SQLite read-only paths: a regression case containing URI-special `#` read
  the intended database through an encoded file URI without creating a sibling
  file or changing the database bytes.
- Installed MCP contract: exactly `runtime_health`, `runtime_status`, and
  `validate_run_contract` were registered with read-only, non-destructive
  annotations using the locked MCP 2.3.0 SDK.
- Public MCP installation and stdio canary: the public wheel resolved MCP
  `2.3.0`; a real SDK client launched it in a child process, initialized a
  session, listed the exact three-tool allowlist, and shut down without state.
- Public-release verifier and package validator: PASS with zero failures for
  the 298-entry release manifest.
- Exact-tag hosted CI: Windows, Ubuntu and the isolated skill-security workflow
  passed against the release commit.
- GitHub controls: private vulnerability reporting is enabled; `main` requires
  strict Windows and Ubuntu CI, admin enforcement, linear history and resolved
  conversations, with force-push and deletion disabled.
- Workflow supply chain: official checkout and Python setup actions are pinned
  to the full commit SHAs of their verified upstream releases.

## Not yet verified

- Docker image build: NOT_TESTED because Docker is unavailable locally.
- Codex and Claude Code application-level connections: NOT_RUN. The underlying
  MCP stdio process handshake passed; each client configuration remains a
  separate user-environment canary.
- Independent external-user feedback: NOT_YET_RECEIVED.
- Live provider calls under the renamed package: NOT_RUN. Historical provider
  evidence belongs to the private predecessor and was deliberately excluded.
- PyPI publication and cloud deployment: NOT_RUN and not authorised.

## Release decision

`v1.1.0a2` is released as a bounded GitHub alpha prerelease and is suitable for
public installation canaries. It is not a hosted service or production
deployment. Promotion to `v1.1.0b1` should wait for at least one independent
Codex or Claude client canary and review of any reported onboarding defects.

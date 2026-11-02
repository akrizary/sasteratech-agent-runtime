# Public Source Candidate Readiness

**Assessment date:** 2026-11-01  
**Candidate version:** `1.1.0a1`
**Local status:** `PASS_LOCAL_SOURCE_CANDIDATE`  
**Publication authorised:** No  
**Production deployment authorised:** No

## Verified locally

- Public identity: **SasteraTech Agent Runtime**.
- Distribution name: `sasteratech-agent-runtime`.
- Import namespace: `sasteratech_runtime`.
- Project-authored source licence: Apache-2.0.
- Copyright notice: Mohammad Akri bin Eddy Akhyar, 2026.
- Publishable manifest: 290 files.
- Offline test suite: 127 tests executed; 126 passed and one loopback HTTP
  integration test was explicitly skipped because the execution sandbox
  forbids local client sockets.
- Runtime lock: 98 packages with required hashes; the dependency set is
  unchanged from the accepted `1.1.0a0` lock.
- SBOM: all 98 locked packages represented with non-empty licence metadata.
- Private-material exclusion: no evidence tree, state tree, local database,
  virtual environment, credential bundle, cache or release archive is present.
- Wheel: two independent builds produced the same SHA-256:
  `1d149764f8c85e4c4583a81773af4c66aebfa7412004fd43512580626a2c6d69`.
- Wheel installation: installed without dependency or index access; the
  `sasteratech-runtime` console command and version `1.1.0a1` were verified.
- Installed CLI: `doctor` and `status` returned bounded JSON without creating
  a state directory or attempting network access.
- SQLite read-only paths: a regression case containing URI-special `#` read
  the intended database through an encoded file URI without creating a sibling
  file or changing the database bytes.
- Installed MCP contract: exactly `runtime_health`, `runtime_status`, and
  `validate_run_contract` were registered with read-only, non-destructive
  annotations using the locked MCP 2.3.0 SDK.
- Installed MCP stdio canary: a real SDK client launched the wheel in a child
  process, initialized a session, listed the exact three-tool allowlist, and
  shut the process down successfully without creating state.
- Public-release verifier and package validator: PASS with zero failures after
  the 290-entry manifest was regenerated.
- Workflow supply chain: official checkout and Python setup actions are pinned
  to the full commit SHAs of their verified upstream releases.

## Not yet verified

- Docker image build: NOT_TESTED because Docker is unavailable locally.
- Linux and Windows hosted CI: NOT_RUN for this `1.1.0a1` candidate until an
  exact candidate commit is pushed under separate deployment approval.
- Codex and Claude Code application-level connections: NOT_RUN. The underlying
  MCP stdio process handshake passed; each client configuration remains a
  post-commit canary step.
- Live provider calls under the renamed package: NOT_RUN. Historical provider
  evidence belongs to the private predecessor and was deliberately excluded.
- PyPI publication and cloud deployment: NOT_RUN and not authorised.

## Release decision

The local source tree is ready to become the `1.1.0a1` GitHub prerelease
candidate. It is not yet a committed or published `1.1.0a1` release, hosted
service, or production deployment. Commit/push, hosted CI, client canary, and
release publication require separate scoped deployment approval and exact-head
verification.

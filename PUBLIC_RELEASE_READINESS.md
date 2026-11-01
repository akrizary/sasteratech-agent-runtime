# Public Source Candidate Readiness

**Assessment date:** 2026-11-01  
**Candidate version:** `1.1.0a0`  
**Local status:** `PASS_LOCAL_SOURCE_CANDIDATE`  
**Publication authorised:** No  
**Production deployment authorised:** No

## Verified locally

- Public identity: **SasteraTech Agent Runtime**.
- Distribution name: `sasteratech-agent-runtime`.
- Import namespace: `sasteratech_runtime`.
- Project-authored source licence: Apache-2.0.
- Copyright notice: Mohammad Akri bin Eddy Akhyar, 2026.
- Public-release verifier: PASS with zero reported failures.
- Publishable manifest: 283 files.
- Offline test suite: 119 tests executed; 118 passed and one loopback HTTP
  integration test was explicitly skipped because the execution sandbox
  forbids local client sockets.
- Runtime lock: 98 packages; hash-required dry-run parsed successfully in the
  validated Windows environment.
- SBOM: all 98 locked packages represented with non-empty licence metadata.
- Private-material exclusion: no evidence tree, state tree, local database,
  virtual environment, credential bundle, cache or release archive is present.
- Wheel: two independent builds produced the same SHA-256:
  `ac612b42eee6983420c9d446fa40a753602aa8493fd1ba6ad6d4193b180c477c`.
- Wheel installation: installed without dependency or index access; import,
  version `1.1.0a0`, and Apache-2.0 package metadata were verified.
- Private predecessor integrity: its separate 291-entry source manifest still
  verifies with no mismatch; it was not rewritten by this migration.
- GitHub preflight: authenticated owner `akrizary` was verified and no existing
  accessible repository named `akrizary/sasteratech-agent-runtime` was found.
- Workflow supply chain: official checkout and Python setup actions are pinned
  to the full commit SHAs of their verified upstream releases.

## Not yet verified

- Docker image build: NOT_TESTED because Docker is unavailable locally.
- Linux and Windows hosted CI: NOT_RUN because no public GitHub repository or
  commit exists yet.
- Live provider calls under the renamed package: NOT_RUN. Historical provider
  evidence belongs to the private predecessor and was deliberately excluded.
- Official trademark availability: NOT_CLEARED. Preliminary open-web searches
  found no indexed exact software/package collision for the new combined name,
  but WIPO and relevant national databases still require a manual exact and
  confusing-similarity search.
- Repository and package names: not reserved until the relevant external
  services accept them.

## Release decision

The local source tree is ready to become a GitHub publication candidate. It is
not yet a published release, hosted service or production deployment. External
repository creation, security settings, CI execution and release publication
must be separately authorised and verified against the exact resulting commit.

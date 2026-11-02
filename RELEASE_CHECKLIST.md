# Public Release Checklist

All items are fail-closed. A local PASS prepares a candidate; it does not
publish, deploy or create external accounts.

- [x] `scripts/verify_public_release.py` passes locally.
- [x] Full offline test suite passes from the clean candidate, with the
      sandbox-blocked loopback socket test explicitly reported as skipped.
- [x] `MANIFEST.sha256` validates after all tracked files are final.
- [x] `sbom.cdx.json` accounts for every package in the runtime lock.
- [x] `THIRD_PARTY_NOTICES.md` contains no unknown licence.
- [x] No evidence, state, database, virtual environment, archive or secret is
      present in the publishable tree.
- [x] The public repository, distribution identity and import namespace were
      confirmed through the published wheel installation.
- [x] The owner attested that manual trademark searches found no concerning
      similar marks; this is not a legal clearance opinion.
- [x] GitHub private vulnerability reporting is enabled.
- [x] `main` has strict Windows and Ubuntu required CI, admin enforcement,
      linear history, conversation resolution and no force-push or deletion.
- [x] Exact tag commit `e251282f66d2111b83ccd64d04417d11e6d451ec`
      passed tag-triggered Windows, Ubuntu and skill-security CI.
- [x] The GitHub prerelease received a separate scoped deployment approval.


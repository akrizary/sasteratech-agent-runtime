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
- [ ] Repository name, package name and import namespace are available at the
      time of publication.
- [ ] The owner manually searches WIPO and relevant national trademark
      databases for exact and confusingly similar marks.
- [ ] GitHub private vulnerability reporting is enabled.
- [ ] Branch protection and required CI are configured.
- [ ] The exact commit intended for release passes CI.
- [ ] Publication receives a separate deployment approval.


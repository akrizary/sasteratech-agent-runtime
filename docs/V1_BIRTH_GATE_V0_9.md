# v1 Birth Gate

v0.9.2 separates **evidence collection** from **release authorization**.

## Hard v1.0 production gate

Do **not** produce a v1.0 artifact from this pack until all of the following are
true:

1. v0.9.2 has passed its offline regression and the canonical pack has run in a clean, network-enabled environment with a hashed runtime lock and approved local SLO policy;
2. at least one configured real provider has completed the required live checks;
3. the generated `LIVE_EVIDENCE_BUNDLE.zip` has been returned to this project;
4. the returned bundle has passed integrity review and the v1 gate evaluator.

An offline candidate, synthetic fixture, credential-presence check, or an
unreturned evidence bundle is insufficient. This gate authorizes evidence
evaluation only; it does not deploy or authorize deployment.

For real-shadow evidence, manually populated proposals are invalid. The bundle
must prove that a no-tool live model generated the scored proposals.

The evaluator can return:
- `PASS_EVIDENCE_COMPLETE`
- `BLOCKED_MISSING_EVIDENCE`
- `FAIL_EVIDENCE`

It never deploys or authorizes deployment.

Required production evidence:
1. hashed runtime lock;
2. runtime import with exact versions;
3. minimal live provider probe;
4. live trajectory policy suite;
5. provider matrix or explicitly scoped single-provider decision;
6. controlled live failover evidence when failover is required;
7. operational baseline with configured thresholds;
8. representative real-shadow evidence;
9. zero unauthorized mutations;
10. zero high-risk false negatives.

Thresholds that are project/business-specific remain `null` until deliberately configured. A null production threshold blocks release instead of inventing a number.

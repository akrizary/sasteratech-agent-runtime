# Evidence Ledger

## Distinguish
- model assertion
- source statement
- tool observation
- inference
- verified result

## Claim

```json
{
  "claim_id": "CLM-001",
  "claim": "All 5,490 blobs passed hash verification",
  "status": "VERIFIED",
  "evidence": [{"kind": "tool_output", "ref": "EV-1001"}],
  "method": "full SHA-256 verification",
  "observed_at": "2026-10-29T00:00:00Z",
  "contradictions": []
}
```

## Completion gate
No success state unless every critical completion claim has fresh supporting evidence.

Examples:
- tests pass → test output;
- file saved → filesystem observation/hash;
- remote update succeeded → remote acknowledgement/read-back;
- no corruption → defined integrity procedure.

## Contradictions
Store conflicting propositions, evidence, temporal order and resolution state.
Unresolved material contradiction forces `PROVISIONAL` or `UNKNOWN`.

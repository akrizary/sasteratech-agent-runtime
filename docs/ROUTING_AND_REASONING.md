# Routing and Reasoning

## Pipeline
`request → domain → task → risk override → workflow → reasoning policy → tool filter`

## Stage A — deterministic boundary checks
Detect explicit writes/deletes/deployments, credentials, money, production systems and destructive verbs. These may force `HIGH_RISK`.

## Stage B — semantic classification
Choose primary and optional secondary task.

Example:
"Investigate why tests fail and patch it" = DEBUG primary + BUILD secondary.

## Reasoning depth
Scale by:
- stakes
- ambiguity
- evidence deficit
- reversibility
- novelty
- contradiction load

Not by prompt length.

## Escalation
- Three non-discriminating fixes → architecture-level diagnosis.
- Material source conflict → contradiction set before synthesis.
- Tool observation conflicting with memory → current observation wins provisionally and memory is flagged stale.

# Memory and Provenance

```text
EVENT LOG (immutable)
   ↓
WORKING MEMORY
   ↓
RETRIEVAL INDEXES
 lexical | vector | graph | temporal
   ↓
OBSERVATION LAYER
   ↓
CANDIDATE DURABLE MEMORY
   ↓
EVIDENCE + PROVENANCE + POLICY
   ↓
CANONICAL MEMORY
```

## Durable item metadata
- memory_id
- content
- type
- temporal validity
- source refs
- writer
- confidence/status
- supersedes/superseded_by
- TTL/review date
- sensitivity
- scope

## Types
FACT, PREFERENCE, DECISION, RULE, PROJECT_STATE, CANON, HYPOTHESIS, OPEN_QUESTION, PROCEDURE, LESSON.

## Observational memory
Background observer/reflector may compress old interaction into dense observations.
Observations remain candidate context, not canonical fact.

## Promotion
Candidate → canonical only when:
1. provenance exists;
2. required evidence is satisfied;
3. no unresolved higher-priority contradiction;
4. sensitivity policy permits storage;
5. temporal scope/TTL assigned where relevant.

## Retrieval fusion
Combine semantic similarity, lexical match, graph relation, recency/validity, authority, scope and task relevance.

`similarity ≠ relationship ≠ truth`.

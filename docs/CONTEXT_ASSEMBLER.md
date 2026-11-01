# Context Assembler

Context is a budgeted input package, not the entire corpus.

Priority classes: POLICY, ACTIVE_STATE, EVIDENCE, CANONICAL_MEMORY, RETRIEVAL, RECENT_DIALOGUE, AUXILIARY.

Required items are always selected or assembly fails. Optional items sort by priority/relevance and are included until budget exhaustion. Dropped items are reported. v0.2 uses `ceil(characters/4)` as a deterministic token approximation unless an explicit estimate is supplied.

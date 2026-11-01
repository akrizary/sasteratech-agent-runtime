# Agents / Organs v0.3

v0.3 implements worker-role contracts above the deterministic Cells core.

## Principle

An agent role is not a personality prompt. It is a **capability envelope**:

```text
ROLE
 ├─ allowed task classes
 ├─ risk ceiling
 ├─ tool allow patterns
 ├─ explicit denies
 ├─ delegation targets
 ├─ output contract
 ├─ evidence obligations
 └─ independence rules
```

## Implemented organs

1. **Researcher** — evidence acquisition and synthesis, read-only by default.
2. **Builder** — prepares/implements bounded local changes; cannot deploy.
3. **Debugger** — reproduce/isolate/patch/regress; bounded local mutation only.
4. **Reviewer** — adversarial review without mutating reviewed artifacts.
5. **Verifier** — independent proof of completion/effect.
6. **Risk Guardian** — policy/risk analysis; may block/escalate, never grant high-risk authority.
7. **Memory Curator** — candidate extraction/deduplication/promotion recommendation; canonical mutation remains gated.
8. **Synthesizer** — merges independent findings without expanding claims.
9. **Domain Specialist** — constrained subject-matter analysis with no implicit extra tools.

## Security properties

- Subagents do not inherit parent tools.
- A delegated task may only **narrow** the parent's risk ceiling and tool scope.
- Delegation depth is bounded.
- Role-to-role delegation uses an explicit graph.
- Reviewer/Verifier independence is machine-checkable.
- No role may delegate to itself recursively by default.
- Deployer is deliberately absent from v0.3; deployment remains a future explicitly gated organ.

## Runtime status

Workers in v0.3 are deterministic contracts and action-intent generators. They do not call an LLM, shell, network, GitHub, or deployment service.

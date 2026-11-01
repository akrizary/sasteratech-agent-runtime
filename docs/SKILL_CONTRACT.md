# Portable Skill Contract

A skill is a bounded procedure, not a mini operating system.

Required:
```text
skill-name/
  SKILL.md
  skill.json
  evals.jsonl
```

Machine fields:
id/version, purpose, positive/negative triggers, inputs/outputs, invariants,
workflow, allowed/forbidden tools, risk ceiling, evidence requirements,
completion conditions, failure modes, recovery and evals.

Descriptions must say when *not* to use the skill to reduce collisions.

A skill cannot install a second universal router that overrides the host.

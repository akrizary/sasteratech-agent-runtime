# Eval-Driven Rectification v0.7

v0.7 fixes failures discovered by v0.6 rather than hiding them.

## Rectification 1 — multi-axis routing

Old:
`text -> one TaskClass`

New:
`text -> Domain × Procedure × ActionIntent/Risk -> legacy TaskClass`

This distinguishes:
- mentioning production from deploying to production;
- discussing secrets from accessing secrets;
- creative-domain review from generic review;
- research about a failing test from authorization to patch it.

## Rectification 2 — temporal memory

Memory now carries:
- `valid_from`
- `valid_to`
- `supersedes`
- `superseded_by`
- `transaction_time`
- `scope`

Both an in-memory temporal store and SQLite repository are included.

## Rectification 3 — real skill routing eval

v0.6's skill-reach corpus included baked trajectories. v0.7 preserves the corpus but sends each frozen query through an actual deterministic SkillRouter and evaluates the resulting trajectory.

## Eval integrity

SHA-256 hashes of all v0.6 frozen corpora are stored in `evals/frozen_v0_6_hashes.json` and checked before every full eval run.

## Shadow fixture correction

The frozen shadow fixture deliberately includes one false positive and one false negative. Its F1=0.8 is therefore an input fixture property, not a harness quality result. v0.7 keeps the metric unchanged and adds `shadow.evaluator_selftest_pass` to verify the evaluator computes the expected errors correctly.

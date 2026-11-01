# Contradiction Scanner v0.5

v0.5 provides deterministic contradiction detection for **structured propositions**.

A proposition has:
- subject
- predicate
- value
- temporal interval / observation time
- source/evidence reference

Two propositions conflict when they address the same subject/predicate and overlapping temporal scope but incompatible normalized values.

The scanner does not pretend to solve arbitrary natural-language contradiction. Semantic contradiction detection belongs in the evaluation/review layer and must remain evidence-backed.

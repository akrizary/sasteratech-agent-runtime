# Live Trajectory Eval v0.9

The live trajectory suite is deliberately small and deterministic.

It tests whether the selected real model/runtime respects core SasteraTech policy distinctions in no-tool mode.

Cases include:
- risk mention vs risky action;
- self-authorization refusal;
- conflicting evidence uncertainty;
- current observation over stale memory;
- prompt injection inside quoted data;
- verification-before-completion discipline.

Each case requests one exact output token. This avoids using another model as the judge.

A pass means the model followed these frozen policy probes under the tested runtime. It does not prove general correctness.

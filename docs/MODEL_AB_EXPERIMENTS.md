# Model / Provider A-B Experiments

The experiment layer compares model/runtime candidates without changing SasteraTech safety policy.

Dimensions may include:
- task success;
- evidence quality;
- trajectory compliance;
- routing/handoff quality;
- token/cost;
- latency;
- unsupported claims;
- safety escalations.

The harness stores experiment results but v0.6 does not claim a live model ranking because no provider calls were executed in this build environment.

Never choose a model solely on aggregate quality if it violates a critical safety or evidence threshold.

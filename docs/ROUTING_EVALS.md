# Routing and Skill Reach Evals

SasteraTech implements metrics inspired by current skill-routing evaluation practice:

- Entrypoint Accuracy
- Trajectory Reachability
- Step Efficiency / MRR
- Skill Selection precision/recall/F1
- Redundancy
- Out-of-scope abstention/restraint

For a one-step deterministic router, entrypoint accuracy and reachability collapse to the same value. The generic metric implementation still supports multi-step trajectories so later agent handoffs can be measured without changing the score definition.

## Negative controls

Routing datasets intentionally include prompts that *mention* risky words without asking for risky actions, for example explanations of deployment/deletion. These reveal keyword-overtriggering.

A route may be safe yet still be wrong. Safety overrides and semantic intent should be evaluated separately.

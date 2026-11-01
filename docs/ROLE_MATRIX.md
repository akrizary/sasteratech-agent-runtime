# Role Matrix

| Role | Normal tasks | Risk ceiling | Typical tools | May delegate to |
|---|---|---:|---|---|
| Researcher | FACT_QUERY, RESEARCH | R0 | web.read, file.read | Domain Specialist, Synthesizer |
| Builder | BUILD | R2 | file.read/write, shell.test | Debugger, Reviewer, Verifier |
| Debugger | DEBUG | R2 | file.read/write, shell.test | Researcher, Reviewer, Verifier |
| Reviewer | REVIEW | R0 | file.read, shell.test | Researcher, Domain Specialist |
| Verifier | REVIEW | R1 | file.read, shell.test, remote.readback | Domain Specialist |
| Risk Guardian | HIGH_RISK, REVIEW | R0 | policy.read, evidence.read | none |
| Memory Curator | REVIEW, DATA | R1 | memory.read, evidence.read | Researcher |
| Synthesizer | RESEARCH, REVIEW | R0 | evidence.read, file.read | none |
| Domain Specialist | FACT_QUERY, RESEARCH, REVIEW | R0 | evidence.read, file.read | none |

## Notes

`risk ceiling` is a maximum capability envelope, **not authorization**. A Builder with R2 capability still requires a matching ApprovalGrant for an R2 action.

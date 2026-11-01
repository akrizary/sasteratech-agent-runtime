from pathlib import Path
import json
ROOT=Path(__file__).parents[1]; r=json.loads((ROOT/'EVAL_REPORT.json').read_text(encoding='utf-8')); g=r['gates']; m=r['metrics']
keys=['routing.accuracy','routing.high_risk_negative_control_accuracy','routing.axes_accuracy','skill.entrypoint_accuracy','skill.out_of_scope_restraint','adversarial.core_pass_rate','safety.core_pass_rate','memory.core_pass_rate','memory.temporal_pass_rate','shadow.evaluator_selftest_pass','shadow.fixture_f1']
lines=['# SasteraTech Agent Runtime v0.7 — Eval Scorecard','',f"**Critical offline gate:** {'PASS' if g.get('_critical_pass') else 'FAIL'}",'', '| Metric | Value | Gate | Critical |','|---|---:|---|---|']
for k in keys:
    spec=g.get(k,{}); val=m.get(k); passed=spec.get('passed') if spec else None
    lines.append(f"| `{k}` | {val:.3f} | {'PASS' if passed else ('FAIL' if passed is False else 'INFO')} | {'YES' if spec.get('critical') else 'no'} |")
lines += ['', '## Integrity', f"- Frozen v0.6 corpus verified: **{r.get('frozen_v0_6_verified',False)}**", '- `shadow.fixture_f1` remains 0.8 by design because the frozen evaluator fixture deliberately contains one FP and one FN; `shadow.evaluator_selftest_pass` is the correctness gate for that fixture.', '', '## Limitations']
for x in r.get('limitations',[]): lines.append('- '+x)
lines += ['', '## Readiness', '', 'Passing offline critical gates does **not** authorize production. Live provider compatibility, live trajectories, and real production-shadow evidence remain separate birth gates.']
(ROOT/'EVAL_SCORECARD.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

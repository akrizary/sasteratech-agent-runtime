from pathlib import Path
import sys,json,hashlib,datetime
ROOT=Path(__file__).parents[1]
sys.path.insert(0,str(ROOT/'src'))
from sasteratech_runtime.evals import SasteraTechEvalRunner

frozen=json.loads((ROOT/'evals'/'frozen_v0_6_hashes.json').read_text(encoding='utf-8'))['datasets']
for name,expected in frozen.items():
    actual=hashlib.sha256((ROOT/'evals'/'datasets'/name).read_bytes()).hexdigest()
    if actual!=expected: raise SystemExit(f'FROZEN_CORPUS_CHANGED:{name}')

baseline_path=ROOT/'evals'/'baseline_v0_6.json'
baseline=json.loads(baseline_path.read_text(encoding='utf-8')) if baseline_path.exists() else {}
report=SasteraTechEvalRunner(ROOT).run(baseline=baseline.get('metrics',{})); out=report.as_dict()
out['generated_at']=datetime.datetime.now(datetime.timezone.utc).isoformat(); out['frozen_v0_6_verified']=True; out['dataset_hashes']={}
for p in sorted((ROOT/'evals'/'datasets').glob('*.jsonl')): out['dataset_hashes'][p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
(ROOT/'EVAL_REPORT.json').write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({
 'suite_version':out['suite_version'],'outcomes':len(out['outcomes']),'critical_pass':out['gates'].get('_critical_pass'),
 'routing_accuracy':out['metrics'].get('routing.accuracy'),'risk_word_negative_control_accuracy':out['metrics'].get('routing.high_risk_negative_control_accuracy'),
 'routing_axes_accuracy':out['metrics'].get('routing.axes_accuracy'),'skill_entrypoint':out['metrics'].get('skill.entrypoint_accuracy'),
 'memory_pass_rate':out['metrics'].get('memory.core_pass_rate'),'temporal_memory':out['metrics'].get('memory.temporal_pass_rate'),
 'adversarial':out['metrics'].get('adversarial.core_pass_rate'),'safety':out['metrics'].get('safety.core_pass_rate'),
 'shadow_evaluator_selftest':out['metrics'].get('shadow.evaluator_selftest_pass'),'shadow_fixture_f1':out['metrics'].get('shadow.fixture_f1')
},indent=2))

import json,pathlib
from datetime import datetime,timedelta,timezone
from .models import EvalReport,EvalOutcome,EvalTier
from .metrics import classification_metrics,skill_reach_metrics
from .shadow import ShadowEvaluator
from .regression import RegressionGate
from ..router import route_task
from ..skill_router import SkillRouter
from ..injection import PromptInjectionDefender
from ..memory import MemoryGovernor,MemoryCandidate,TemporalMemoryStore
from ..contradictions import ContradictionScanner,StructuredProposition
from ..models import Risk,ApprovalGrant,ToolDefinition
from ..policy import PolicyEngine

class SasteraTechEvalRunner:
    def __init__(self,root):
        self.root=pathlib.Path(root); self.dataset_dir=self.root/'evals'/'datasets'
        self.thresholds=json.loads((self.root/'evals'/'thresholds.json').read_text(encoding='utf-8'))

    def _load(self,name):
        return [json.loads(x) for x in (self.dataset_dir/name).read_text(encoding='utf-8').splitlines() if x.strip()]

    def routing(self,report):
        cases=self._load('routing_v1.jsonl'); exp=[]; pred=[]; risk_neg=[]
        for c in cases:
            d=route_task(c['input']); actual=d.task.value; ok=actual==c['expected_task']
            exp.append(c['expected_task']); pred.append(actual)
            if c['kind']=='risk_word_negative_control': risk_neg.append(1.0 if ok else 0.0)
            report.outcomes.append(EvalOutcome(c['id'],EvalTier.T1,ok,1.0 if ok else 0.0,
                {'task':actual,'domain':d.domain.value,'procedure':d.procedure.value,'action':d.action.value,'risk':d.risk_floor.value},
                c['expected_task'],{'kind':c['kind'],'reasons':d.reasons,'frozen_v0_6':True}))
        m=classification_metrics(exp,pred)
        report.metrics['routing.accuracy']=m['accuracy']; report.metrics['routing.macro_f1']=m['macro_f1']
        report.metrics['routing.high_risk_negative_control_accuracy']=sum(risk_neg)/len(risk_neg) if risk_neg else 1.0
        report.metrics['routing.per_class']=m['per_class']

    def routing_axes(self,report):
        cases=self._load('routing_axes_v2.jsonl'); results=[]
        for c in cases:
            d=route_task(c['input'])
            actual={'domain':d.domain.value,'procedure':d.procedure.value,'action':d.action.value,'risk':d.risk_floor.value}
            expected={k:c[k] for k in ('domain','procedure','action','risk')}
            ok=actual==expected; results.append(ok)
            report.outcomes.append(EvalOutcome(c['id'],EvalTier.T1,ok,1.0 if ok else 0.0,actual,expected,{'v0_7_axis_eval':True}))
        report.metrics['routing.axes_accuracy']=sum(results)/len(results)

    def skill_reach(self,report):
        cases=self._load('skill_reach_v1.jsonl'); router=SkillRouter(self.root/'skills'); evaluated=[]
        for c in cases:
            traj=router.trajectory(c['query']); row=dict(c); row['trajectory']=traj; evaluated.append(row)
        m=skill_reach_metrics(evaluated)
        for k,v in m.items(): report.metrics[f'skill.{k}']=v
        for c in evaluated:
            target=c.get('expected_skill'); traj=c.get('trajectory',[]); oos=c.get('out_of_scope') or target is None
            ok=(not traj) if oos else bool(traj and traj[0]==target)
            report.outcomes.append(EvalOutcome(c['id'],EvalTier.T1,ok,1.0 if ok else 0.0,traj,target,
                {'out_of_scope':bool(oos),'actual_router':True,'frozen_v0_6_query':True}))

    def adversarial(self,report):
        cases=self._load('adversarial_v1.jsonl'); results=[]
        defender=PromptInjectionDefender(); gov=MemoryGovernor(); policy=PolicyEngine()
        for c in cases:
            typ=c['type']; ok=False; actual=None
            if typ=='prompt_injection':
                f=defender.inspect(c['text'],'UNTRUSTED_EXTERNAL'); actual='WITHHOLD' if f.withhold else f.severity.value; ok=actual==c['expected']
            elif typ=='memory_no_evidence':
                okp,_=gov.promotable(MemoryCandidate(c['id'],'claim','FACT',source_refs=['S'])); actual='ALLOW' if okp else 'BLOCK'; ok=actual==c['expected']
            elif typ=='memory_contradiction':
                okp,_=gov.promotable(MemoryCandidate(c['id'],'claim','FACT',source_refs=['S'],evidence_refs=['E'],unresolved_contradiction=True)); actual='ALLOW' if okp else 'BLOCK'; ok=actual==c['expected']
            elif typ=='llm_approval':
                tool=ToolDefinition('file.write','1',Risk.R2,True,True); g=ApprovalGrant('G',Risk.R4,('*',),('*',),'llm')
                actual='ALLOW' if policy.decide(tool,'/repo/a',(g,),run_id='R',action_id='A').allowed else 'BLOCK'; ok=actual==c['expected']
            elif typ=='scoped_approval_mismatch':
                tool=ToolDefinition('file.write','1',Risk.R2,True,True)
                g=ApprovalGrant('G',Risk.R2,('file.write',),('/repo/a',),'human',datetime.now(timezone.utc)+timedelta(hours=1),None,'R','OTHER')
                actual='ALLOW' if policy.decide(tool,'/repo/a',(g,),run_id='R',action_id='A').allowed else 'BLOCK'; ok=actual==c['expected']
            results.append(ok); report.outcomes.append(EvalOutcome(c['id'],EvalTier.T3,ok,1.0 if ok else 0.0,actual,c['expected']))
        report.metrics['adversarial.core_pass_rate']=sum(results)/len(results)

    def memory(self,report):
        cases=self._load('memory_v1.jsonl'); gov=MemoryGovernor(); results=[]
        for c in cases:
            typ=c['type']; actual=False; details={}
            if typ=='fact_without_evidence': actual=gov.promotable(MemoryCandidate(c['id'],'x','FACT',source_refs=['S']))[0]
            elif typ=='fact_with_evidence': actual=gov.promotable(MemoryCandidate(c['id'],'x','FACT',source_refs=['S'],evidence_refs=['E']))[0]
            elif typ=='contradicted_fact': actual=gov.promotable(MemoryCandidate(c['id'],'x','FACT',source_refs=['S'],evidence_refs=['E'],unresolved_contradiction=True))[0]
            elif typ=='sensitive_block': actual=gov.promotable(MemoryCandidate(c['id'],'x','FACT',source_refs=['S'],evidence_refs=['E'],sensitivity_ok=False))[0]
            elif typ=='temporal_supersession_capability':
                fields=set(MemoryCandidate.__dataclass_fields__); actual={'valid_from','valid_to','supersedes','superseded_by','transaction_time'}.issubset(fields); details={'fields':sorted(fields)}
            ok=actual==c['expected']; results.append(ok)
            report.outcomes.append(EvalOutcome(c['id'],EvalTier.T5,ok,1.0 if ok else 0.0,actual,c['expected'],details))
        report.metrics['memory.core_pass_rate']=sum(results)/len(results)

    def temporal_memory(self,report):
        cases=self._load('temporal_memory_v2.jsonl'); results=[]
        for c in cases:
            ok=False; actual={}
            if c['scenario']=='supersession':
                s=TemporalMemoryStore()
                old=MemoryCandidate('OLD','manager=A','FACT',['S1'],['E1'],valid_from=datetime(2025,1,1,tzinfo=timezone.utc),scope='project')
                new=MemoryCandidate('NEW','manager=B','FACT',['S2'],['E2'],valid_from=datetime(2026,1,1,tzinfo=timezone.utc),supersedes=['OLD'],scope='project')
                s.add(old); s.add(new)
                a25={m.memory_id for m in s.as_of(datetime(2025,6,1,tzinfo=timezone.utc),kind='FACT',scope='project')}
                a26={m.memory_id for m in s.as_of(datetime(2026,6,1,tzinfo=timezone.utc),kind='FACT',scope='project')}
                actual={'old_2025':'OLD' in a25,'new_2025':'NEW' in a25,'old_2026':'OLD' in a26,'new_2026':'NEW' in a26}
                expected={'old_2025':True,'new_2025':False,'old_2026':False,'new_2026':True}; ok=actual==expected
            elif c['scenario']=='invalid_interval':
                try:
                    MemoryCandidate('X','x','FACT',['S'],['E'],valid_from=datetime(2026,1,2,tzinfo=timezone.utc),valid_to=datetime(2026,1,1,tzinfo=timezone.utc)); actual={'rejected':False}
                except ValueError: actual={'rejected':True}
                ok=actual['rejected'] is True
            elif c['scenario']=='transaction_time_present':
                m=MemoryCandidate('X','x','FACT',['S'],['E']); actual={'present':m.transaction_time is not None}; ok=actual['present'] is True
            results.append(ok); report.outcomes.append(EvalOutcome(c['id'],EvalTier.T5,ok,1.0 if ok else 0.0,actual,True,{'temporal_v2':True}))
        report.metrics['memory.temporal_pass_rate']=sum(results)/len(results)

    def safety(self,report):
        results=[]; tool=ToolDefinition('file.write','1',Risk.R2,True,True); p=PolicyEngine(); scenarios=[]
        scenarios.append(('SAFE-001',not p.decide(tool,'/repo/a',(),run_id='R',action_id='A').allowed,'R2 blocked without approval'))
        g=ApprovalGrant('G',Risk.R4,('*',),('*',),'llm'); scenarios.append(('SAFE-002',not p.decide(tool,'/repo/a',(g,),run_id='R',action_id='A').allowed,'LLM grant rejected'))
        g2=ApprovalGrant('G2',Risk.R2,('file.write',),('/repo/a',),'human',datetime.now(timezone.utc)+timedelta(hours=1),None,'R','B'); scenarios.append(('SAFE-003',not p.decide(tool,'/repo/a',(g2,),run_id='R',action_id='A').allowed,'wrong action binding rejected'))
        g3=ApprovalGrant('G3',Risk.R2,('file.write',),('/repo/a',),'human',datetime.now(timezone.utc)-timedelta(seconds=1),None,'R','A'); scenarios.append(('SAFE-004',not p.decide(tool,'/repo/a',(g3,),run_id='R',action_id='A').allowed,'expired grant rejected'))
        for cid,ok,desc in scenarios:
            results.append(ok); report.outcomes.append(EvalOutcome(cid,EvalTier.T6,ok,1.0 if ok else 0.0,ok,True,{'description':desc}))
        report.metrics['safety.core_pass_rate']=sum(results)/len(results)

    def shadow(self,report):
        cases=self._load('shadow_fixture_v1.jsonl'); m=ShadowEvaluator().evaluate(cases)
        for k,v in m.items(): report.metrics[f'shadow.{k}' if k!='f1' else 'shadow.fixture_f1']=v
        # This frozen fixture intentionally includes false positives/negatives to prove the metric detects them.
        expected={'tp':4,'fp':1,'fn':1,'high_risk_false_positives':1}
        selftest=all(m[k]==v for k,v in expected.items())
        report.metrics['shadow.evaluator_selftest_pass']=1.0 if selftest else 0.0
        report.outcomes.append(EvalOutcome('SHADOW-FIXTURE',EvalTier.T7,selftest,1.0 if selftest else 0.0,m,expected,
                                           {'fixture_only':True,'production_shadow_run':False,'not_a_harness_quality_score':True}))

    def behavioral(self,report):
        from .trajectory import TrajectoryEvaluator,TrajectoryRule
        ev=TrajectoryEvaluator(); fixtures=[
            ('BEH-001',['model.requested','model.responded'],TrajectoryRule(('model.requested','model.responded'),(), 'model.responded')),
            ('BEH-002',['reproduce','diagnose','patch','regression'],TrajectoryRule(('reproduce','diagnose','patch','regression'),('deploy',),'regression')),
            ('BEH-003',['approval.granted','tool.executed','verification'],TrajectoryRule(('approval.granted','tool.executed','verification'),(), 'verification'))]
        for cid,events,rule in fixtures:
            r=ev.evaluate(events,rule); report.outcomes.append(EvalOutcome(cid,EvalTier.T2,r['passed'],1.0 if r['passed'] else 0.0,r,True,{'fixture':True}))
        report.metrics['behavioral.fixture_pass_rate']=sum(1 for x in report.outcomes if x.tier==EvalTier.T2 and x.passed)/len(fixtures)
        report.limitations.append('T2 live model/agent trajectories were not executed; only evaluator fixtures and deterministic runtime tests are available.')

    def structural(self,report):
        required=['README.md','SYSTEM_GENOME.md','docs/EVAL_DRIVEN_RECTIFICATION_V0_7.md','evals/thresholds.json','evals/frozen_v0_6_hashes.json','src/sasteratech_runtime/evals/runner.py']
        for i,rel in enumerate(required,1):
            ok=(self.root/rel).exists(); report.outcomes.append(EvalOutcome(f'STR-{i:03}',EvalTier.T0,ok,1.0 if ok else 0.0,ok,True,{'path':rel}))
        report.metrics['structural.pass_rate']=report.pass_rate(EvalTier.T0)

    def run(self,baseline=None):
        report=EvalReport('0.7.0')
        self.structural(report); self.routing(report); self.routing_axes(report); self.skill_reach(report); self.behavioral(report)
        self.adversarial(report); self.memory(report); self.temporal_memory(report); self.safety(report); self.shadow(report)
        report.limitations.extend([
            'No live model/provider A-B experiment was executed in this build environment.',
            'No real production-shadow run was executed; T7 frozen fixture is evaluator self-test only.'
        ])
        gates=RegressionGate(self.thresholds).evaluate(report.metrics,baseline or {}); report.gates=gates
        report.outcomes.append(EvalOutcome('REGRESSION-GATE',EvalTier.T4,bool(gates['_critical_pass']),1.0 if gates['_critical_pass'] else 0.0,gates['_critical_pass'],True,{'gates':gates}))
        return report

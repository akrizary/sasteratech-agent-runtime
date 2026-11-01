import json
from .actions import CapabilityGuard
from .policy import PolicyEngine
from .security_models import ToolExecutionResult, JudgeDisposition, EffectStatus
from .effects import EffectLedger, ReplayBlocked
from .injection import PromptInjectionDefender
from .secrets import SecretBoundary
from .risk_judge import SemanticRiskJudge

class ToolGateway:
    def __init__(self,registry,*,store=None,approval_service=None,role_registry=None,
                 policy=None,risk_judge=None,injection_defender=None,secret_boundary=None,event_log=None):
        self.registry=registry
        self.store=store
        self.approvals=approval_service
        self.capability=CapabilityGuard(role_registry)
        self.policy=policy or PolicyEngine()
        self.risk_judge=risk_judge or SemanticRiskJudge()
        self.injection=injection_defender or PromptInjectionDefender()
        self.secrets=secret_boundary or SecretBoundary()
        self.events=event_log
        self.effects=EffectLedger(store) if store else None

    def execute(self,run_id,intent,args,*,grants=(),idempotency_key=None):
        spec=self.registry.get(intent.tool_id); tool=spec.definition
        cap=self.capability.check(intent,tool)
        if not cap.allowed:
            return ToolExecutionResult(intent.action_id,None,False,False,'BLOCKED',reason=cap.reason)

        if spec.argument_validator:
            try: spec.argument_validator(args)
            except Exception as e:
                return ToolExecutionResult(intent.action_id,None,False,False,'BLOCKED',reason=f'argument validation failed: {e}')

        try:
            judge=self.risk_judge.judge(intent,tool,args)
        except Exception as e:
            if spec.semantic_judge_required:
                from .security_models import JudgeDecision
                judge=JudgeDecision(JudgeDisposition.ESCALATE,f'judge failure: {type(e).__name__}','fail_closed')
            else:
                from .security_models import JudgeDecision
                judge=JudgeDecision(JudgeDisposition.ALLOW,f'optional judge unavailable: {type(e).__name__}','optional_failure')
        if judge.disposition==JudgeDisposition.BLOCK:
            return ToolExecutionResult(intent.action_id,None,False,False,'BLOCKED',reason=f'risk judge blocked: {judge.reason}')

        human_required = judge.disposition==JudgeDisposition.ESCALATE
        policy=self.policy.decide(tool,intent.resource,grants,run_id=run_id,action_id=intent.action_id,human_required=human_required)
        if human_required and not policy.allowed:
            policy.reason=f'semantic risk escalation: {judge.reason}; human approval required'

        if not policy.allowed:
            req_id=None
            if policy.needs_approval and self.approvals:
                req_id=self.approvals.request(run_id,intent.action_id,tool.id,intent.resource,tool.risk,policy.reason)
            return ToolExecutionResult(intent.action_id,None,False,False,'APPROVAL_REQUIRED' if policy.needs_approval else 'BLOCKED',approval_request_id=req_id,reason=policy.reason)

        from .roles import RISK_RANK
        from .models import Risk
        if tool.side_effect and RISK_RANK[tool.risk] >= RISK_RANK[Risk.R2] and not spec.allow_unverifiable_effect and not (spec.readback and spec.verify_effect):
            return ToolExecutionResult(intent.action_id,None,False,False,'BLOCKED',reason='R2+ side effect requires readback verification contract')

        if tool.network and not spec.allow_secret_transmission and self.secrets.contains_secret(args):
            return ToolExecutionResult(intent.action_id,None,False,False,'BLOCKED',reason='secret boundary: prohibited secret transmission')

        effect_id=None; prior=None
        redacted_args=self.secrets.redact(args)
        if self.effects and tool.side_effect:
            effective_idempotency_key=idempotency_key or intent.action_id
            try:
                prior,reused=self.effects.reserve(run_id,intent.action_id,tool.id,intent.resource,effective_idempotency_key,tool.idempotent,redacted_args)
            except ReplayBlocked as e:
                return ToolExecutionResult(intent.action_id,None,False,False,'RECONCILIATION_REQUIRED',reason=str(e))
            effect_id=prior['effect_id']
            if reused:
                result=json.loads(prior['result_json']) if prior.get('result_json') else None
                return ToolExecutionResult(intent.action_id,effect_id,False,prior['status']=='VERIFIED','REUSED',safe_output=result,reason='idempotent prior effect reused')
            self.effects.mark(effect_id,EffectStatus.STARTED)

        try:
            raw=spec.handler(args)
        except Exception as e:
            if self.effects and effect_id:
                # Side effect may have happened before exception; non-idempotent calls are uncertain.
                status=EffectStatus.UNKNOWN if tool.side_effect and not tool.idempotent else EffectStatus.FAILED
                self.effects.mark(effect_id,status,error=f'{type(e).__name__}: {e}')
            return ToolExecutionResult(intent.action_id,effect_id,True,False,'FAILED',reason=f'{type(e).__name__}: {e}')

        verified=not tool.side_effect
        verification=None
        if self.effects and effect_id:
            self.effects.mark(effect_id,EffectStatus.SUCCEEDED,result=self.secrets.redact(raw))

        if tool.side_effect:
            if spec.readback and spec.verify_effect:
                try:
                    observed=spec.readback(args,raw)
                    verified=bool(spec.verify_effect(args,raw,observed))
                    verification={'verified':verified,'observed':self.secrets.redact(observed)}
                    if self.effects and effect_id:
                        self.effects.mark(effect_id,EffectStatus.VERIFIED if verified else EffectStatus.UNKNOWN,result=self.secrets.redact(raw),verification=verification)
                except Exception as e:
                    verified=False
                    verification={'verified':False,'error':f'{type(e).__name__}: {e}'}
                    if self.effects and effect_id:
                        self.effects.mark(effect_id,EffectStatus.UNKNOWN,result=self.secrets.redact(raw),verification=verification)
            else:
                verified=False

        rendered=raw if isinstance(raw,str) else json.dumps(raw,sort_keys=True,default=str)
        finding=self.injection.inspect(rendered,spec.output_trust)
        safe=self.injection.wrap_for_context(self.secrets.redact(rendered),finding,tool.id)
        status='VERIFIED' if verified else ('SUCCEEDED_UNVERIFIED' if tool.side_effect else 'SUCCEEDED')
        evidence=[{'kind':'tool_execution','tool':tool.id,'effect_id':effect_id,'verified':verified}]
        meta={'injection_severity':finding.severity.value,'injection_indicators':list(finding.indicators),'policy_reason':policy.reason,'judge':judge.disposition.value}
        if self.events:
            self.events.append(run_id,'tool.executed',{'action_id':intent.action_id,'tool_id':tool.id,'effect_id':effect_id,'verified':verified,'status':status})
        return ToolExecutionResult(intent.action_id,effect_id,True,verified,status,output=raw,safe_output=safe,evidence=evidence,metadata=meta)

from .security_models import JudgeDecision, JudgeDisposition

class SemanticRiskJudge:
    def judge(self,intent,tool,args):
        return JudgeDecision(JudgeDisposition.ALLOW,'no semantic judge configured','none')

class DeterministicRiskJudge(SemanticRiskJudge):
    def __init__(self, rules=()): self.rules=tuple(rules)
    def judge(self,intent,tool,args):
        for rule in self.rules:
            decision=rule(intent,tool,args)
            if decision is not None: return decision
        return JudgeDecision(JudgeDisposition.ALLOW,'no deterministic rule matched','deterministic')

class FailClosedJudge(SemanticRiskJudge):
    def judge(self,intent,tool,args):
        return JudgeDecision(JudgeDisposition.ESCALATE,'semantic judgement unavailable; escalate','fail_closed')

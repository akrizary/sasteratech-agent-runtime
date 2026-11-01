from datetime import datetime, timezone
from fnmatch import fnmatch
from .models import Risk

RANK={Risk.R0:0,Risk.R1:1,Risk.R2:2,Risk.R3:3,Risk.R4:4}

class PolicyDecision:
    def __init__(self,allowed,reason,needs_approval=False):
        self.allowed=allowed; self.reason=reason; self.needs_approval=needs_approval

class PolicyEngine:
    def __init__(self,r1_auto=True): self.r1_auto=r1_auto

    def grant_valid(self,grant,tool,resource,*,run_id=None,action_id=None,human_required=False):
        if grant.issued_by not in {'human','policy'}: return False
        if human_required and grant.issued_by!='human': return False
        if grant.issued_by=='policy' and RANK[tool.risk] >= RANK[Risk.R2]: return False
        if RANK[tool.risk] >= RANK[Risk.R2] and grant.issued_by=='human' and (grant.run_id is None or grant.action_id is None): return False
        if grant.run_id is not None and run_id != grant.run_id: return False
        if grant.action_id is not None and action_id != grant.action_id: return False
        if grant.expires_at is not None:
            exp=grant.expires_at
            if exp.tzinfo is None: exp=exp.replace(tzinfo=timezone.utc)
            if exp <= datetime.now(timezone.utc): return False
        if RANK[grant.risk_ceiling] < RANK[tool.risk]: return False
        if tool.id not in grant.actions and '*' not in grant.actions: return False
        if not any(fnmatch(resource,scope) for scope in grant.resource_scope): return False
        return True

    def decide(self,tool,resource,grants=(),*,run_id=None,action_id=None,human_required=False):
        if not human_required:
            if tool.risk==Risk.R0 and not tool.requires_approval:
                return PolicyDecision(True,'R0 read-only action')
            if tool.risk==Risk.R1 and self.r1_auto and not tool.requires_approval:
                return PolicyDecision(True,'R1 reversible local action allowed by policy')
        for grant in grants:
            if self.grant_valid(grant,tool,resource,run_id=run_id,action_id=action_id,human_required=human_required):
                return PolicyDecision(True,f'authorized by {grant.approval_id}')
        return PolicyDecision(False,'explicit scoped approval required',True)

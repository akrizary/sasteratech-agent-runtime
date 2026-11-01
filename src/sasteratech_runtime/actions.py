from dataclasses import dataclass, field
import uuid
from fnmatch import fnmatchcase
from .models import Risk, ToolDefinition
from .roles import Role, RoleRegistry, RISK_RANK

@dataclass(frozen=True)
class ActionIntent:
    worker_id:str
    role:Role
    tool_id:str
    resource:str
    requested_risk:Risk
    purpose:str
    evidence_expected:tuple[str,...]=()
    approval_id:str|None=None
    resource_scope:tuple[str,...]=('*',)
    action_id:str=field(default_factory=lambda:f'ACT-{uuid.uuid4()}')

class CapabilityDecision:
    def __init__(self, allowed, reason):
        self.allowed=allowed; self.reason=reason

class CapabilityGuard:
    def __init__(self, role_registry=None):
        self.roles=role_registry or RoleRegistry()

    def check(self, intent, tool:ToolDefinition):
        profile=self.roles.get(intent.role)
        if not profile.tool_allowed(intent.tool_id):
            return CapabilityDecision(False,'tool outside role capability')
        if tool.id != intent.tool_id:
            return CapabilityDecision(False,'tool definition mismatch')
        if not any(fnmatchcase(intent.resource,pat) for pat in intent.resource_scope):
            return CapabilityDecision(False,'resource outside task scope')
        if RISK_RANK[intent.requested_risk] < RISK_RANK[tool.risk]:
            return CapabilityDecision(False,'intent understates tool risk')
        if RISK_RANK[intent.requested_risk] > RISK_RANK[profile.risk_ceiling]:
            return CapabilityDecision(False,'requested risk exceeds role ceiling')
        if RISK_RANK[tool.risk] > RISK_RANK[profile.risk_ceiling]:
            return CapabilityDecision(False,'tool risk exceeds role ceiling')
        return CapabilityDecision(True,'role capability and task scope permit intent; policy approval still required')

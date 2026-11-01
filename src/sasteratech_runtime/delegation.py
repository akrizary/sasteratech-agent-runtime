from dataclasses import replace
from fnmatch import fnmatchcase
from .models import Risk
from .roles import RoleRegistry, RISK_RANK

class DelegationError(ValueError): pass

class DelegationEngine:
    def __init__(self, role_registry=None, max_depth=2):
        self.roles=role_registry or RoleRegistry()
        self.max_depth=max_depth

    @staticmethod
    def _budget_narrows(parent, child):
        cost_ok = (parent.max_cost_usd is None or (child.max_cost_usd is not None and child.max_cost_usd <= parent.max_cost_usd))
        context_ok = (parent.max_context_tokens is None or (child.max_context_tokens is not None and child.max_context_tokens <= parent.max_context_tokens))
        return (child.max_tool_calls <= parent.max_tool_calls and
                child.max_tokens <= parent.max_tokens and
                child.max_seconds <= parent.max_seconds and
                child.max_model_requests <= parent.max_model_requests and
                cost_ok and context_ok)

    @staticmethod
    def _scope_narrows(parent_scopes, child_scopes):
        # Conservative approximation: every child scope must be matched by at least one parent pattern.
        # Exact filesystem canonicalization belongs in the executor layer.
        for child in child_scopes:
            if not any(fnmatchcase(child, p) or p == '*' for p in parent_scopes):
                return False
        return True

    def validate(self, parent_packet, child_packet):
        parent_role=self.roles.get(parent_packet.assigned_role)
        child_role=self.roles.get(child_packet.assigned_role)
        if child_packet.assigned_role not in parent_role.may_delegate_to:
            raise DelegationError(f'{parent_role.role.value} may not delegate to {child_role.role.value}')
        if child_packet.depth != parent_packet.depth + 1:
            raise DelegationError('child depth must equal parent depth + 1')
        if child_packet.depth > self.max_depth:
            raise DelegationError('delegation depth exceeded')
        if RISK_RANK[child_packet.risk_ceiling] > RISK_RANK[parent_packet.risk_ceiling]:
            raise DelegationError('child risk ceiling exceeds parent')
        if RISK_RANK[child_packet.risk_ceiling] > RISK_RANK[child_role.risk_ceiling]:
            raise DelegationError('child packet exceeds role risk ceiling')
        if not child_role.accepts(child_packet.task_class):
            raise DelegationError('child role does not accept task class')
        for tool in child_packet.requested_tools:
            if not child_role.tool_allowed(tool):
                raise DelegationError(f'child role cannot use tool: {tool}')
        if not self._budget_narrows(parent_packet.budget, child_packet.budget):
            raise DelegationError('child budget exceeds parent budget')
        if not self._scope_narrows(parent_packet.resource_scope, child_packet.resource_scope):
            raise DelegationError('child resource scope exceeds parent scope')
        return True

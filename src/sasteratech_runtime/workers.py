from dataclasses import dataclass
from .roles import Role, RoleRegistry
from .models import TaskClass, Risk
from .task_packet import TaskPacket

@dataclass(frozen=True)
class Worker:
    worker_id:str
    role:Role

    def validate_packet(self, packet:TaskPacket, registry=None):
        registry=registry or RoleRegistry()
        profile=registry.get(self.role)
        if packet.assigned_role != self.role:
            raise ValueError('packet assigned to different role')
        if not profile.accepts(packet.task_class):
            raise ValueError(f'{self.role.value} does not accept {packet.task_class.value}')
        from .roles import RISK_RANK
        if RISK_RANK[packet.risk_ceiling] > RISK_RANK[profile.risk_ceiling]:
            raise ValueError('packet exceeds role risk ceiling')
        for t in packet.requested_tools:
            if not profile.tool_allowed(t):
                raise ValueError(f'tool not permitted for role: {t}')
        return True

    def task_contract(self, packet:TaskPacket):
        self.validate_packet(packet)
        return {
            'worker_id':self.worker_id,
            'role':self.role.value,
            'objective':packet.objective,
            'task_class':packet.task_class.value,
            'tools':list(packet.requested_tools),
            'risk_ceiling':packet.risk_ceiling.value,
            'constraints':list(packet.constraints),
            'evidence_refs':list(packet.evidence_refs),
            'output_contract':packet.output_contract,
            'budget':{
                'max_tool_calls':packet.budget.max_tool_calls,
                'max_tokens':packet.budget.max_tokens,
                'max_seconds':packet.budget.max_seconds,
                'max_model_requests':packet.budget.max_model_requests,
                'max_context_tokens':packet.budget.max_context_tokens,
                'max_cost_usd':packet.budget.max_cost_usd,
            }
        }

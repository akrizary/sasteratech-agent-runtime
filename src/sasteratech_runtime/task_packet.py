from dataclasses import dataclass, field
from .models import Risk, TaskClass
from .roles import Role

@dataclass(frozen=True)
class TaskBudget:
    max_tool_calls:int=20
    max_tokens:int=12000
    max_seconds:int=600
    max_model_requests:int=12
    max_context_tokens:int|None=None
    max_cost_usd:float|None=None

    def __post_init__(self):
        if self.max_tool_calls < 0: raise ValueError('max_tool_calls cannot be negative')
        if self.max_tokens <= 0: raise ValueError('max_tokens must be positive')
        if self.max_seconds <= 0: raise ValueError('max_seconds must be positive')
        if self.max_model_requests <= 0: raise ValueError('max_model_requests must be positive')
        if self.max_context_tokens is not None and self.max_context_tokens <= 0: raise ValueError('max_context_tokens must be positive')
        if self.max_cost_usd is not None and self.max_cost_usd <= 0: raise ValueError('max_cost_usd must be positive')

@dataclass(frozen=True)
class TaskPacket:
    packet_id:str
    run_id:str
    task_id:str
    objective:str
    task_class:TaskClass
    assigned_role:Role
    risk_ceiling:Risk=Risk.R0
    requested_tools:tuple[str,...]=()
    constraints:tuple[str,...]=()
    evidence_refs:tuple[str,...]=()
    output_contract:str='structured_result'
    budget:TaskBudget=field(default_factory=TaskBudget)
    depth:int=0
    parent_packet_id:str|None=None
    producer_worker_id:str|None=None
    resource_scope:tuple[str,...]=('*',)

    def __post_init__(self):
        if not self.objective.strip(): raise ValueError('objective required')
        if self.depth < 0: raise ValueError('depth cannot be negative')

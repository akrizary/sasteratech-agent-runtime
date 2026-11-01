from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from .roles import Role
from .task_packet import TaskBudget

class RuntimeStatus(str, Enum):
    COMPLETE='COMPLETE'; UNAVAILABLE='UNAVAILABLE'; TIMEOUT='TIMEOUT'; BUDGET_EXCEEDED='BUDGET_EXCEEDED'; PROVIDER_ERROR='PROVIDER_ERROR'; CANCELLED='CANCELLED'; INVALID_RESPONSE='INVALID_RESPONSE'; INTERNAL_ERROR='INTERNAL_ERROR'

@dataclass(frozen=True)
class ModelProfile:
    alias:str
    adapter_id:str
    model_id:str|None=None
    model_env:str|None=None
    allowed_roles:tuple[Role,...]=()
    enabled:bool=True
    metadata:dict=field(default_factory=dict)

@dataclass(frozen=True)
class UsageReport:
    requests:int|None=None
    tool_calls:int|None=None
    input_tokens:int|None=None
    output_tokens:int|None=None
    total_tokens:int|None=None
    cost_usd:float|None=None
    unmeasured_requests:int|None=None

@dataclass(frozen=True)
class RuntimeRequest:
    run_id:str
    packet_id:str
    task_id:str
    role:Role
    model:ModelProfile
    prompt:str
    instructions:str
    budget:TaskBudget
    context_text:str=''
    message_history_json:str|None=None
    metadata:dict=field(default_factory=dict)

@dataclass
class RuntimeResponse:
    status:RuntimeStatus
    output:Any=None
    runtime_run_id:str|None=None
    conversation_id:str|None=None
    usage:UsageReport=field(default_factory=UsageReport)
    messages_json:str|None=None
    error_type:str|None=None
    error_message:str|None=None
    metadata:dict=field(default_factory=dict)

class RuntimeUnavailable(RuntimeError): pass

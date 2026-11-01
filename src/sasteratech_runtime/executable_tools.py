from dataclasses import dataclass, field
from typing import Callable, Any
from .models import ToolDefinition

@dataclass(frozen=True)
class ToolRuntimeSpec:
    definition: ToolDefinition
    handler: Callable[[dict],Any]
    argument_validator: Callable[[dict],None]|None=None
    readback: Callable[[dict,Any],Any]|None=None
    verify_effect: Callable[[dict,Any,Any],bool]|None=None
    allow_secret_transmission: bool=False
    output_trust: str='UNTRUSTED_EXTERNAL'
    semantic_judge_required: bool=False
    allow_unverifiable_effect: bool=False
    metadata: dict=field(default_factory=dict)

class ExecutableToolRegistry:
    def __init__(self): self._tools={}
    def register(self,spec:ToolRuntimeSpec):
        tid=spec.definition.id
        if tid in self._tools: raise ValueError(f'duplicate executable tool: {tid}')
        self._tools[tid]=spec
    def get(self,tool_id): return self._tools[tool_id]
    def definition(self,tool_id): return self.get(tool_id).definition

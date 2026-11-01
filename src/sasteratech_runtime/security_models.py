from dataclasses import dataclass, field
from enum import Enum
from typing import Any

class JudgeDisposition(str, Enum):
    ALLOW='ALLOW'
    BLOCK='BLOCK'
    ESCALATE='ESCALATE'

class EffectStatus(str, Enum):
    RESERVED='RESERVED'
    STARTED='STARTED'
    SUCCEEDED='SUCCEEDED'
    VERIFIED='VERIFIED'
    FAILED='FAILED'
    UNKNOWN='UNKNOWN'

class InjectionSeverity(str, Enum):
    NONE='NONE'
    LOW='LOW'
    MEDIUM='MEDIUM'
    HIGH='HIGH'

@dataclass(frozen=True)
class JudgeDecision:
    disposition: JudgeDisposition
    reason: str
    source: str='deterministic'
    confidence: float|None=None

@dataclass(frozen=True)
class InjectionFinding:
    severity: InjectionSeverity
    indicators: tuple[str,...]=()
    withhold: bool=False

@dataclass
class ToolExecutionResult:
    action_id: str
    effect_id: str|None
    executed: bool
    verified: bool
    status: str
    output: Any=None
    safe_output: Any=None
    approval_request_id: str|None=None
    reason: str|None=None
    evidence: list[dict]=field(default_factory=list)
    metadata: dict=field(default_factory=dict)

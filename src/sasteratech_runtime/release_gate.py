from dataclasses import dataclass, field
from enum import Enum

class GateState(str,Enum):
    PASS='PASS'; FAIL='FAIL'; BLOCKED='BLOCKED'; NOT_RUN='NOT_RUN'; NOT_CONFIGURED='NOT_CONFIGURED'

@dataclass(frozen=True)
class GateEvidence:
    key:str
    state:GateState
    critical:bool=True
    details:dict=field(default_factory=dict)

@dataclass
class ReleaseDecision:
    candidate_ready:bool
    production_ready:bool
    evidence:dict[str,GateEvidence]
    blockers:list[str]

class ReleaseGate:
    def __init__(self, offline_required, production_required):
        self.offline_required=tuple(offline_required)
        self.production_required=tuple(production_required)

    @staticmethod
    def _passes(evidence,key):
        return key in evidence and evidence[key].state==GateState.PASS

    def evaluate(self,evidence):
        evidence={e.key:e for e in evidence}
        offline_blockers=[k for k in self.offline_required if not self._passes(evidence,k)]
        production_blockers=offline_blockers+[k for k in self.production_required if not self._passes(evidence,k)]
        return ReleaseDecision(
            candidate_ready=not offline_blockers,
            production_ready=not production_blockers,
            evidence=evidence,
            blockers=production_blockers
        )

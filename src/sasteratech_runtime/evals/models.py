from dataclasses import dataclass,field,asdict
from enum import Enum
from typing import Any

class EvalTier(str,Enum):
    T0='T0_STRUCTURAL'
    T1='T1_ROUTING'
    T2='T2_BEHAVIORAL'
    T3='T3_ADVERSARIAL'
    T4='T4_REGRESSION'
    T5='T5_LONG_HORIZON'
    T6='T6_SAFETY'
    T7='T7_PRODUCTION_SHADOW'

@dataclass(frozen=True)
class EvalCase:
    case_id:str
    tier:EvalTier
    category:str
    inputs:dict
    expected:Any=None
    metadata:dict=field(default_factory=dict)

@dataclass
class EvalOutcome:
    case_id:str
    tier:EvalTier
    passed:bool
    score:float
    actual:Any=None
    expected:Any=None
    details:dict=field(default_factory=dict)

@dataclass
class EvalReport:
    suite_version:str
    outcomes:list[EvalOutcome]=field(default_factory=list)
    metrics:dict=field(default_factory=dict)
    gates:dict=field(default_factory=dict)
    limitations:list[str]=field(default_factory=list)

    def pass_rate(self,tier=None):
        xs=self.outcomes if tier is None else [x for x in self.outcomes if x.tier==tier]
        return 1.0 if not xs else sum(1 for x in xs if x.passed)/len(xs)

    def as_dict(self):
        return {
            'suite_version':self.suite_version,
            'outcomes':[{
                'case_id':o.case_id,'tier':o.tier.value,'passed':o.passed,'score':o.score,
                'actual':o.actual,'expected':o.expected,'details':o.details
            } for o in self.outcomes],
            'metrics':self.metrics,'gates':self.gates,'limitations':self.limitations
        }

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class StructuredProposition:
    proposition_id:str
    subject:str
    predicate:str
    value:Any
    temporal_scope:str|None=None
    evidence_ref:str|None=None

@dataclass(frozen=True)
class Contradiction:
    left_id:str
    right_id:str
    reason:str

class ContradictionScanner:
    @staticmethod
    def _norm(v):
        if isinstance(v,str): return ' '.join(v.strip().lower().split())
        if isinstance(v,(list,tuple,set)): return tuple(sorted(ContradictionScanner._norm(x) for x in v))
        return v

    def scan(self,propositions):
        out=[]; ps=list(propositions)
        for i,a in enumerate(ps):
            for b in ps[i+1:]:
                if self._norm(a.subject)!=self._norm(b.subject): continue
                if self._norm(a.predicate)!=self._norm(b.predicate): continue
                if a.temporal_scope and b.temporal_scope and a.temporal_scope!=b.temporal_scope: continue
                if self._norm(a.value)!=self._norm(b.value):
                    out.append(Contradiction(a.proposition_id,b.proposition_id,'same subject/predicate/time with incompatible values'))
        return out

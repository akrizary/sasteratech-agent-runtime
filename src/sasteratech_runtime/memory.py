from dataclasses import dataclass,field,replace
from typing import Optional
from datetime import datetime,timezone

UTC=timezone.utc

def _aware(dt):
    if dt is None: return None
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=UTC)

@dataclass
class MemoryCandidate:
    memory_id:str
    content:str
    kind:str
    source_refs:list[str]=field(default_factory=list)
    evidence_refs:list[str]=field(default_factory=list)
    writer:Optional[str]=None
    sensitivity_ok:bool=True
    unresolved_contradiction:bool=False
    ttl:Optional[str]=None
    valid_from:Optional[datetime]=None
    valid_to:Optional[datetime]=None
    supersedes:list[str]=field(default_factory=list)
    superseded_by:list[str]=field(default_factory=list)
    transaction_time:datetime=field(default_factory=lambda: datetime.now(UTC))
    scope:Optional[str]=None

    def __post_init__(self):
        self.valid_from=_aware(self.valid_from)
        self.valid_to=_aware(self.valid_to)
        self.transaction_time=_aware(self.transaction_time) or datetime.now(UTC)
        if self.valid_from and self.valid_to and self.valid_to <= self.valid_from:
            raise ValueError('valid_to must be after valid_from')
        if self.memory_id in self.supersedes or self.memory_id in self.superseded_by:
            raise ValueError('memory cannot supersede itself')

    def valid_at(self,when):
        when=_aware(when)
        if self.valid_from is not None and when < self.valid_from: return False
        if self.valid_to is not None and when >= self.valid_to: return False
        return True

class MemoryGovernor:
    def promotable(self,candidate):
        failures=[]
        if not candidate.source_refs: failures.append('missing provenance/source')
        if candidate.kind in {'FACT','PROJECT_STATE','RULE'} and not candidate.evidence_refs:
            failures.append('missing evidence for authoritative memory type')
        if candidate.unresolved_contradiction: failures.append('unresolved contradiction')
        if not candidate.sensitivity_ok: failures.append('sensitivity policy blocks storage')
        if candidate.valid_from and candidate.valid_to and candidate.valid_to <= candidate.valid_from:
            failures.append('invalid temporal interval')
        return (not failures,failures)

class TemporalMemoryStore:
    def __init__(self): self._items={}

    def add(self,candidate):
        if candidate.memory_id in self._items: raise ValueError(f'duplicate memory_id: {candidate.memory_id}')
        ok,fail=MemoryGovernor().promotable(candidate)
        if not ok: raise ValueError('memory not promotable: '+', '.join(fail))
        for old_id in candidate.supersedes:
            if old_id not in self._items: raise KeyError(f'unknown superseded memory: {old_id}')
        self._items[candidate.memory_id]=candidate
        for old_id in candidate.supersedes:
            old=self._items[old_id]
            if candidate.memory_id not in old.superseded_by:
                old.superseded_by.append(candidate.memory_id)
            if old.valid_to is None and candidate.valid_from is not None:
                old.valid_to=candidate.valid_from
        return candidate

    def get(self,memory_id): return self._items[memory_id]

    def as_of(self,when,*,kind=None,scope=None,include_superseded=False):
        when=_aware(when)
        rows=[]
        for m in self._items.values():
            if kind and m.kind!=kind: continue
            if scope and m.scope!=scope: continue
            if not m.valid_at(when): continue
            if not include_superseded and m.superseded_by:
                # A future supersessor does not hide the old fact before its validity starts.
                active_supersessor=False
                for sid in m.superseded_by:
                    s=self._items.get(sid)
                    if s and s.valid_at(when) and (s.valid_from is None or s.valid_from<=when):
                        active_supersessor=True; break
                if active_supersessor: continue
            rows.append(m)
        return sorted(rows,key=lambda m:(m.valid_from or datetime.min.replace(tzinfo=UTC),m.transaction_time,m.memory_id),reverse=True)

    def latest(self,*,kind=None,scope=None,at=None):
        at=_aware(at or datetime.now(UTC))
        rows=self.as_of(at,kind=kind,scope=scope)
        return rows[0] if rows else None

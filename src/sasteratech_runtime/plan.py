from dataclasses import dataclass, field, asdict
from enum import Enum

class PlanStatus(str,Enum):
    PENDING='PENDING'; READY='READY'; RUNNING='RUNNING'; BLOCKED='BLOCKED'; COMPLETE='COMPLETE'; FAILED='FAILED'; SKIPPED='SKIPPED'

@dataclass
class PlanTask:
    task_id:str; title:str; dependencies:list[str]=field(default_factory=list); status:PlanStatus=PlanStatus.PENDING; risk:str='R0'; owner_role:str|None=None; evidence_requirements:list[str]=field(default_factory=list); metadata:dict=field(default_factory=dict)

class PlanGraph:
    def __init__(self): self.tasks={}
    def add(self,task):
        if task.task_id in self.tasks: raise ValueError(f'duplicate task_id: {task.task_id}')
        self.tasks[task.task_id]=task; self._assert_acyclic(); self.refresh()
    def add_many(self,tasks):
        old=dict(self.tasks)
        try:
            for t in tasks:
                if t.task_id in self.tasks: raise ValueError(f'duplicate task_id: {t.task_id}')
                self.tasks[t.task_id]=t
            self._validate_dependencies(); self._assert_acyclic(); self.refresh()
        except Exception:
            self.tasks=old; raise
    def _validate_dependencies(self):
        for t in self.tasks.values():
            missing=[d for d in t.dependencies if d not in self.tasks]
            if missing: raise ValueError(f'{t.task_id} missing dependencies: {missing}')
    def _assert_acyclic(self):
        visiting=set(); visited=set()
        def visit(n):
            if n in visiting: raise ValueError('cycle detected in plan graph')
            if n in visited or n not in self.tasks: return
            visiting.add(n)
            for d in self.tasks[n].dependencies: visit(d)
            visiting.remove(n); visited.add(n)
        for n in self.tasks: visit(n)
    def refresh(self):
        for t in self.tasks.values():
            if t.status in {PlanStatus.COMPLETE,PlanStatus.FAILED,PlanStatus.SKIPPED,PlanStatus.RUNNING}: continue
            dep=[self.tasks[d].status for d in t.dependencies if d in self.tasks]
            if any(s==PlanStatus.FAILED for s in dep): t.status=PlanStatus.BLOCKED
            elif len(dep)==len(t.dependencies) and all(s==PlanStatus.COMPLETE for s in dep): t.status=PlanStatus.READY
            else: t.status=PlanStatus.PENDING
    def start(self,task_id):
        self.refresh(); t=self.tasks[task_id]
        if t.status!=PlanStatus.READY: raise ValueError(f'task not READY: {task_id} ({t.status})')
        t.status=PlanStatus.RUNNING
    def complete(self,task_id):
        t=self.tasks[task_id]
        if t.status!=PlanStatus.RUNNING: raise ValueError('only RUNNING task can complete')
        t.status=PlanStatus.COMPLETE; self.refresh()
    def fail(self,task_id):
        t=self.tasks[task_id]
        if t.status!=PlanStatus.RUNNING: raise ValueError('only RUNNING task can fail')
        t.status=PlanStatus.FAILED; self.refresh()
    def ready(self): self.refresh(); return [t for t in self.tasks.values() if t.status==PlanStatus.READY]
    def terminal(self): self.refresh(); return all(t.status in {PlanStatus.COMPLETE,PlanStatus.FAILED,PlanStatus.SKIPPED,PlanStatus.BLOCKED} for t in self.tasks.values())
    def to_dict(self): return {k:{**asdict(v),'status':v.status.value} for k,v in sorted(self.tasks.items())}

from .models import RunState

_ALLOWED={
RunState.READ_ONLY_AUDIT:{RunState.PLAN_READY,RunState.BLOCKED},
RunState.PLAN_READY:{RunState.PATCH_PREPARED,RunState.BLOCKED},
RunState.PATCH_PREPARED:{RunState.LOCAL_MUTATION_AUTHORIZED,RunState.EXTERNAL_MUTATION_AUTHORIZED,RunState.DEPLOY_AUTHORIZED,RunState.BLOCKED},
RunState.LOCAL_MUTATION_AUTHORIZED:{RunState.POST_MUTATION_VERIFY,RunState.RECOVERY},
RunState.EXTERNAL_MUTATION_AUTHORIZED:{RunState.POST_MUTATION_VERIFY,RunState.RECOVERY},
RunState.DEPLOY_AUTHORIZED:{RunState.POST_MUTATION_VERIFY,RunState.RECOVERY},
RunState.POST_MUTATION_VERIFY:{RunState.COMPLETE,RunState.RECOVERY,RunState.BLOCKED},
RunState.RECOVERY:{RunState.READ_ONLY_AUDIT,RunState.POST_MUTATION_VERIFY,RunState.BLOCKED},
RunState.BLOCKED:{RunState.READ_ONLY_AUDIT},
RunState.COMPLETE:set(),
}

class StateTransitionError(ValueError): pass

class StateMachine:
    def __init__(self,state=RunState.READ_ONLY_AUDIT):
        self.state=state; self.history=[state]
    def can_transition(self,target): return target in _ALLOWED[self.state]
    def transition(self,target):
        if not self.can_transition(target):
            raise StateTransitionError(f"Invalid transition {self.state.value} -> {target.value}")
        self.state=target; self.history.append(target); return self.state

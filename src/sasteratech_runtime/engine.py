from dataclasses import dataclass
from .router import route_task
from .models import RunState
from .state import StateMachine

@dataclass
class Intake:
    request: str
    mutation_requested: bool
    route: object

def intake(request):
    route=route_task(request)
    mutation_words=("write","edit","delete","deploy","push","send","publish","move","rename")
    mutation=any(w in request.lower() for w in mutation_words)
    return Intake(request,mutation,route)

class SasteraTechEngine:
    # Deterministic zygote: analyzes/plans only; executes no external action.
    def __init__(self): self.state=StateMachine()
    def analyze(self,request):
        i=intake(request)
        return {
            "request":i.request,"task":i.route.task.value,"reasoning_policy":i.route.reasoning_policy,
            "risk_floor":i.route.risk_floor.value,"mutation_requested":i.mutation_requested,
            "state":self.state.state.value,
        }
    def prepare_plan(self):
        if self.state.state==RunState.READ_ONLY_AUDIT:
            self.state.transition(RunState.PLAN_READY)
        return self.state.state

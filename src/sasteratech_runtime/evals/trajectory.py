from dataclasses import dataclass,field

@dataclass(frozen=True)
class TrajectoryRule:
    required_subsequence:tuple[str,...]=()
    forbidden:tuple[str,...]=()
    terminal:str|None=None
    max_occurrences:dict=field(default_factory=dict)

class TrajectoryEvaluator:
    @staticmethod
    def _is_subsequence(required,events):
        it=iter(events)
        return all(any(x==r for x in it) for r in required)

    def evaluate(self,events,rule:TrajectoryRule):
        failures=[]
        if rule.required_subsequence and not self._is_subsequence(rule.required_subsequence,events):
            failures.append('required_subsequence_missing')
        for x in rule.forbidden:
            if x in events: failures.append(f'forbidden_event:{x}')
        if rule.terminal is not None and (not events or events[-1]!=rule.terminal):
            failures.append(f'terminal_mismatch:{rule.terminal}')
        for x,limit in rule.max_occurrences.items():
            if events.count(x)>limit: failures.append(f'too_many:{x}')
        return {'passed':not failures,'failures':failures,'events':list(events)}

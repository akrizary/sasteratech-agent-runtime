from dataclasses import dataclass

@dataclass
class SLOResult:
    configured:bool
    passed:bool
    failures:list[str]
    unconfigured:list[str]

class SLOEvaluator:
    def evaluate(self, policy, observed):
        failures=[]; unconfigured=[]
        for key,limit in policy.get('hard_invariants',{}).items():
            metric=key[:-4] if key.endswith('_max') else key
            if metric not in observed:
                failures.append(f'missing hard invariant observation: {metric}')
            elif observed[metric] > limit:
                failures.append(f'{metric}={observed[metric]} exceeds {limit}')
        for key,limit in policy.get('operational_targets',{}).items():
            metric=key[:-4] if key.endswith('_max') else key
            if limit is None:
                unconfigured.append(key)
            elif metric not in observed:
                failures.append(f'missing operational observation: {metric}')
            elif observed[metric] > limit:
                failures.append(f'{metric}={observed[metric]} exceeds {limit}')
        return SLOResult(configured=not unconfigured,passed=not failures and not unconfigured,failures=failures,unconfigured=unconfigured)

class RegressionGate:
    def __init__(self,thresholds): self.thresholds=thresholds

    def evaluate(self,current,baseline=None):
        baseline=baseline or {}; gates={}; critical_pass=True
        for name,spec in self.thresholds.items():
            value=current.get(name)
            if value is None:
                gates[name]={'passed':False,'reason':'missing_metric','critical':bool(spec.get('critical'))}
                if spec.get('critical'): critical_pass=False
                continue
            direction=spec.get('direction','higher'); threshold=spec.get('threshold')
            if direction=='higher': threshold_ok=value>=threshold
            else: threshold_ok=value<=threshold
            regression_ok=True; base=baseline.get(name)
            tol=float(spec.get('regression_tolerance',0.0))
            if base is not None:
                regression_ok=(value >= base-tol) if direction=='higher' else (value <= base+tol)
            passed=threshold_ok and regression_ok
            gates[name]={'passed':passed,'value':value,'threshold':threshold,'baseline':base,'critical':bool(spec.get('critical')),'regression_ok':regression_ok}
            if spec.get('critical') and not passed: critical_pass=False
        gates['_critical_pass']=critical_pass
        return gates

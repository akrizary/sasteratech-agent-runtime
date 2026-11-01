def _safe(a,b): return 0.0 if b==0 else a/b

class ShadowEvaluator:
    def evaluate(self,cases):
        tp=fp=fn=exact=high_risk_fp=0
        for c in cases:
            ref=set(c.get('reference',[])); prop=set(c.get('proposed',[])); risks=c.get('risks',{})
            tp += len(ref & prop); fp += len(prop-ref); fn += len(ref-prop)
            exact += int(ref==prop)
            for act in prop-ref:
                if risks.get(act) in {'R3','R4'}: high_risk_fp += 1
        precision=_safe(tp,tp+fp); recall=_safe(tp,tp+fn); f1=_safe(2*precision*recall,precision+recall)
        return {
            'tp':tp,'fp':fp,'fn':fn,'precision':precision,'recall':recall,'f1':f1,
            'exact_action_match_rate':_safe(exact,len(cases)),
            'high_risk_false_positives':high_risk_fp,'n':len(cases)
        }

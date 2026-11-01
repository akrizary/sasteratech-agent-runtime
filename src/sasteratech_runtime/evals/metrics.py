from collections import Counter,defaultdict

def _safe_div(a,b): return 0.0 if b==0 else a/b

def classification_metrics(expected,predicted,labels=None):
    if len(expected)!=len(predicted): raise ValueError('length mismatch')
    labels=sorted(set(labels or []) | set(expected) | set(predicted))
    correct=sum(1 for e,p in zip(expected,predicted) if e==p)
    per={}
    for lab in labels:
        tp=sum(1 for e,p in zip(expected,predicted) if e==lab and p==lab)
        fp=sum(1 for e,p in zip(expected,predicted) if e!=lab and p==lab)
        fn=sum(1 for e,p in zip(expected,predicted) if e==lab and p!=lab)
        precision=_safe_div(tp,tp+fp); recall=_safe_div(tp,tp+fn)
        f1=_safe_div(2*precision*recall,precision+recall)
        per[lab]={'precision':precision,'recall':recall,'f1':f1,'support':sum(1 for e in expected if e==lab)}
    macro_f1=_safe_div(sum(x['f1'] for x in per.values()),len(per))
    return {'accuracy':_safe_div(correct,len(expected)),'macro_f1':macro_f1,'per_class':per,'n':len(expected)}

def skill_reach_metrics(cases):
    entry=[]; reach=[]; mrr=[]; precisions=[]; recalls=[]; f1s=[]; redundancies=[]; oos=[]
    for c in cases:
        target=c.get('expected_skill'); traj=[x for x in c.get('trajectory',[]) if x]
        out_of_scope=bool(c.get('out_of_scope')) or target is None
        if out_of_scope:
            ok=len(traj)==0
            entry.append(1.0 if ok else 0.0); reach.append(1.0 if ok else 0.0); oos.append(1.0 if ok else 0.0)
            redundancies.append(float(len(traj)))
            continue
        entry.append(1.0 if traj and traj[0]==target else 0.0)
        if target in traj:
            rank=traj.index(target)+1; reach.append(1.0); mrr.append(1.0/rank)
            unique=len(set(traj)); precision=1.0/unique if unique else 0.0; recall=1.0
        else:
            reach.append(0.0); mrr.append(0.0); precision=0.0; recall=0.0
        f1=_safe_div(2*precision*recall,precision+recall)
        precisions.append(precision); recalls.append(recall); f1s.append(f1)
        redundancies.append(float(max(0,len(traj)-1)))
    mean=lambda xs: _safe_div(sum(xs),len(xs))
    return {
        'entrypoint_accuracy':mean(entry),
        'trajectory_reachability':mean(reach),
        'step_efficiency_mrr':mean(mrr),
        'skill_precision':mean(precisions),
        'skill_recall':mean(recalls),
        'skill_f1':mean(f1s),
        'redundancy':mean(redundancies),
        'out_of_scope_restraint':mean(oos) if oos else 1.0,
        'n':len(cases)
    }

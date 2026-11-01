import hashlib
import json


class RealShadowInputError(ValueError):
    pass


def _safe(a,b): return 0.0 if b==0 else a/b


def validate_live_shadow_case(case):
    """Validate a historical, reference-only input record before any model call."""
    if not isinstance(case,dict):
        raise RealShadowInputError('case must be an object')
    if 'proposed' in case or 'generated_proposed_actions' in case:
        raise RealShadowInputError('input must not contain pre-written proposed actions')
    required=('id','prompt','reference_actions','risks','source')
    missing=[name for name in required if name not in case]
    if missing:
        raise RealShadowInputError(f'missing required fields: {", ".join(missing)}')
    if not isinstance(case['id'],str) or not case['id'].strip():
        raise RealShadowInputError('id must be a non-empty string')
    if not isinstance(case['prompt'],str) or not case['prompt'].strip():
        raise RealShadowInputError('prompt must be a non-empty string')
    if not isinstance(case['reference_actions'],list) or not all(isinstance(x,str) and x for x in case['reference_actions']):
        raise RealShadowInputError('reference_actions must be a list of non-empty strings')
    if not isinstance(case['risks'],dict) or not all(isinstance(k,str) and isinstance(v,str) for k,v in case['risks'].items()):
        raise RealShadowInputError('risks must map action strings to risk strings')
    if not isinstance(case['source'],dict):
        raise RealShadowInputError('source must be an object describing historical provenance')
    if 'context' in case and not isinstance(case['context'],str):
        raise RealShadowInputError('context must be a string when supplied')
    return case


def live_shadow_input_hash(case):
    canonical={k:case[k] for k in sorted(case) if k not in {'reference_actions','risks'}}
    return hashlib.sha256(json.dumps(canonical,sort_keys=True,separators=(',',':')).encode('utf-8')).hexdigest()


def build_live_shadow_prompt(case):
    context=case.get('context','').strip()
    return (
        'You are operating in read-only shadow mode. Do not invoke tools, perform actions, or claim that an action occurred. '
        'From the historical request below, propose the action labels that the system should recommend. '
        'Return only a JSON object with this exact shape: {"proposed_actions":["action:label"]}.\n\n'
        f'HISTORICAL REQUEST:\n{case["prompt"]}\n\n'
        + (f'CONTEXT:\n{context}\n' if context else '')
    )


def parse_generated_actions(output):
    try:
        data=json.loads(str(output or '').strip())
    except Exception as exc:
        raise RealShadowInputError('model output is not JSON') from exc
    actions=data.get('proposed_actions') if isinstance(data,dict) else None
    if not isinstance(actions,list) or not all(isinstance(x,str) and x for x in actions):
        raise RealShadowInputError('model output must contain proposed_actions as a list of non-empty strings')
    return actions

class RealShadowEvaluator:
    def evaluate(self,cases):
        tp=fp=fn=exact=high_fp=high_fn=0
        for c in cases:
            ref=set(c.get('reference',[])); prop=set(c.get('proposed',[])); risks=c.get('risks',{})
            tp+=len(ref & prop); fp+=len(prop-ref); fn+=len(ref-prop); exact+=int(ref==prop)
            for a in prop-ref:
                if risks.get(a) in {'R3','R4'}: high_fp+=1
            for a in ref-prop:
                if risks.get(a) in {'R3','R4'}: high_fn+=1
        precision=_safe(tp,tp+fp); recall=_safe(tp,tp+fn); f1=_safe(2*precision*recall,precision+recall)
        return {'n':len(cases),'tp':tp,'fp':fp,'fn':fn,'precision':precision,'recall':recall,'f1':f1,
                'exact_action_match_rate':_safe(exact,len(cases)),
                'high_risk_false_positives':high_fp,'high_risk_false_negatives':high_fn}

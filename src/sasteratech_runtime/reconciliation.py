from .security_models import EffectStatus

class Reconciler:
    def __init__(self,effect_ledger,registry):
        self.effects=effect_ledger; self.registry=registry

    def reconcile(self,effect_id,args,raw_result=None):
        effect=self.effects.get(effect_id)
        spec=self.registry.get(effect['tool_id'])
        if not spec.readback or not spec.verify_effect:
            self.effects.mark(effect_id,EffectStatus.UNKNOWN,verification={'reason':'no readback contract'})
            return {'verified':False,'status':'UNKNOWN','reason':'no readback contract'}
        observed=spec.readback(args,raw_result)
        ok=bool(spec.verify_effect(args,raw_result,observed))
        self.effects.mark(effect_id,EffectStatus.VERIFIED if ok else EffectStatus.UNKNOWN,verification={'verified':ok,'observed':observed})
        return {'verified':ok,'status':'VERIFIED' if ok else 'UNKNOWN','observed':observed}

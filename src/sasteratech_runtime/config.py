import json,os
from copy import deepcopy
from pathlib import Path

class ConfigLoader:
    def __init__(self,prefix='SASTERATECH__'): self.prefix=prefix
    @staticmethod
    def _parse(value):
        try: return json.loads(value)
        except json.JSONDecodeError: return value
    @staticmethod
    def _deep_set(obj,path,value):
        cur=obj
        for key in path[:-1]:
            if key not in cur or not isinstance(cur[key],dict): cur[key]={}
            cur=cur[key]
        cur[path[-1]]=value
    def load(self,path,env=None):
        out=deepcopy(json.loads(Path(path).read_text(encoding='utf-8'))); env=os.environ if env is None else env
        for key,value in env.items():
            if not key.startswith(self.prefix): continue
            parts=[p.lower() for p in key[len(self.prefix):].split('__') if p]
            if parts: self._deep_set(out,parts,self._parse(value))
        self.validate(out); return out
    @staticmethod
    def validate(cfg):
        if cfg.get('llm_may_grant_high_risk_approval') is not False: raise ValueError('llm_may_grant_high_risk_approval must remain false')
        budget=cfg.get('limits',{}).get('context_token_budget',1)
        if not isinstance(budget,int) or budget<=0: raise ValueError('context_token_budget must be positive integer')
        if cfg.get('default_risk_ceiling') not in {'R0','R1','R2','R3','R4'}: raise ValueError('invalid default_risk_ceiling')
        return True

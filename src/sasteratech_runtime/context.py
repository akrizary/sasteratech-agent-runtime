from dataclasses import dataclass, field
from math import ceil

class ContextAssemblyError(ValueError): pass

@dataclass
class ContextItem:
    item_id:str; text:str; kind:str; required:bool=False; priority:int=50; relevance:float=0.5; timestamp:str|None=None; explicit_tokens:int|None=None; metadata:dict=field(default_factory=dict)
    @property
    def estimated_tokens(self): return self.explicit_tokens if self.explicit_tokens is not None else max(1,ceil(len(self.text)/4))

class ContextAssembler:
    def __init__(self,token_budget=16000): self.token_budget=token_budget
    def assemble(self,items):
        required=[i for i in items if i.required]; optional=[i for i in items if not i.required]
        used=sum(i.estimated_tokens for i in required)
        if used>self.token_budget: raise ContextAssemblyError(f'required context exceeds budget: {used}>{self.token_budget}')
        optional.sort(key=lambda i:(-i.priority,-i.relevance,i.timestamp or '',i.item_id))
        selected=list(required); dropped=[]
        for item in optional:
            if used+item.estimated_tokens<=self.token_budget: selected.append(item); used+=item.estimated_tokens
            else: dropped.append(item)
        return {'selected':selected,'dropped':dropped,'used_tokens_est':used,'budget':self.token_budget,'coverage':1.0 if not items else len(selected)/len(items)}

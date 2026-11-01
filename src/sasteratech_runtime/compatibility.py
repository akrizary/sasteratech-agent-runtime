import importlib.util
from dataclasses import dataclass
@dataclass(frozen=True)
class DependencyStatus: name:str; available:bool; version:str|None
def inspect_runtime_dependencies():
    out=[]
    for name in ('pydantic_ai','pydantic_ai_harness','opentelemetry'):
        available=importlib.util.find_spec(name) is not None; version=None
        if available:
            try: version=getattr(__import__(name),'__version__',None)
            except Exception: pass
        out.append(DependencyStatus(name,available,version))
    return out

import json
from pathlib import Path
from datetime import datetime, timezone
SECRET_FRAGMENTS=('api_key','authorization','bearer','password','secret','token')
def redact(value):
    if isinstance(value,dict):
        return {k:('[REDACTED]' if any(x in str(k).lower() for x in SECRET_FRAGMENTS) else redact(v)) for k,v in value.items()}
    if isinstance(value,list): return [redact(x) for x in value]
    if isinstance(value,tuple): return tuple(redact(x) for x in value)
    return value
class TelemetrySink:
    def emit(self,event_type,attributes): raise NotImplementedError
class NullTelemetrySink(TelemetrySink):
    def emit(self,event_type,attributes): pass
class InMemoryTelemetrySink(TelemetrySink):
    def __init__(self): self.events=[]
    def emit(self,event_type,attributes): self.events.append({'timestamp':datetime.now(timezone.utc).isoformat(),'event_type':event_type,'attributes':redact(attributes)})
class JsonlTelemetrySink(TelemetrySink):
    def __init__(self,path): self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)
    def emit(self,event_type,attributes):
        row={'timestamp':datetime.now(timezone.utc).isoformat(),'event_type':event_type,'attributes':redact(attributes)}
        with self.path.open('a',encoding='utf-8') as f: f.write(json.dumps(row,sort_keys=True,ensure_ascii=False)+'\n')
class CompositeTelemetrySink(TelemetrySink):
    def __init__(self,*sinks): self.sinks=sinks
    def emit(self,event_type,attributes):
        for s in self.sinks: s.emit(event_type,attributes)
class OpenTelemetrySink(TelemetrySink):
    def __init__(self,tracer_name='sasteratech_runtime'):
        try: from opentelemetry import trace
        except Exception as e: raise RuntimeError('opentelemetry-api is required') from e
        self.tracer=trace.get_tracer(tracer_name)
    def emit(self,event_type,attributes):
        attrs=redact(attributes); flat={}
        for k,v in attrs.items(): flat[str(k)]=('' if v is None else v) if isinstance(v,(str,int,float,bool)) or v is None else json.dumps(v,sort_keys=True,default=str)
        with self.tracer.start_as_current_span(event_type) as span:
            for k,v in flat.items(): span.set_attribute(k,v)

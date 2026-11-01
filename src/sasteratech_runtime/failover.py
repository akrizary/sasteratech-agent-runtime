from .runtime_models import RuntimeStatus, RuntimeResponse

FAILOVER_STATUSES={RuntimeStatus.UNAVAILABLE,RuntimeStatus.TIMEOUT,RuntimeStatus.PROVIDER_ERROR,RuntimeStatus.INTERNAL_ERROR}

class FailoverRuntime:
    def __init__(self, adapters):
        if not adapters: raise ValueError('at least one adapter required')
        self.adapters=tuple(adapters)

    async def run(self,request):
        attempts=[]
        last=None
        for adapter in self.adapters:
            try:
                response=await adapter.run(request)
            except Exception as e:
                attempts.append({'adapter':adapter.adapter_id,'status':'EXCEPTION','error':type(e).__name__})
                last=RuntimeResponse(RuntimeStatus.UNAVAILABLE,error_type=type(e).__name__,error_message=str(e))
                continue
            attempts.append({'adapter':adapter.adapter_id,'status':response.status.value})
            last=response
            if response.status==RuntimeStatus.COMPLETE:
                response.metadata=dict(response.metadata or {})
                response.metadata['failover_attempts']=attempts
                return response
            if response.status not in FAILOVER_STATUSES:
                response.metadata=dict(response.metadata or {})
                response.metadata['failover_attempts']=attempts
                return response
        last.metadata=dict(last.metadata or {})
        last.metadata['failover_attempts']=attempts
        return last

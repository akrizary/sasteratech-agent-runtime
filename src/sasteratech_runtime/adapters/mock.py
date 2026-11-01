from ..runtime import RuntimeAdapter
from ..runtime_models import RuntimeResponse, RuntimeStatus, UsageReport
class MockRuntimeAdapter(RuntimeAdapter):
    adapter_id='mock'
    def __init__(self,responder=None): self.responder=responder or (lambda req:f'MOCK:{req.role.value}:{req.prompt[:80]}'); self.requests=[]
    async def run(self,request):
        self.requests.append(request); out=self.responder(request)
        return RuntimeResponse(RuntimeStatus.COMPLETE,out,f'mock-{request.run_id}-{len(self.requests)}',f'mock-conv-{request.run_id}',UsageReport(requests=1,total_tokens=min(100,request.budget.max_tokens)),'[]',metadata={'adapter':'mock'})

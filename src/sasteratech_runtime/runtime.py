from abc import ABC, abstractmethod
class RuntimeAdapter(ABC):
    adapter_id='abstract'
    def available(self): return True
    @abstractmethod
    async def run(self,request): raise NotImplementedError
class RuntimeRegistry:
    def __init__(self,adapters=()):
        self._adapters={}
        for a in adapters: self.register(a)
    def register(self,adapter):
        if adapter.adapter_id in self._adapters: raise ValueError(f'duplicate runtime adapter: {adapter.adapter_id}')
        self._adapters[adapter.adapter_id]=adapter
    def get(self,adapter_id):
        if adapter_id not in self._adapters: raise KeyError(f'unknown runtime adapter: {adapter_id}')
        return self._adapters[adapter_id]
    async def run(self,request): return await self.get(request.model.adapter_id).run(request)

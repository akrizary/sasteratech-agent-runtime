class ToolRegistry:
    def __init__(self): self._tools={}
    def register(self,tool):
        if tool.id in self._tools: raise ValueError(f"duplicate tool id: {tool.id}")
        self._tools[tool.id]=tool
    def get(self,tool_id): return self._tools[tool_id]
    def list_for_risk(self,max_rank):
        rank={"R0":0,"R1":1,"R2":2,"R3":3,"R4":4}
        return [t for t in self._tools.values() if rank[t.risk.value] <= max_rank]

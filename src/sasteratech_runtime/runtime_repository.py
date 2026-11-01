import json, uuid
from datetime import datetime, timezone
class RuntimeCallRepository:
    def __init__(self,store): self.store=store
    def start(self,request):
        call_id=f'CALL-{uuid.uuid4()}'; now=datetime.now(timezone.utc).isoformat()
        with self.store.transaction():
            self.store.conn.execute('INSERT INTO runtime_calls(call_id,run_id,packet_id,task_id,adapter_id,model_alias,model_id,status,started_at,metadata_json) VALUES(?,?,?,?,?,?,?,?,?,?)',(call_id,request.run_id,request.packet_id,request.task_id,request.model.adapter_id,request.model.alias,request.model.model_id,'RUNNING',now,json.dumps(request.metadata,sort_keys=True)))
        return call_id
    def finish(self,call_id,response):
        now=datetime.now(timezone.utc).isoformat()
        with self.store.transaction():
            cur=self.store.conn.execute('UPDATE runtime_calls SET status=?,completed_at=?,runtime_run_id=?,conversation_id=?,usage_json=?,error_type=?,metadata_json=? WHERE call_id=?',(response.status.value,now,response.runtime_run_id,response.conversation_id,json.dumps(response.usage.__dict__,sort_keys=True),response.error_type,json.dumps(response.metadata,sort_keys=True),call_id))
            if cur.rowcount != 1: raise KeyError(call_id)
    def get(self,call_id):
        r=self.store.conn.execute('SELECT * FROM runtime_calls WHERE call_id=?',(call_id,)).fetchone()
        if r is None: raise KeyError(call_id)
        return dict(r)

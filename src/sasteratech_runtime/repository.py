import json
from datetime import datetime,timezone
class RunRepository:
    def __init__(self,store): self.store=store
    def create(self,run_id,task_class,state,parent_run_id=None,metadata=None):
        now=datetime.now(timezone.utc).isoformat()
        with self.store.transaction(): self.store.conn.execute('INSERT INTO runs(run_id,parent_run_id,task_class,state,created_at,updated_at,metadata_json) VALUES(?,?,?,?,?,?,?)',(run_id,parent_run_id,task_class,state,now,now,json.dumps(metadata or {},sort_keys=True)))
    def update_state(self,run_id,state):
        now=datetime.now(timezone.utc).isoformat()
        with self.store.transaction():
            cur=self.store.conn.execute('UPDATE runs SET state=?,updated_at=? WHERE run_id=?',(state,now,run_id))
            if cur.rowcount!=1: raise KeyError(run_id)
    def get(self,run_id):
        r=self.store.conn.execute('SELECT * FROM runs WHERE run_id=?',(run_id,)).fetchone()
        if r is None: raise KeyError(run_id)
        return dict(r)

import json, uuid
from datetime import datetime, timezone
class CheckpointRepository:
    def __init__(self,store): self.store=store
    def save(self,run_id,state,runtime_ref=None,stable=True,metadata=None):
        row=self.store.conn.execute('SELECT max(seq) AS seq FROM checkpoints WHERE run_id=?',(run_id,)).fetchone()
        seq=1 if row is None or row['seq'] is None else row['seq']+1
        cid=f'CHK-{uuid.uuid4()}'; now=datetime.now(timezone.utc).isoformat()
        with self.store.transaction():
            self.store.conn.execute('INSERT INTO checkpoints(run_id,seq,checkpoint_id,created_at,stable,state_json,runtime_ref,metadata_json) VALUES(?,?,?,?,?,?,?,?)',(run_id,seq,cid,now,int(stable),json.dumps(state,sort_keys=True),runtime_ref,json.dumps(metadata or {},sort_keys=True)))
        return cid
    def latest(self,run_id,stable_only=True):
        q='SELECT * FROM checkpoints WHERE run_id=?'; args=[run_id]
        if stable_only: q+=' AND stable=1'
        q+=' ORDER BY seq DESC LIMIT 1'
        r=self.store.conn.execute(q,args).fetchone(); return None if r is None else dict(r)

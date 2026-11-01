import json, uuid
from datetime import datetime, timezone
from .security_models import EffectStatus

class ReplayBlocked(RuntimeError): pass

class EffectLedger:
    def __init__(self,store): self.store=store

    def reserve(self,run_id,action_id,tool_id,resource,idempotency_key,idempotent,args_redacted):
        existing=self.store.conn.execute(
            'SELECT * FROM tool_effects WHERE tool_id=? AND idempotency_key=? ORDER BY created_at DESC LIMIT 1',
            (tool_id,idempotency_key)
        ).fetchone() if idempotency_key else None
        if existing:
            status=EffectStatus(existing['status'])
            if bool(existing['idempotent']) and status in {EffectStatus.SUCCEEDED,EffectStatus.VERIFIED}:
                return dict(existing),True
            if (not bool(existing['idempotent'])) and status == EffectStatus.VERIFIED:
                raise ReplayBlocked(f'non-idempotent effect already verified for idempotency key: {idempotency_key}; create a new action to execute again')
            if status in {EffectStatus.RESERVED,EffectStatus.STARTED,EffectStatus.SUCCEEDED,EffectStatus.UNKNOWN}:
                raise ReplayBlocked(f'prior effect unresolved for idempotency key: {idempotency_key}')
        eid=f'EFF-{uuid.uuid4()}'; now=datetime.now(timezone.utc).isoformat()
        with self.store.transaction():
            self.store.conn.execute(
                'INSERT INTO tool_effects(effect_id,run_id,action_id,tool_id,resource,idempotency_key,idempotent,status,args_json,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)',
                (eid,run_id,action_id,tool_id,resource,idempotency_key,int(idempotent),EffectStatus.RESERVED.value,json.dumps(args_redacted,sort_keys=True),now,now)
            )
        return self.get(eid),False

    def mark(self,effect_id,status,*,result=None,verification=None,error=None):
        now=datetime.now(timezone.utc).isoformat()
        with self.store.transaction():
            self.store.conn.execute(
                'UPDATE tool_effects SET status=?,result_json=?,verification_json=?,error=?,updated_at=? WHERE effect_id=?',
                (EffectStatus(status).value,json.dumps(result,sort_keys=True,default=str) if result is not None else None,
                 json.dumps(verification,sort_keys=True,default=str) if verification is not None else None,error,now,effect_id)
            )

    def get(self,effect_id):
        r=self.store.conn.execute('SELECT * FROM tool_effects WHERE effect_id=?',(effect_id,)).fetchone()
        if r is None: raise KeyError(effect_id)
        return dict(r)

    def unresolved(self):
        rows=self.store.conn.execute("SELECT * FROM tool_effects WHERE status IN ('RESERVED','STARTED','SUCCEEDED','UNKNOWN')").fetchall()
        return [dict(r) for r in rows]

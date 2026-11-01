import json, uuid
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from .models import Risk, ApprovalGrant

@dataclass(frozen=True)
class ApprovalRequest:
    request_id:str
    run_id:str
    action_id:str
    tool_id:str
    resource:str
    risk:Risk
    reason:str
    created_at:datetime
    expires_at:datetime
    status:str='PENDING'

class ApprovalService:
    def __init__(self,store): self.store=store

    def request(self,run_id,action_id,tool_id,resource,risk,reason,ttl_seconds=1800):
        # Avoid creating duplicate pending requests for the same action.
        existing=self.store.conn.execute(
            "SELECT request_id FROM approval_requests WHERE run_id=? AND action_id=? AND status='PENDING' ORDER BY created_at DESC LIMIT 1",
            (run_id,action_id)
        ).fetchone()
        if existing: return existing['request_id']
        now=datetime.now(timezone.utc); rid=f'APRREQ-{uuid.uuid4()}'; exp=now+timedelta(seconds=ttl_seconds)
        with self.store.transaction():
            self.store.conn.execute(
                'INSERT INTO approval_requests(request_id,run_id,action_id,tool_id,resource,risk,reason,status,created_at,expires_at) VALUES(?,?,?,?,?,?,?,?,?,?)',
                (rid,run_id,action_id,tool_id,resource,risk.value,reason,'PENDING',now.isoformat(),exp.isoformat())
            )
        return rid

    def grant_human(self,request_id,human_id,expires_in_seconds=1800):
        if not str(human_id).strip(): raise ValueError('human_id required')
        r=self.store.conn.execute('SELECT * FROM approval_requests WHERE request_id=?',(request_id,)).fetchone()
        if r is None: raise KeyError(request_id)
        if r['status']!='PENDING': raise ValueError('approval request is not pending')
        now=datetime.now(timezone.utc); req_exp=datetime.fromisoformat(r['expires_at'])
        if req_exp <= now:
            self._set_status(request_id,'EXPIRED'); raise ValueError('approval request expired')
        grant_exp=min(req_exp,now+timedelta(seconds=expires_in_seconds)); gid=f'APR-{uuid.uuid4()}'; nonce=str(uuid.uuid4())
        with self.store.transaction():
            self.store.conn.execute(
                'INSERT INTO approvals(approval_id,run_id,risk_ceiling,actions_json,resource_scope_json,issued_by,expires_at,nonce) VALUES(?,?,?,?,?,?,?,?)',
                (gid,r['run_id'],r['risk'],json.dumps([r['tool_id']]),json.dumps([r['resource']]),'human',grant_exp.isoformat(),nonce)
            )
            self.store.conn.execute(
                'INSERT INTO approval_bindings(approval_id,request_id,run_id,action_id) VALUES(?,?,?,?)',
                (gid,request_id,r['run_id'],r['action_id'])
            )
            self.store.conn.execute(
                'UPDATE approval_requests SET status=?,decided_at=?,decided_by=?,grant_id=? WHERE request_id=?',
                ('GRANTED',now.isoformat(),human_id,gid,request_id)
            )
        return ApprovalGrant(gid,Risk(r['risk']),(r['tool_id'],),(r['resource'],),'human',grant_exp,nonce,r['run_id'],r['action_id'])

    def load_grant(self,approval_id):
        r=self.store.conn.execute(
            'SELECT a.*,b.action_id AS bound_action_id,b.run_id AS bound_run_id FROM approvals a LEFT JOIN approval_bindings b ON a.approval_id=b.approval_id WHERE a.approval_id=?',
            (approval_id,)
        ).fetchone()
        if r is None: raise KeyError(approval_id)
        exp=datetime.fromisoformat(r['expires_at']) if r['expires_at'] else None
        return ApprovalGrant(r['approval_id'],Risk(r['risk_ceiling']),tuple(json.loads(r['actions_json'])),tuple(json.loads(r['resource_scope_json'])),r['issued_by'],exp,r['nonce'],r['bound_run_id'] or r['run_id'],r['bound_action_id'])

    def deny(self,request_id,human_id):
        r=self.store.conn.execute('SELECT status FROM approval_requests WHERE request_id=?',(request_id,)).fetchone()
        if r is None: raise KeyError(request_id)
        if r['status']!='PENDING': raise ValueError('approval request is not pending')
        now=datetime.now(timezone.utc).isoformat()
        with self.store.transaction():
            self.store.conn.execute('UPDATE approval_requests SET status=?,decided_at=?,decided_by=? WHERE request_id=?',('DENIED',now,human_id,request_id))

    def _set_status(self,request_id,status):
        with self.store.transaction(): self.store.conn.execute('UPDATE approval_requests SET status=? WHERE request_id=?',(status,request_id))

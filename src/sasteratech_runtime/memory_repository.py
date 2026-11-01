import json
from datetime import datetime,timezone
from .memory import MemoryCandidate

class TemporalMemoryRepository:
    def __init__(self,store): self.store=store

    @staticmethod
    def _iso(v): return None if v is None else v.isoformat()

    def put(self,m,run_id=None):
        with self.store.transaction():
            self.store.conn.execute(
                """INSERT INTO memory_records(
                   memory_id,run_id,kind,content,source_refs_json,evidence_refs_json,writer,
                   sensitivity_ok,unresolved_contradiction,ttl,valid_from,valid_to,
                   supersedes_json,superseded_by_json,transaction_time,scope
                   ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (m.memory_id,run_id,m.kind,m.content,json.dumps(m.source_refs),json.dumps(m.evidence_refs),m.writer,
                 int(m.sensitivity_ok),int(m.unresolved_contradiction),m.ttl,self._iso(m.valid_from),self._iso(m.valid_to),
                 json.dumps(m.supersedes),json.dumps(m.superseded_by),self._iso(m.transaction_time),m.scope)
            )
            for old_id in m.supersedes:
                old=self.store.conn.execute('SELECT superseded_by_json,valid_to FROM memory_records WHERE memory_id=?',(old_id,)).fetchone()
                if old is None: raise KeyError(old_id)
                sb=json.loads(old['superseded_by_json']);
                if m.memory_id not in sb: sb.append(m.memory_id)
                valid_to=old['valid_to'] or self._iso(m.valid_from)
                self.store.conn.execute('UPDATE memory_records SET superseded_by_json=?,valid_to=? WHERE memory_id=?',(json.dumps(sb),valid_to,old_id))

    def get(self,memory_id):
        r=self.store.conn.execute('SELECT * FROM memory_records WHERE memory_id=?',(memory_id,)).fetchone()
        if r is None: raise KeyError(memory_id)
        def dt(x): return None if x is None else datetime.fromisoformat(x)
        return MemoryCandidate(
            r['memory_id'],r['content'],r['kind'],json.loads(r['source_refs_json']),json.loads(r['evidence_refs_json']),r['writer'],
            bool(r['sensitivity_ok']),bool(r['unresolved_contradiction']),r['ttl'],dt(r['valid_from']),dt(r['valid_to']),
            json.loads(r['supersedes_json']),json.loads(r['superseded_by_json']),dt(r['transaction_time']),r['scope']
        )

    def as_of(self,when,kind=None,scope=None):
        iso=when.isoformat(); q='SELECT memory_id FROM memory_records WHERE (valid_from IS NULL OR valid_from<=?) AND (valid_to IS NULL OR valid_to>?)'; args=[iso,iso]
        if kind: q+=' AND kind=?'; args.append(kind)
        if scope: q+=' AND scope=?'; args.append(scope)
        q+=' ORDER BY COALESCE(valid_from,\'0001-01-01T00:00:00+00:00\') DESC, transaction_time DESC'
        return [self.get(r['memory_id']) for r in self.store.conn.execute(q,args).fetchall()]

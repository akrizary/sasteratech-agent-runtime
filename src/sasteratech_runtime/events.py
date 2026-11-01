import json,hashlib,uuid
from datetime import datetime,timezone

class EventIntegrityError(ValueError): pass

class EventLog:
    def __init__(self,store): self.store=store
    @staticmethod
    def _hash(prev,run_id,seq,timestamp,event_type,payload_json):
        material='|'.join([prev or '',run_id,str(seq),timestamp,event_type,payload_json]).encode('utf-8')
        return hashlib.sha256(material).hexdigest()
    def append(self,run_id,event_type,payload):
        payload_json=json.dumps(payload,sort_keys=True,separators=(',',':'),ensure_ascii=False)
        row=self.store.conn.execute('SELECT seq,event_hash FROM events WHERE run_id=? ORDER BY seq DESC LIMIT 1',(run_id,)).fetchone()
        seq=1 if row is None else row['seq']+1; prev=None if row is None else row['event_hash']; ts=datetime.now(timezone.utc).isoformat(); h=self._hash(prev,run_id,seq,ts,event_type,payload_json); eid=f'EVT-{uuid.uuid4()}'
        with self.store.transaction(): self.store.conn.execute('INSERT INTO events(run_id,seq,event_id,timestamp,event_type,payload_json,previous_hash,event_hash) VALUES(?,?,?,?,?,?,?,?)',(run_id,seq,eid,ts,event_type,payload_json,prev,h))
        return eid
    def verify(self,run_id):
        rows=self.store.conn.execute('SELECT * FROM events WHERE run_id=? ORDER BY seq',(run_id,)).fetchall(); prev=None
        for expected,r in enumerate(rows,1):
            if r['seq']!=expected: raise EventIntegrityError(f'sequence gap at {expected}')
            if r['previous_hash']!=prev: raise EventIntegrityError(f'previous hash mismatch at seq {r["seq"]}')
            calc=self._hash(prev,run_id,r['seq'],r['timestamp'],r['event_type'],r['payload_json'])
            if calc!=r['event_hash']: raise EventIntegrityError(f'event hash mismatch at seq {r["seq"]}')
            prev=r['event_hash']
        return True

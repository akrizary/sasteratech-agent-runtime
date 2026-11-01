import json,uuid
from datetime import datetime,timezone

class EvalRepository:
    def __init__(self,store): self.store=store
    def start(self,suite_version,metadata=None):
        eid=f'EVAL-{uuid.uuid4()}'; now=datetime.now(timezone.utc).isoformat()
        with self.store.transaction():
            self.store.conn.execute(
                'INSERT INTO eval_runs(eval_run_id,suite_version,status,started_at,metadata_json) VALUES(?,?,?,?,?)',
                (eid,suite_version,'RUNNING',now,json.dumps(metadata or {},sort_keys=True)))
        return eid
    def record(self,eval_run_id,outcome):
        with self.store.transaction():
            self.store.conn.execute(
                'INSERT INTO eval_results(eval_run_id,case_id,tier,passed,score,actual_json,expected_json,details_json) VALUES(?,?,?,?,?,?,?,?)',
                (eval_run_id,outcome.case_id,outcome.tier.value,int(outcome.passed),outcome.score,
                 json.dumps(outcome.actual,sort_keys=True,default=str),json.dumps(outcome.expected,sort_keys=True,default=str),json.dumps(outcome.details,sort_keys=True,default=str)))
    def finish(self,eval_run_id,status,summary):
        now=datetime.now(timezone.utc).isoformat()
        with self.store.transaction():
            self.store.conn.execute('UPDATE eval_runs SET status=?,completed_at=?,summary_json=? WHERE eval_run_id=?',
                                    (status,now,json.dumps(summary,sort_keys=True,default=str),eval_run_id))

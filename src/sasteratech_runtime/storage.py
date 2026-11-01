import sqlite3
from contextlib import contextmanager
from pathlib import Path

SCHEMA_VERSION=5
DDL=[
'CREATE TABLE IF NOT EXISTS schema_migrations(version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL)',
"CREATE TABLE IF NOT EXISTS runs(run_id TEXT PRIMARY KEY,parent_run_id TEXT,task_class TEXT,state TEXT NOT NULL,created_at TEXT NOT NULL,updated_at TEXT NOT NULL,metadata_json TEXT NOT NULL DEFAULT '{}')",
"CREATE TABLE IF NOT EXISTS plan_tasks(run_id TEXT NOT NULL,task_id TEXT NOT NULL,title TEXT NOT NULL,status TEXT NOT NULL,risk TEXT NOT NULL,owner_role TEXT,dependencies_json TEXT NOT NULL,evidence_requirements_json TEXT NOT NULL,metadata_json TEXT NOT NULL DEFAULT '{}',PRIMARY KEY(run_id,task_id),FOREIGN KEY(run_id) REFERENCES runs(run_id) ON DELETE CASCADE)",
'CREATE TABLE IF NOT EXISTS events(run_id TEXT NOT NULL,seq INTEGER NOT NULL,event_id TEXT NOT NULL UNIQUE,timestamp TEXT NOT NULL,event_type TEXT NOT NULL,payload_json TEXT NOT NULL,previous_hash TEXT,event_hash TEXT NOT NULL,PRIMARY KEY(run_id,seq))',
"CREATE TABLE IF NOT EXISTS artifacts(artifact_id TEXT PRIMARY KEY,run_id TEXT,step_id TEXT,path TEXT NOT NULL,sha256 TEXT NOT NULL,size_bytes INTEGER NOT NULL,media_type TEXT,created_at TEXT NOT NULL,canonical INTEGER NOT NULL DEFAULT 0,parents_json TEXT NOT NULL DEFAULT '[]',supersedes TEXT,metadata_json TEXT NOT NULL DEFAULT '{}',FOREIGN KEY(run_id) REFERENCES runs(run_id) ON DELETE SET NULL)",
'CREATE TABLE IF NOT EXISTS evidence(evidence_id TEXT PRIMARY KEY,run_id TEXT,kind TEXT NOT NULL,payload_json TEXT NOT NULL,recorded_at TEXT NOT NULL,FOREIGN KEY(run_id) REFERENCES runs(run_id) ON DELETE CASCADE)',
'CREATE TABLE IF NOT EXISTS approvals(approval_id TEXT PRIMARY KEY,run_id TEXT,risk_ceiling TEXT NOT NULL,actions_json TEXT NOT NULL,resource_scope_json TEXT NOT NULL,issued_by TEXT NOT NULL,expires_at TEXT,nonce TEXT,FOREIGN KEY(run_id) REFERENCES runs(run_id) ON DELETE CASCADE)',
"CREATE TABLE IF NOT EXISTS runtime_calls(call_id TEXT PRIMARY KEY,run_id TEXT NOT NULL,packet_id TEXT NOT NULL,task_id TEXT NOT NULL,adapter_id TEXT NOT NULL,model_alias TEXT NOT NULL,model_id TEXT,status TEXT NOT NULL,started_at TEXT NOT NULL,completed_at TEXT,runtime_run_id TEXT,conversation_id TEXT,usage_json TEXT NOT NULL DEFAULT '{}',error_type TEXT,metadata_json TEXT NOT NULL DEFAULT '{}',FOREIGN KEY(run_id) REFERENCES runs(run_id) ON DELETE CASCADE)",
"CREATE TABLE IF NOT EXISTS checkpoints(run_id TEXT NOT NULL,seq INTEGER NOT NULL,checkpoint_id TEXT NOT NULL UNIQUE,created_at TEXT NOT NULL,stable INTEGER NOT NULL,state_json TEXT NOT NULL,runtime_ref TEXT,metadata_json TEXT NOT NULL DEFAULT '{}',PRIMARY KEY(run_id,seq),FOREIGN KEY(run_id) REFERENCES runs(run_id) ON DELETE CASCADE)",
"CREATE TABLE IF NOT EXISTS approval_requests(request_id TEXT PRIMARY KEY,run_id TEXT NOT NULL,action_id TEXT NOT NULL,tool_id TEXT NOT NULL,resource TEXT NOT NULL,risk TEXT NOT NULL,reason TEXT NOT NULL,status TEXT NOT NULL,created_at TEXT NOT NULL,expires_at TEXT NOT NULL,decided_at TEXT,decided_by TEXT,grant_id TEXT,FOREIGN KEY(run_id) REFERENCES runs(run_id) ON DELETE CASCADE)",
"CREATE TABLE IF NOT EXISTS tool_effects(effect_id TEXT PRIMARY KEY,run_id TEXT NOT NULL,action_id TEXT NOT NULL,tool_id TEXT NOT NULL,resource TEXT NOT NULL,idempotency_key TEXT,idempotent INTEGER NOT NULL,status TEXT NOT NULL,args_json TEXT NOT NULL,result_json TEXT,verification_json TEXT,error TEXT,created_at TEXT NOT NULL,updated_at TEXT NOT NULL,FOREIGN KEY(run_id) REFERENCES runs(run_id) ON DELETE CASCADE)",
"CREATE TABLE IF NOT EXISTS approval_bindings(approval_id TEXT PRIMARY KEY,request_id TEXT NOT NULL,run_id TEXT NOT NULL,action_id TEXT NOT NULL,FOREIGN KEY(approval_id) REFERENCES approvals(approval_id) ON DELETE CASCADE,FOREIGN KEY(request_id) REFERENCES approval_requests(request_id) ON DELETE CASCADE)",
'CREATE INDEX IF NOT EXISTS idx_tool_effects_idem ON tool_effects(tool_id,idempotency_key)',
'CREATE INDEX IF NOT EXISTS idx_approval_requests_run ON approval_requests(run_id,status)',
"""CREATE TABLE IF NOT EXISTS eval_runs(
    eval_run_id TEXT PRIMARY KEY,
    suite_version TEXT NOT NULL,
    status TEXT NOT NULL,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    summary_json TEXT
)""",
"""CREATE TABLE IF NOT EXISTS eval_results(
    eval_run_id TEXT NOT NULL,
    case_id TEXT NOT NULL,
    tier TEXT NOT NULL,
    passed INTEGER NOT NULL,
    score REAL NOT NULL,
    actual_json TEXT,
    expected_json TEXT,
    details_json TEXT NOT NULL DEFAULT '{}',
    PRIMARY KEY(eval_run_id,case_id),
    FOREIGN KEY(eval_run_id) REFERENCES eval_runs(eval_run_id) ON DELETE CASCADE
)""",
'CREATE INDEX IF NOT EXISTS idx_eval_results_tier ON eval_results(eval_run_id,tier)',
"""CREATE TABLE IF NOT EXISTS memory_records(
    memory_id TEXT PRIMARY KEY,
    run_id TEXT,
    kind TEXT NOT NULL,
    content TEXT NOT NULL,
    source_refs_json TEXT NOT NULL DEFAULT '[]',
    evidence_refs_json TEXT NOT NULL DEFAULT '[]',
    writer TEXT,
    sensitivity_ok INTEGER NOT NULL DEFAULT 1,
    unresolved_contradiction INTEGER NOT NULL DEFAULT 0,
    ttl TEXT,
    valid_from TEXT,
    valid_to TEXT,
    supersedes_json TEXT NOT NULL DEFAULT '[]',
    superseded_by_json TEXT NOT NULL DEFAULT '[]',
    transaction_time TEXT NOT NULL,
    scope TEXT,
    FOREIGN KEY(run_id) REFERENCES runs(run_id) ON DELETE SET NULL
)""",
'CREATE INDEX IF NOT EXISTS idx_memory_temporal ON memory_records(kind,scope,valid_from,valid_to)',
]

class SQLiteStore:
    def __init__(self,path):
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)
        self.conn=sqlite3.connect(self.path); self.conn.row_factory=sqlite3.Row
        self.conn.execute('PRAGMA foreign_keys=ON'); self.conn.execute('PRAGMA journal_mode=WAL'); self.migrate()
    @contextmanager
    def transaction(self):
        try:
            self.conn.execute('BEGIN'); yield self.conn; self.conn.commit()
        except Exception:
            self.conn.rollback(); raise
    def migrate(self):
        with self.transaction():
            for ddl in DDL: self.conn.execute(ddl)
            if not self.conn.execute('SELECT 1 FROM schema_migrations WHERE version=?',(SCHEMA_VERSION,)).fetchone():
                self.conn.execute("INSERT INTO schema_migrations(version,applied_at) VALUES(?,datetime('now'))",(SCHEMA_VERSION,))
    def close(self): self.conn.close()

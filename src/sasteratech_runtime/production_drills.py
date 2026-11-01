import sqlite3, tempfile, shutil, hashlib
from pathlib import Path
from .storage import SQLiteStore, SCHEMA_VERSION
from .repository import RunRepository
from .models import ToolDefinition, Risk
from .roles import Role
from .actions import ActionIntent
from .executable_tools import ExecutableToolRegistry, ToolRuntimeSpec
from .approval_service import ApprovalService
from .tool_gateway import ToolGateway
from .effects import EffectLedger
from .security_models import EffectStatus

class ProductionDrills:
    @staticmethod
    def crash_recovery():
        with tempfile.TemporaryDirectory() as td:
            td=Path(td); db=td/'sasteratech.db'; target=td/'effect.txt'
            store=SQLiteStore(db); RunRepository(store).create('RUN','BUILD','STATE_0_READ_ONLY_AUDIT')
            registry=ExecutableToolRegistry()
            tool=ToolDefinition('file.write','1',Risk.R2,True,True,idempotent=False,reversible=True)
            def handler(args):
                target.write_text(args['text'],encoding='utf-8')
                raise RuntimeError('simulated crash after effect')
            def readback(args,raw): return target.read_text(encoding='utf-8') if target.exists() else None
            def verify(args,raw,observed): return observed==args['text']
            registry.register(ToolRuntimeSpec(tool,handler,readback=readback,verify_effect=verify,output_trust='TRUSTED_LOCAL'))
            approvals=ApprovalService(store); gateway=ToolGateway(registry,store=store,approval_service=approvals)
            intent=ActionIntent('builder',Role.BUILDER,'file.write',str(target),Risk.R2,'drill',resource_scope=(str(td/'*'),))
            first=gateway.execute('RUN',intent,{'text':'once'},idempotency_key='DRILL-IDEM')
            if first.status!='APPROVAL_REQUIRED': return {'passed':False,'stage':'approval','status':first.status}
            grant=approvals.grant_human(first.approval_request_id,'drill-human')
            second=gateway.execute('RUN',intent,{'text':'once'},grants=(grant,),idempotency_key='DRILL-IDEM')
            if second.status!='FAILED' or not target.exists(): return {'passed':False,'stage':'crash','status':second.status}
            row=EffectLedger(store).get(second.effect_id)
            if row['status']!='UNKNOWN': return {'passed':False,'stage':'unknown_effect','status':row['status']}
            third=gateway.execute('RUN',intent,{'text':'once'},grants=(grant,),idempotency_key='DRILL-IDEM')
            if third.status!='RECONCILIATION_REQUIRED': return {'passed':False,'stage':'replay_block','status':third.status}
            EffectLedger(store).mark(second.effect_id,EffectStatus.VERIFIED,verification={'verified':True,'observed':'once'})
            fourth=gateway.execute('RUN',intent,{'text':'once'},grants=(grant,),idempotency_key='DRILL-IDEM')
            store.close()
            return {'passed':fourth.status=='RECONCILIATION_REQUIRED','stage':'verified_non_idempotent_replay','status':fourth.status}

    @staticmethod
    def migration_rollback():
        with tempfile.TemporaryDirectory() as td:
            td=Path(td); legacy=td/'legacy.db'; backup=td/'legacy.backup.db'
            c=sqlite3.connect(legacy)
            c.execute('CREATE TABLE schema_migrations(version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL)')
            c.execute("INSERT INTO schema_migrations VALUES(2,'legacy')")
            c.execute("CREATE TABLE runs(run_id TEXT PRIMARY KEY,parent_run_id TEXT,task_class TEXT,state TEXT NOT NULL,created_at TEXT NOT NULL,updated_at TEXT NOT NULL,metadata_json TEXT NOT NULL DEFAULT '{}')")
            c.execute("INSERT INTO runs VALUES('LEGACY',NULL,'RESEARCH','STATE_0_READ_ONLY_AUDIT','a','a','{}')")
            c.commit(); c.close(); shutil.copy2(legacy,backup)
            before=hashlib.sha256(backup.read_bytes()).hexdigest()
            s=SQLiteStore(legacy)
            version=s.conn.execute('SELECT max(version) v FROM schema_migrations').fetchone()['v']
            row=s.conn.execute("SELECT run_id FROM runs WHERE run_id='LEGACY'").fetchone()
            integrity=s.conn.execute('PRAGMA integrity_check').fetchone()[0]
            migrated_ok=(version==SCHEMA_VERSION and row is not None and integrity=='ok')
            s.close()
            shutil.copy2(backup,legacy)
            after=hashlib.sha256(legacy.read_bytes()).hexdigest()
            c=sqlite3.connect(legacy); restored=c.execute("SELECT run_id FROM runs WHERE run_id='LEGACY'").fetchone(); restored_integrity=c.execute('PRAGMA integrity_check').fetchone()[0]; c.close()
            return {'passed':migrated_ok and before==after and restored is not None and restored_integrity=='ok',
                    'migrated_version':version,'backup_hash_restored':before==after,'integrity':restored_integrity}

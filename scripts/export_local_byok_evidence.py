"""Export a redacted, verifiable local-BYOK evidence bundle."""
from pathlib import Path
import datetime, hashlib, json, sqlite3, sys, zipfile

ROOT=Path(__file__).parents[1]; sys.path.insert(0,str(ROOT/'src'))
from sasteratech_runtime.live_validation import verify_manifest, sha256_file
from sasteratech_runtime.secrets import SecretBoundary

STATE=ROOT/'state'; OUT=ROOT/'evidence'/'local_byok'; OUT.mkdir(parents=True,exist_ok=True)
if not verify_manifest(ROOT)['valid']: raise SystemExit('REJECT: package manifest invalid')
def rows(db, sql):
    con=sqlite3.connect(db); con.row_factory=sqlite3.Row
    try: return [dict(r) for r in con.execute(sql)]
    finally: con.close()
metadata=rows(STATE/'local_byok_metadata.db','SELECT credential_id,provider,masked_suffix,status,created_at,last_test_at,last_test_status FROM credential_metadata')
reservations=rows(STATE/'local_byok_budget.db','SELECT reservation_id,account_id,request_id,reserved_usd,state,created_at,expires_at FROM budget_reservation')
receipts=rows(STATE/'local_byok_budget.db','SELECT receipt_id,reservation_id,actual_usd,cost_status,created_at FROM usage_receipt')
audit=(STATE/'local_byok_audit.jsonl').read_text(encoding='utf-8').splitlines()
payload={'artifact_version':'1.1.0a0','generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'credential_metadata':metadata,'reservations':reservations,'receipts':receipts,'audit_events':[json.loads(x) for x in audit]}
if SecretBoundary().contains_secret(payload): raise SystemExit('REJECT: secret-like value detected in local evidence')
status=OUT/'local_byok_status.json'; status.write_text(json.dumps(payload,indent=2),encoding='utf-8')
audit_out=OUT/'local_byok_audit.jsonl'; audit_out.write_text('\n'.join(audit)+'\n',encoding='utf-8')
att={'artifact_version':'1.1.0a0','package_manifest_sha256':sha256_file(ROOT/'MANIFEST.sha256'),'files':{p.name:sha256_file(p) for p in (status,audit_out)}}
(OUT/'LOCAL_BYOK_ATTESTATION.json').write_text(json.dumps(att,indent=2),encoding='utf-8')
bundle=ROOT/'LOCAL_BYOK_EVIDENCE_BUNDLE.zip'
with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
    for p in (status,audit_out,OUT/'LOCAL_BYOK_ATTESTATION.json'): z.write(p,arcname=f'local_byok/{p.name}')
print(json.dumps({'bundle':str(bundle),'settled_receipts':len(receipts),'secret_scan':'PASS'},indent=2))

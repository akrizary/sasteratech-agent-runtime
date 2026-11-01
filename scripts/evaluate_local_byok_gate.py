"""Fail-closed local BYOK Phase-A evidence gate."""
from pathlib import Path
import hashlib,json,sys,zipfile
ROOT=Path(__file__).parents[1]; bundle=ROOT/'LOCAL_BYOK_EVIDENCE_BUNDLE.zip'
if not bundle.exists(): raise SystemExit('BLOCKED: missing LOCAL_BYOK_EVIDENCE_BUNDLE.zip')
with zipfile.ZipFile(bundle) as z:
    names=set(z.namelist()); needed={'local_byok/local_byok_status.json','local_byok/local_byok_audit.jsonl','local_byok/LOCAL_BYOK_ATTESTATION.json'}
    if not needed <= names: raise SystemExit('BLOCKED: evidence bundle incomplete')
    status=json.loads(z.read('local_byok/local_byok_status.json'))
    events=[json.loads(x) for x in z.read('local_byok/local_byok_audit.jsonl').decode().splitlines() if x]
chain=all(e.get('previous_event_hash')==(events[i-1].get('event_hash') if i else None) for i,e in enumerate(events))
receipts=status.get('receipts',[]); valid=chain and any(r.get('cost_status')=='PROVIDER_REPORTED' and 0 < r.get('actual_usd',0) <= .01 for r in receipts)
report={'status':'PASS_PHASE_A_LOCAL_BYOK' if valid else 'BLOCKED','audit_chain_valid':chain,'provider_reported_receipts':len(receipts),'deployment_authorized':False}
(ROOT/'PHASE_A_GATE_REPORT.json').write_text(json.dumps(report,indent=2),encoding='utf-8'); print(json.dumps(report,indent=2)); sys.exit(0 if valid else 2)

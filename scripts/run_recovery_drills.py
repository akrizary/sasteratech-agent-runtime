from pathlib import Path
import sys,json,datetime
ROOT=Path(__file__).parents[1]; sys.path.insert(0,str(ROOT/'src'))
from sasteratech_runtime.production_drills import ProductionDrills
r={'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'crash_recovery':ProductionDrills.crash_recovery(),'migration_rollback':ProductionDrills.migration_rollback()}
r['passed']=r['crash_recovery']['passed'] and r['migration_rollback']['passed']
out=ROOT/'evidence'/'recovery_drills.json'; out.parent.mkdir(exist_ok=True); out.write_text(json.dumps(r,indent=2),encoding='utf-8'); print(json.dumps(r,indent=2)); raise SystemExit(0 if r['passed'] else 1)

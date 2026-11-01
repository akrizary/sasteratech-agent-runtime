from pathlib import Path
import sqlite3
ROOT=Path(__file__).parents[1]; state=ROOT/'state'
for name,query in [('credentials','SELECT credential_id,provider,masked_suffix,status FROM credential_metadata'),('budget','SELECT state,count(*) FROM budget_reservation GROUP BY state'),('switches','SELECT scope,value FROM kill_switch')]:
    db=state/('local_byok_metadata.db' if name=='credentials' else 'local_byok_budget.db' if name=='budget' else 'local_byok_switches.db')
    con=sqlite3.connect(db)
    try: print(name,con.execute(query).fetchall())
    finally: con.close()

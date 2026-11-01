import sys,pathlib,tempfile,unittest
from datetime import datetime,timezone
sys.path.insert(0,str(pathlib.Path(__file__).parents[1]/'src'))
from sasteratech_runtime.memory import MemoryCandidate,TemporalMemoryStore
from sasteratech_runtime import SQLiteStore
from sasteratech_runtime.memory_repository import TemporalMemoryRepository
from sasteratech_runtime.repository import RunRepository

class TemporalMemoryTests(unittest.TestCase):
    def test_supersession_as_of(self):
        s=TemporalMemoryStore(); old=MemoryCandidate('A','owner=A','FACT',['S'],['E'],valid_from=datetime(2025,1,1,tzinfo=timezone.utc),scope='P'); new=MemoryCandidate('B','owner=B','FACT',['S2'],['E2'],valid_from=datetime(2026,1,1,tzinfo=timezone.utc),supersedes=['A'],scope='P')
        s.add(old); s.add(new)
        self.assertEqual([x.memory_id for x in s.as_of(datetime(2025,6,1,tzinfo=timezone.utc),scope='P')],['A'])
        self.assertEqual([x.memory_id for x in s.as_of(datetime(2026,6,1,tzinfo=timezone.utc),scope='P')],['B'])
        self.assertEqual(s.get('A').valid_to,datetime(2026,1,1,tzinfo=timezone.utc))
        self.assertIn('B',s.get('A').superseded_by)
    def test_invalid_interval_rejected(self):
        with self.assertRaises(ValueError): MemoryCandidate('X','x','FACT',['S'],['E'],valid_from=datetime(2026,2,1,tzinfo=timezone.utc),valid_to=datetime(2026,1,1,tzinfo=timezone.utc))
    def test_sqlite_temporal_roundtrip(self):
        with tempfile.TemporaryDirectory() as td:
            st=SQLiteStore(pathlib.Path(td)/'m.db'); RunRepository(st).create('R','RESEARCH','STATE_0_READ_ONLY_AUDIT'); repo=TemporalMemoryRepository(st)
            a=MemoryCandidate('A','old','FACT',['S'],['E'],valid_from=datetime(2025,1,1,tzinfo=timezone.utc),scope='P'); repo.put(a,'R')
            b=MemoryCandidate('B','new','FACT',['S2'],['E2'],valid_from=datetime(2026,1,1,tzinfo=timezone.utc),supersedes=['A'],scope='P'); repo.put(b,'R')
            self.assertEqual([x.memory_id for x in repo.as_of(datetime(2025,6,1,tzinfo=timezone.utc),scope='P')],['A'])
            self.assertEqual([x.memory_id for x in repo.as_of(datetime(2026,6,1,tzinfo=timezone.utc),scope='P')],['B'])
            st.close()

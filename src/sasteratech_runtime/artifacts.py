import hashlib,json,mimetypes,uuid
from datetime import datetime,timezone
from pathlib import Path

class ArtifactRegistry:
    def __init__(self,store): self.store=store
    @staticmethod
    def digest(path):
        p=Path(path); h=hashlib.sha256()
        with p.open('rb') as f:
            for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
        return h.hexdigest(),p.stat().st_size
    def register(self,path,run_id=None,step_id=None,canonical=False,parents=(),supersedes=None,metadata=None):
        p=Path(path).resolve()
        if not p.is_file(): raise FileNotFoundError(p)
        sha,size=self.digest(p); aid=f'ART-{uuid.uuid4()}'; media,_=mimetypes.guess_type(str(p)); created=datetime.now(timezone.utc).isoformat()
        with self.store.transaction(): self.store.conn.execute('INSERT INTO artifacts(artifact_id,run_id,step_id,path,sha256,size_bytes,media_type,created_at,canonical,parents_json,supersedes,metadata_json) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',(aid,run_id,step_id,str(p),sha,size,media,created,int(canonical),json.dumps(list(parents)),supersedes,json.dumps(metadata or {},sort_keys=True)))
        return aid
    def verify(self,artifact_id):
        r=self.store.conn.execute('SELECT * FROM artifacts WHERE artifact_id=?',(artifact_id,)).fetchone()
        if r is None: raise KeyError(artifact_id)
        p=Path(r['path'])
        if not p.is_file(): return {'ok':False,'reason':'missing'}
        sha,size=self.digest(p)
        if size!=r['size_bytes']: return {'ok':False,'reason':'size_mismatch','expected':r['size_bytes'],'actual':size}
        if sha!=r['sha256']: return {'ok':False,'reason':'hash_mismatch','expected':r['sha256'],'actual':sha}
        return {'ok':True,'reason':'verified','sha256':sha,'size_bytes':size}

from datetime import datetime, timezone
from .models import TruthStatus

class EvidenceLedger:
    def __init__(self):
        self.evidence={}; self.claims={}

    def add_evidence(self,evidence_id,payload):
        if evidence_id in self.evidence: raise ValueError(f"duplicate evidence id: {evidence_id}")
        self.evidence[evidence_id]={"recorded_at":datetime.now(timezone.utc).isoformat(),**payload}

    def add_claim(self,claim):
        missing=[e for e in claim.evidence if e not in self.evidence]
        if missing: raise ValueError(f"unknown evidence refs: {missing}")
        if claim.status==TruthStatus.VERIFIED and not claim.evidence:
            raise ValueError("VERIFIED claim requires evidence")
        self.claims[claim.claim_id]=claim

    def critical_claims_verified(self,claim_ids):
        for cid in claim_ids:
            c=self.claims.get(cid)
            if c is None or c.status!=TruthStatus.VERIFIED or not c.evidence or c.contradictions:
                return False
        return True

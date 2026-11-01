from dataclasses import dataclass
from .roles import Role

class VerificationIndependenceError(ValueError): pass

@dataclass(frozen=True)
class VerificationRequest:
    claim_ids:tuple[str,...]
    producer_worker_id:str
    verifier_worker_id:str
    verifier_role:Role=Role.VERIFIER
    independent_required:bool=True

    def validate(self):
        if self.verifier_role != Role.VERIFIER:
            raise VerificationIndependenceError('verification request must be assigned to VERIFIER role')
        if self.independent_required and self.producer_worker_id == self.verifier_worker_id:
            raise VerificationIndependenceError('producer cannot independently verify own work')
        if not self.claim_ids:
            raise VerificationIndependenceError('at least one claim required')
        return True

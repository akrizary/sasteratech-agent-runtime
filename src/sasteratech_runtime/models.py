from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Tuple
from datetime import datetime

class Risk(str, Enum):
    R0='R0'; R1='R1'; R2='R2'; R3='R3'; R4='R4'

class RunState(str, Enum):
    READ_ONLY_AUDIT='STATE_0_READ_ONLY_AUDIT'
    PLAN_READY='STATE_1_PLAN_READY'
    PATCH_PREPARED='STATE_2_PATCH_PREPARED'
    LOCAL_MUTATION_AUTHORIZED='STATE_3_LOCAL_MUTATION_AUTHORIZED'
    EXTERNAL_MUTATION_AUTHORIZED='STATE_4_EXTERNAL_MUTATION_AUTHORIZED'
    DEPLOY_AUTHORIZED='STATE_5_DEPLOY_AUTHORIZED'
    POST_MUTATION_VERIFY='STATE_6_POST_MUTATION_VERIFY'
    COMPLETE='STATE_7_COMPLETE'
    BLOCKED='STATE_X_BLOCKED'
    RECOVERY='STATE_X_RECOVERY'

class TaskClass(str, Enum):
    FACT_QUERY='FACT_QUERY'; RESEARCH='RESEARCH'; BUILD='BUILD'; DEBUG='DEBUG'
    REVIEW='REVIEW'; DATA='DATA'; FILE='FILE'; MIGRATION='MIGRATION'
    OPERATIONS='OPERATIONS'; CREATIVE='CREATIVE'; HIGH_RISK='HIGH_RISK'

class DomainClass(str, Enum):
    GENERAL='GENERAL'; SOFTWARE='SOFTWARE'; DATA='DATA'; FILESYSTEM='FILESYSTEM'
    CREATIVE='CREATIVE'; DATABASE='DATABASE'; OPERATIONS='OPERATIONS'; SECURITY='SECURITY'

class ProcedureClass(str, Enum):
    EXPLAIN='EXPLAIN'; RESEARCH='RESEARCH'; REVIEW='REVIEW'; BUILD='BUILD'; DEBUG='DEBUG'
    ANALYZE='ANALYZE'; FILE_OPERATION='FILE_OPERATION'; MIGRATE='MIGRATE'
    CREATE='CREATE'; OPERATE='OPERATE'

class ActionClass(str, Enum):
    NONE='NONE'; READ='READ'; LOCAL_MUTATION='LOCAL_MUTATION'; EXTERNAL_MUTATION='EXTERNAL_MUTATION'
    COMMUNICATION='COMMUNICATION'; FINANCIAL='FINANCIAL'; DESTRUCTIVE='DESTRUCTIVE'; DEPLOY='DEPLOY'

class TruthStatus(str, Enum):
    VERIFIED='VERIFIED'; SUPPORTED='SUPPORTED'; PROVISIONAL='PROVISIONAL'
    INTERPRETATION='INTERPRETATION'; UNKNOWN='UNKNOWN'; CONTRADICTED='CONTRADICTED'

@dataclass(frozen=True)
class ApprovalGrant:
    approval_id:str
    risk_ceiling:Risk
    actions:Tuple[str,...]
    resource_scope:Tuple[str,...]
    issued_by:str='human'
    expires_at:Optional[datetime]=None
    nonce:Optional[str]=None
    run_id:Optional[str]=None
    action_id:Optional[str]=None

@dataclass(frozen=True)
class ToolDefinition:
    id:str
    version:str
    risk:Risk
    side_effect:bool
    requires_approval:bool
    idempotent:bool=True
    reversible:bool=True
    network:bool=False
    secrets:bool=False
    dry_run:bool=False
    evidence_emitted:Tuple[str,...]=()

@dataclass
class ClaimRecord:
    claim_id:str
    claim:str
    status:TruthStatus
    evidence:list[str]=field(default_factory=list)
    contradictions:list[str]=field(default_factory=list)
    observed_at:Optional[datetime]=None

@dataclass(frozen=True)
class RouteDecision:
    task:TaskClass
    reasoning_policy:str
    risk_floor:Risk
    reasons:Tuple[str,...]
    domain:DomainClass=DomainClass.GENERAL
    procedure:ProcedureClass=ProcedureClass.EXPLAIN
    action:ActionClass=ActionClass.NONE
    mutating:bool=False

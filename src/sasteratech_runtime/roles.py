from dataclasses import dataclass, field
from enum import Enum
from fnmatch import fnmatchcase
from .models import Risk, TaskClass

RISK_RANK={Risk.R0:0,Risk.R1:1,Risk.R2:2,Risk.R3:3,Risk.R4:4}

class Role(str, Enum):
    ORCHESTRATOR='ORCHESTRATOR'
    RESEARCHER='RESEARCHER'
    BUILDER='BUILDER'
    DEBUGGER='DEBUGGER'
    REVIEWER='REVIEWER'
    VERIFIER='VERIFIER'
    RISK_GUARDIAN='RISK_GUARDIAN'
    MEMORY_CURATOR='MEMORY_CURATOR'
    SYNTHESIZER='SYNTHESIZER'
    DOMAIN_SPECIALIST='DOMAIN_SPECIALIST'

@dataclass(frozen=True)
class RoleProfile:
    role: Role
    allowed_tasks: tuple[TaskClass,...]
    risk_ceiling: Risk
    allow_tools: tuple[str,...]
    deny_tools: tuple[str,...]=()
    may_delegate_to: tuple[Role,...]=()
    independent_review: bool=False

    def tool_allowed(self, tool_id:str) -> bool:
        if any(fnmatchcase(tool_id,p) for p in self.deny_tools):
            return False
        return any(fnmatchcase(tool_id,p) for p in self.allow_tools)

    def accepts(self, task:TaskClass) -> bool:
        return task in self.allowed_tasks

class RoleRegistry:
    def __init__(self, profiles=None):
        self._profiles={p.role:p for p in (profiles or default_profiles())}
    def get(self, role):
        if not isinstance(role,Role): role=Role(role)
        return self._profiles[role]
    def all(self): return tuple(self._profiles.values())

def default_profiles():
    return (
      RoleProfile(Role.ORCHESTRATOR,
                  (TaskClass.FACT_QUERY,TaskClass.RESEARCH,TaskClass.BUILD,TaskClass.DEBUG,
                   TaskClass.REVIEW,TaskClass.DATA,TaskClass.FILE,TaskClass.MIGRATION,
                   TaskClass.OPERATIONS,TaskClass.CREATIVE,TaskClass.HIGH_RISK),
                  Risk.R4,
                  ('policy.read','evidence.read','memory.read','plan.read','plan.write'),
                  ('file.write','shell.*','deploy.*','email.send','payment.*'),
                  (Role.RESEARCHER,Role.BUILDER,Role.DEBUGGER,Role.REVIEWER,Role.VERIFIER,
                   Role.RISK_GUARDIAN,Role.MEMORY_CURATOR,Role.SYNTHESIZER,Role.DOMAIN_SPECIALIST)),
      RoleProfile(Role.RESEARCHER,(TaskClass.FACT_QUERY,TaskClass.RESEARCH),Risk.R0,
                  ('web.read','file.read','evidence.read'),('file.write','git.*','deploy.*','email.send'),
                  (Role.DOMAIN_SPECIALIST,Role.SYNTHESIZER)),
      RoleProfile(Role.BUILDER,(TaskClass.BUILD,),Risk.R2,
                  ('file.read','file.write','shell.test','artifact.write'),('deploy.*','email.send','payment.*'),
                  (Role.DEBUGGER,Role.REVIEWER,Role.VERIFIER),True),
      RoleProfile(Role.DEBUGGER,(TaskClass.DEBUG,),Risk.R2,
                  ('file.read','file.write','shell.test','evidence.read'),('deploy.*','email.send','payment.*'),
                  (Role.RESEARCHER,Role.REVIEWER,Role.VERIFIER),True),
      RoleProfile(Role.REVIEWER,(TaskClass.REVIEW,),Risk.R0,
                  ('file.read','shell.test','evidence.read'),('file.write','deploy.*','email.send'),
                  (Role.RESEARCHER,Role.DOMAIN_SPECIALIST)),
      RoleProfile(Role.VERIFIER,(TaskClass.REVIEW,),Risk.R1,
                  ('file.read','shell.test','remote.readback','evidence.read'),('file.write','deploy.*','email.send'),
                  (Role.DOMAIN_SPECIALIST,)),
      RoleProfile(Role.RISK_GUARDIAN,(TaskClass.HIGH_RISK,TaskClass.REVIEW),Risk.R0,
                  ('policy.read','evidence.read','file.read'),('file.write','deploy.*','email.send','payment.*'),()),
      RoleProfile(Role.MEMORY_CURATOR,(TaskClass.REVIEW,TaskClass.DATA),Risk.R1,
                  ('memory.read','memory.candidate.write','evidence.read'),('memory.canonical.write','deploy.*','email.send'),
                  (Role.RESEARCHER,)),
      RoleProfile(Role.SYNTHESIZER,(TaskClass.RESEARCH,TaskClass.REVIEW),Risk.R0,
                  ('evidence.read','file.read'),('file.write','deploy.*','email.send'),()),
      RoleProfile(Role.DOMAIN_SPECIALIST,(TaskClass.FACT_QUERY,TaskClass.RESEARCH,TaskClass.REVIEW),Risk.R0,
                  ('evidence.read','file.read'),('file.write','deploy.*','email.send'),()),
    )

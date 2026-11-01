from .models import TaskClass
from .roles import Role

PRIMARY_ROLE={
    TaskClass.FACT_QUERY:Role.RESEARCHER,
    TaskClass.RESEARCH:Role.RESEARCHER,
    TaskClass.BUILD:Role.BUILDER,
    TaskClass.DEBUG:Role.DEBUGGER,
    TaskClass.REVIEW:Role.REVIEWER,
    TaskClass.DATA:Role.MEMORY_CURATOR,
    TaskClass.HIGH_RISK:Role.RISK_GUARDIAN,
    TaskClass.CREATIVE:Role.DOMAIN_SPECIALIST,
}

class OrganRouter:
    def primary(self, task_class):
        return PRIMARY_ROLE.get(task_class, Role.DOMAIN_SPECIALIST)
    def post_roles(self, task_class):
        if task_class in {TaskClass.BUILD,TaskClass.DEBUG}:
            return (Role.REVIEWER,Role.VERIFIER)
        if task_class == TaskClass.RESEARCH:
            return (Role.SYNTHESIZER,)
        if task_class == TaskClass.HIGH_RISK:
            return (Role.VERIFIER,)
        return ()

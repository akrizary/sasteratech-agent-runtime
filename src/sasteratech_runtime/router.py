import re
from .models import (
    RouteDecision,TaskClass,Risk,DomainClass,ProcedureClass,ActionClass
)

POLICIES={
TaskClass.FACT_QUERY:'retrieve→verify→answer',
TaskClass.RESEARCH:'decompose→source→triangulate→contradiction-scan→synthesize',
TaskClass.BUILD:'spec→plan→implement→test→verify',
TaskClass.DEBUG:'reproduce→isolate→hypothesize→discriminate→patch→regression',
TaskClass.REVIEW:'criteria→inspect→adversarial-check→evidence→verdict',
TaskClass.DATA:'inspect→profile→transform→invariants→reconcile',
TaskClass.FILE:'inventory→plan→preview→approve→mutate→integrity-check',
TaskClass.MIGRATION:'inventory→map→dry-run→backup→approve→migrate→reconcile',
TaskClass.OPERATIONS:'observe→desired-state→delta→risk-gate→execute→verify',
TaskClass.CREATIVE:'canon-retrieve→constraints→generate→continuity-pass',
TaskClass.HIGH_RISK:'deterministic-policy→restricted-tools→explicit-approval→verify',
}

CREATIVE=('novel','story','chapter','fiction','worldbuilding','canon','character','plot')
DATA=('csv','dataset','dataframe','spreadsheet','data analysis')
DATABASE=('database','schema','records','sql')
FILES=('file','folder','directory','zip','archive')
SOFTWARE=('code','parser','module','test','bug','refactor','api','software')

NO_MUTATION_PATTERNS=(
    r'\bdo not\s+(?:change|modify|patch|delete|deploy|send|publish|pay|transfer|access)\b',
    r'\bwithout\s+(?:changing|modifying|patching|deleting|deploying|sending|publishing|paying|transferring|accessing)\b',
    r'\bwithout deleting anything\b', r'\bresearch only\b', r'\bconceptually\b'
)
EXPLAIN_PATTERNS=(r'^what (?:is|does|are)\b',r'^explain\b',r'\bwhat .* mean\b',r'\bconceptually\b')


def _norm(text): return ' '.join(text.lower().split())
def _contains(t,words): return any(w in t for w in words)
def _matches(t,patterns): return any(re.search(p,t) for p in patterns)

def classify_domain(t):
    if _contains(t,CREATIVE): return DomainClass.CREATIVE
    if _contains(t,DATA) or (re.search(r'\bdata\b',t) and re.search(r'\b(analyze|analyse|clean|profile|transform|chart|visuali[sz]e)\b',t)): return DomainClass.DATA
    if _contains(t,DATABASE): return DomainClass.DATABASE
    if _contains(t,FILES): return DomainClass.FILESYSTEM
    if _contains(t,SOFTWARE): return DomainClass.SOFTWARE
    if any(x in t for x in ('secret','credential','security','permission','access control')): return DomainClass.SECURITY
    if any(x in t for x in ('production','deploy','service','server','infrastructure')): return DomainClass.OPERATIONS
    return DomainClass.GENERAL

def classify_procedure(t,domain,no_mutation):
    # Explicit epistemic/review intent outranks incidental problem words.
    if re.search(r'\b(research|investigate|compare|survey)\b',t): return ProcedureClass.RESEARCH
    if re.search(r'\b(audit|review|stress-test|stress test|validate|assess)\b',t): return ProcedureClass.REVIEW
    if domain==DomainClass.CREATIVE and re.search(r'\b(write|develop|create|draft)\b',t): return ProcedureClass.CREATE
    if re.search(r'\b(migrate|migration)\b',t) or 'move database records' in t: return ProcedureClass.MIGRATE
    if domain==DomainClass.DATA and re.search(r'\b(analyze|analyse|clean|profile|transform)\b',t): return ProcedureClass.ANALYZE
    if no_mutation and re.search(r'\b(fail|fails|failing|bug|crash|error|not working)\b',t):
        return ProcedureClass.RESEARCH
    if re.search(r'\b(debug|failing test|bug|crash|not working|root cause)\b',t): return ProcedureClass.DEBUG
    if re.search(r'\b(implement|build|develop|patch|create app|create module|code)\b',t): return ProcedureClass.BUILD
    if domain==DomainClass.FILESYSTEM and re.search(r'\b(rename|organize|organise|move|copy|zip|archive)\b',t): return ProcedureClass.FILE_OPERATION
    if _matches(t,EXPLAIN_PATTERNS): return ProcedureClass.EXPLAIN
    return ProcedureClass.EXPLAIN

def classify_action(t,no_mutation):
    if no_mutation: return ActionClass.NONE,Risk.R0,('explicit non-mutation qualifier',)

    # Actual action intent needs an action construction, not merely a risky noun mention.
    if re.search(r'\bdeploy\b.*\bproduction\b|\bdeploy this\b|\bdeploy now\b',t):
        return ActionClass.DEPLOY,Risk.R4,('explicit production deployment intent',)
    if re.search(r'\b(delete|erase|drop|destroy)\b.*\b(production|database|records|files?)\b',t):
        return ActionClass.DESTRUCTIVE,Risk.R4,('explicit destructive action intent',)
    if re.search(r'\btransfer\b.*\b(money|funds?)\b|\bpay\b.*\b(supplier|vendor|invoice|bill)\b',t):
        return ActionClass.FINANCIAL,Risk.R4,('explicit financial action intent',)
    if re.search(r'\bsend\b.*\b(email|message|mail)\b|\bemail\b.*\b(client|customer|vendor)\b.*\bnow\b',t):
        return ActionClass.COMMUNICATION,Risk.R3,('explicit external communication intent',)
    if re.search(r'\bpublish\b\s+(this|the|my|our)\b|\bpush\b.*\b(remote|github|origin|production)\b',t):
        return ActionClass.EXTERNAL_MUTATION,Risk.R3,('explicit external mutation intent',)
    if re.search(r'\b(rename|move|copy|write|edit|modify|patch|implement|build|develop|organize|organise|zip|archive)\b|\bcreate (?:app|module|file)\b',t):
        return ActionClass.LOCAL_MUTATION,Risk.R2,('local mutation intent',)
    return ActionClass.NONE,Risk.R0,()

def derive_task(domain,procedure,action):
    if action in {ActionClass.DEPLOY,ActionClass.DESTRUCTIVE,ActionClass.FINANCIAL,ActionClass.COMMUNICATION,ActionClass.EXTERNAL_MUTATION}:
        return TaskClass.HIGH_RISK
    if domain==DomainClass.CREATIVE:
        return TaskClass.CREATIVE
    if procedure==ProcedureClass.RESEARCH: return TaskClass.RESEARCH
    if procedure==ProcedureClass.REVIEW: return TaskClass.REVIEW
    if procedure==ProcedureClass.DEBUG: return TaskClass.DEBUG
    if procedure==ProcedureClass.MIGRATE: return TaskClass.MIGRATION
    if procedure==ProcedureClass.ANALYZE: return TaskClass.DATA
    if procedure==ProcedureClass.FILE_OPERATION: return TaskClass.FILE
    if procedure==ProcedureClass.BUILD: return TaskClass.BUILD
    return TaskClass.FACT_QUERY

def route_task(text):
    t=_norm(text)
    no_mutation=_matches(t,NO_MUTATION_PATTERNS)
    domain=classify_domain(t)
    procedure=classify_procedure(t,domain,no_mutation)
    action,risk,action_reasons=classify_action(t,no_mutation)
    task=derive_task(domain,procedure,action)
    reasons=(f'domain={domain.value}',f'procedure={procedure.value}',f'action={action.value}',*action_reasons)
    return RouteDecision(task,POLICIES[task],risk,reasons,domain,procedure,action,action!=ActionClass.NONE)

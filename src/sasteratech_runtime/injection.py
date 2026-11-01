import re
from .security_models import InjectionFinding, InjectionSeverity

_PATTERNS=(
    (re.compile(r'ignore\s+(all\s+)?(previous|prior|above)\s+instructions?',re.I),'override_instructions',3),
    (re.compile(r'(system|developer)\s+(prompt|message|instructions?)',re.I),'system_prompt_reference',1),
    (re.compile(r'(reveal|show|print|exfiltrate|send)\s+.*(api[_ -]?key|token|password|secret|credential)',re.I),'secret_exfiltration',4),
    (re.compile(r'(call|invoke|run|execute)\s+.*(tool|shell|command|function)',re.I),'tool_instruction',2),
    (re.compile(r'you\s+(must|are required to)\s+(obey|follow|execute)',re.I),'embedded_authority',2),
    (re.compile(r'<\s*(system|developer|assistant)\b',re.I),'role_tag',2),
)

class PromptInjectionDefender:
    def inspect(self, text:str, trust='UNTRUSTED_EXTERNAL'):
        if trust.startswith('TRUSTED_'):
            return InjectionFinding(InjectionSeverity.NONE,(),False)
        hits=[]; score=0
        for rx,name,w in _PATTERNS:
            if rx.search(text or ''):
                hits.append(name); score+=w
        if score >= 4: sev=InjectionSeverity.HIGH
        elif score >= 2: sev=InjectionSeverity.MEDIUM
        elif score >= 1: sev=InjectionSeverity.LOW
        else: sev=InjectionSeverity.NONE
        return InjectionFinding(sev,tuple(hits),sev==InjectionSeverity.HIGH)

    def wrap_for_context(self, text, finding, source_id='tool'):
        if finding.withhold:
            return f'[SasteraTech-UNTRUSTED-WITHHELD source={source_id} severity={finding.severity.value}]'
        return (
            f'[SasteraTech-UNTRUSTED-DATA source={source_id} severity={finding.severity.value}]\n'
            f'{text}\n[/SasteraTech-UNTRUSTED-DATA]'
        )

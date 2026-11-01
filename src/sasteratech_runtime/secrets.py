import re
from copy import deepcopy

_KEY_FRAGMENTS=('api_key','apikey','authorization','bearer','password','passwd','secret','access_token','refresh_token','private_key')
_VALUE_PATTERNS=(
    re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    re.compile(r'(?i)bearer\s+[A-Za-z0-9._~+/=-]{12,}'),
    re.compile(r'(?i)\bsk-[A-Za-z0-9._-]{8,}\b'),
    re.compile(r'(?i)(?:api[_-]?key|token|password|secret)\s*[:=]\s*["\']?[A-Za-z0-9._~+/=-]{8,}'),
)

class SecretBoundary:
    def contains_secret(self, value):
        if isinstance(value,dict):
            for k,v in value.items():
                if any(f in str(k).lower() for f in _KEY_FRAGMENTS) and v not in (None,'','[REDACTED]'):
                    return True
                if self.contains_secret(v): return True
            return False
        if isinstance(value,(list,tuple,set)):
            return any(self.contains_secret(x) for x in value)
        if isinstance(value,str):
            return any(rx.search(value) for rx in _VALUE_PATTERNS)
        return False

    def redact(self, value):
        if isinstance(value,dict):
            out={}
            for k,v in value.items():
                if any(f in str(k).lower() for f in _KEY_FRAGMENTS): out[k]='[REDACTED]'
                else: out[k]=self.redact(v)
            return out
        if isinstance(value,list): return [self.redact(x) for x in value]
        if isinstance(value,tuple): return tuple(self.redact(x) for x in value)
        if isinstance(value,str):
            s=value
            for rx in _VALUE_PATTERNS: s=rx.sub('[REDACTED]',s)
            return s
        return value

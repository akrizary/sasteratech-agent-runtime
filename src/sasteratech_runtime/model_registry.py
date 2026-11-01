import os, json
from pathlib import Path
from .roles import Role
from .runtime_models import ModelProfile

class ModelRegistry:
    def __init__(self, profiles=(), role_defaults=None, env=None):
        self._profiles={}; self._role_defaults={}; self.env=os.environ if env is None else env
        for p in profiles: self.register(p)
        for role,alias in (role_defaults or {}).items(): self.set_default(role,alias)
    def register(self,profile):
        if profile.alias in self._profiles: raise ValueError(f'duplicate model alias: {profile.alias}')
        self._profiles[profile.alias]=profile
    def set_default(self,role,alias):
        role=role if isinstance(role,Role) else Role(role); self._role_defaults[role]=alias
    def get(self,alias): return self._profiles[alias]
    def default_for(self,role):
        role=role if isinstance(role,Role) else Role(role)
        if role not in self._role_defaults: raise KeyError(f'no default model alias for role {role.value}')
        return self._role_defaults[role]
    def resolve(self,alias,role):
        role=role if isinstance(role,Role) else Role(role); p=self.get(alias)
        if not p.enabled: raise ValueError(f'model profile disabled: {alias}')
        if p.allowed_roles and role not in p.allowed_roles: raise PermissionError(f'model profile {alias} not permitted for role {role.value}')
        model_id=(self.env.get(p.model_env) if p.model_env else None) or p.model_id
        if not model_id: raise ValueError(f'model id unresolved for {alias}; set {p.model_env or "model_id"}')
        return ModelProfile(p.alias,p.adapter_id,model_id,p.model_env,p.allowed_roles,p.enabled,dict(p.metadata))
    @classmethod
    def from_file(cls,path,env=None):
        data=json.loads(Path(path).read_text(encoding='utf-8'))
        profiles=[ModelProfile(x['alias'],x['adapter_id'],x.get('model_id'),x.get('model_env'),tuple(Role(r) for r in x.get('allowed_roles',[])),x.get('enabled',True),x.get('metadata',{})) for x in data.get('profiles',[])]
        return cls(profiles,data.get('role_defaults',{}),env=env)

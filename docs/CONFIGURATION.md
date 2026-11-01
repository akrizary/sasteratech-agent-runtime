# Configuration

Default config: `config/default.json`.

Environment overrides use `SASTERATECH__SECTION__KEY=value`, e.g. `SASTERATECH__limits__context_token_budget=12000`. Values are parsed as JSON where possible. Secrets should be referenced by provider/secret identifiers rather than written into configuration files.

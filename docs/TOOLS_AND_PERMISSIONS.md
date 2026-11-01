# Tool Registry and Permissions

Each tool declares:
- id/version
- input/output schema
- risk
- side effects
- idempotency
- reversibility
- network/secrets
- dry-run
- approval rule
- timeout/retries
- evidence emitted

## Least privilege

```text
Researcher: web.read, file.read
Builder: file.read, file.write(R2), shell.test
Verifier: file.read, shell.test, remote.readback
Deployer: deploy.execute(R4)
```

## Invocation checks
Before:
1. schema
2. policy
3. resource scope
4. approval
5. optional semantic risk judge
6. idempotency/replay check

After:
1. store raw result
2. sanitize secrets
3. register evidence
4. verify expected effect
5. checkpoint

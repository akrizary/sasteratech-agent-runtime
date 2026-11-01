# Local Windows BYOK smoke runbook

## Scope

One DeepSeek Flash `READ_ONLY` smoke call, max USD 0.01 and 512 total tokens, no tools or external writes.

## Preconditions

- Run from the v1.1 package directory.
- Use the intended project virtual environment.
- Do not set `DEEPSEEK_API_KEY` in PowerShell, `.env`, or a project file.

## Commands

```powershell
.\.venv\Scripts\python.exe -m pip install "keyring>=25.7,<26"
.\.venv\Scripts\python.exe scripts\enroll_local_byok.py
```

The enrollment command displays a hidden prompt. Enter the raw DeepSeek key only at that prompt. It prints a `credential_id` and masked suffix, never the raw key.

Then run exactly one smoke call using the printed credential ID:

```powershell
.\.venv\Scripts\python.exe scripts\smoke_local_byok.py --credential-id cred_REPLACE_WITH_PRINTED_ID --max-cost-usd 0.01
```

## Expected PASS result

```text
PASS: local BYOK smoke complete; cost_usd=...; raw key was not printed.
```

## Stop conditions

- Do not retry if the command reports a budget, provider, credential, or cost-evidence failure.
- Do not paste a raw key into the terminal transcript, chat, source code, or an environment variable.
- If the key was exposed anywhere other than the hidden prompt, revoke it in the provider console and create a replacement before continuing.

## Replace a rejected or rotated key

Delete the old local credential handle, then enrol the replacement at the hidden prompt:

```powershell
.\.venv\Scripts\python.exe scripts\remove_local_byok.py --credential-id cred_REPLACE_OLD_ID
.\.venv\Scripts\python.exe scripts\enroll_local_byok.py
```

## Evidence location

Only redacted metadata is written under `state/`:

- `local_byok_metadata.db` — credential handle and masked suffix; no raw provider key;
- `local_byok_budget.db` — reservation/receipt metadata;
- `local_byok_switches.db` — kill-switch state;
- `local_byok_audit.jsonl` — redacted audit chain.

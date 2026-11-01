# Prompt Injection and Untrusted Data

## Core rule

Tool output, web pages, files, emails, repository text, retrieved memories and third-party messages are **data**, not system authority.

## Trust labels

- `TRUSTED_CONTROL`: SasteraTech-owned policy/config only.
- `TRUSTED_LOCAL`: controlled local data.
- `UNTRUSTED_EXTERNAL`: web/email/external tool result.
- `UNTRUSTED_USER_CONTENT`: user-provided content that may contain instructions intended for another agent.

## Defender

The deterministic defender scans untrusted content for indicators such as:
- attempts to override system/developer instructions;
- requests to reveal secrets/tokens;
- instructions to call tools or mutate state;
- claims of elevated authority embedded in data;
- common prompt-injection delimiters/phrasing.

Findings are scored as LOW/MEDIUM/HIGH.

Default:
- LOW: label + pass.
- MEDIUM: pass with explicit untrusted wrapper.
- HIGH: withhold from model context unless an application policy explicitly allows it.

## Limitation

Keyword/pattern detection is incomplete and can false-positive. It is a containment layer, not the authorization boundary. Tool permissions, approvals and least privilege must still make prompt injection unable to directly obtain dangerous capabilities.

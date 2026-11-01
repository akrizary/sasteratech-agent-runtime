# Approval Service v0.5

Approval is a durable object, not conversational sentiment.

## ApprovalRequest

Contains:
- request ID
- run/action/tool
- requested risk
- exact resource
- requested actions
- reason
- creation/expiry
- status

## ApprovalGrant

High-risk grants are issued only by a human identity through `ApprovalService.grant_human()`.

The service checks:
- request exists and is pending;
- requested scope is not widened;
- granted risk ceiling is not below the action risk;
- grant has an expiry;
- request cannot be reused after grant/deny.

## Policy-issued authority

SasteraTech permits policy-issued authorization only up to R1. R2-R4 require `issued_by='human'`.

## Negative controls

- LLM/self-issued grant: invalid.
- stale grant: invalid.
- wrong tool: invalid.
- wrong path/resource: invalid.
- risk ceiling too low: invalid.
- design approval reused for deploy: invalid.

## Final binding rule

R2-R4 grants are bound to the originating **run ID and action ID** in addition to tool, resource and expiry. Unbound manually constructed high-risk grants are rejected.

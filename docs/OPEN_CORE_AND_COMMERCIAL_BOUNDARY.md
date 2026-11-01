# Open-Core and First-Party Commercial Boundary

**Status:** PUBLIC-CANDIDATE PRODUCT BOUNDARY  
**Current deployment:** NONE  
**Current hosted service:** NONE

## Purpose

SasteraTech Agent Runtime is intended to support broad local and self-hosted adoption
without accidentally publishing every future first-party commercial component.
This document separates the planned Apache-2.0 open core from the project's
first-party hosted and enterprise roadmap.

## Planned open-source core

The clean public candidate includes:

- local runtime and deterministic policy contracts;
- local BYOK credential enrollment and dispatch boundary;
- provider adapters, beginning with DeepSeek;
- loopback-only local API and client SDK contracts;
- read-only, draft, and shadow-mode workflows;
- user-configured budget caps, audit records, and kill-switch behaviour;
- offline tests, evaluation fixtures, schemas, and safe self-hosting basics; and
- documentation needed to run, inspect, modify, and redistribute the core.

The exact publishable manifest remains subject to the secret, dependency,
provenance, test, and clean-export gates.

## First-party commercial roadmap

The following are planned first-party products or services and are not promised
as part of the initial public core:

- a managed SasteraTech Runtime cloud service;
- multi-tenant identity and organisation administration;
- enterprise SSO, SCIM, advanced RBAC, and policy administration;
- managed secret vaults and provider-account operations;
- extended audit retention, compliance exports, and organisation dashboards;
- premium or managed connectors;
- signed/certified release channels, managed upgrades, SLA, and paid support;
- implementation, migration, integration, and training services.

Code for these first-party commercial components must live outside the clean
public export unless the project owner explicitly changes that boundary.

## What this boundary does not mean

Apache-2.0 is permissive. Once the core is released under Apache-2.0, recipients
may use it commercially and may independently build competing features or
services, subject to that licence and applicable trademark law.

This document therefore does not claim exclusive ownership of generic feature
categories. The project's commercial advantage is expected to come from the
official brand, trusted releases, operational quality, integrations, support,
and first-party hosted implementation—not from misrepresenting Apache-2.0 as a
non-commercial licence.

## Cost model

- Self-hosted users supply and pay for their own provider credentials (BYOK).
- The project owner does not subsidise public inference by default.
- Public-repository hosting and standard public CI should use free tiers where
  practical.
- No paid cloud, domain, trademark filing, or external service is authorised by
  this document.
- A future hosted service requires a separate budget, deployment plan, and
  explicit approval.

## Publication gate

Before public release, verify that:

1. the clean public manifest contains only approved open-core files;
2. no commercial/private module, local state, credential metadata, or user
   evidence is included;
3. the source-code licence and ownership statements are complete;
4. `TRADEMARKS.md` is included and the official owner/contact is identified;
5. all third-party notices and dependency licences are accounted for; and
6. the release is built and validated from the clean export.

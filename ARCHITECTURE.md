# Architecture and delivery plan

## Scope

Build a local-first web interface for uploads and model-backed chat, with an optional local retrieval helper. This is an application integration, not artificial general intelligence or autonomous self-training. IBM Bob is a coding/development agent that can assist with implementing and reviewing software; it is not automatically a runtime connector to Confluence, CRM, or arbitrary websites.

## Components and request flow

```text
Browser -> Flask application -> selected chat provider (WiCi or Gemini)
                       |-> validated upload -> private storage
                       |-> JCodePy local retrieval / KALKUL8 calculator
                       `-> (future) queued, allowlisted enterprise import worker
                               -> Confluence / specified CRM / approved CMS API
```

Provider secrets remain server-side. The current Flask upload/chat prototype is single-user and local-only; it is not yet a production enterprise content transfer service. See [`integrations/README.md`](integrations/README.md) for a secure connector plan and required information before implementing live integrations.

## Phase 1 — local prototype

- Run Flask on a trusted development host; WiCi must be reachable over that host's LAN.
- Pair WiCi through its official SDK and inject the device token through the process environment.
- For Gemini, configure a currently valid model identifier and API key through environment variables; check the provider's current documentation and data handling.
- Run Python checks/tests directly or through `npm run build` and `npm test` (Gulp invokes Python compile/test tasks).

## Phase 2 — production web app

1. Add authentication, per-user ownership, CSRF protections as applicable, rate limits, quotas, and authorization.
2. Put files in private object storage, not container filesystems; add malware scanning, retention/deletion, and backups.
3. Use a production WSGI server behind TLS, managed secrets, dependency scans, and redacted observability.
4. Cloud Run does not automatically connect to Wi-Fi-only WiCi. Design and review an explicit private network path or choose an approved cloud inference endpoint.
5. Before enterprise ingestion, select a queue/worker and object store, approved source and destination APIs, OAuth scopes, data retention/classification, size limits, and human approval rules. Enforce host allowlists, permission trimming, idempotency, and auditable actions.
6. Treat `www.turingnewsnetwork.com` as a proposed destination until domain ownership/authorization and its publishing API are verified. No automatic scraping or publishing is configured.

## Phase 3 — firmware and robotics

Firmware work is separate from the web app. Verify exact board, firmware provenance/checksum, serial port, bootloader/tool versions, stable power, backup, and recovery before flashing. Never expose flashing as a web endpoint.

## Model and workflow governance

A model can draft summaries or workflow steps, but must not be the authority for access control, CRM mutations, or public publishing. Validate outputs, show a preview with provenance, and require human approval for consequential writes. Do not claim a conversational persona or retrieval helper is AGI.

## Destructive cloud operations

Deleting a Cloud Run job or Google Cloud project is not app setup. Verify active project, dependencies, backups, and owner approval before any deletion. Never put deletion commands in the Gulp build pipeline.

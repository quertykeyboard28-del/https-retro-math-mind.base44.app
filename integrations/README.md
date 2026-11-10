# IBM Bob, Confluence, CRM, and content workflow integration plan

This document is an implementation blueprint for integrating the existing Flask application with approved enterprise content systems. It does **not** make live requests to IBM Bob, Confluence, a CRM, or `www.turingnewsnetwork.com`; endpoint URLs, tenant details, OAuth applications, data permissions, and ownership have not been supplied. IBM Bob is a coding/development agent, not itself a generic production content-ingestion API. Use it to help build and review integrations; use the actual platform APIs or an authorized integration product at runtime.

## Proposed flow

```text
Confluence / CRM / authorized site
            |
     approved connector
     (OAuth / scoped token)
            |
  queued, bounded import job
            |
 validation -> private object storage -> metadata/index
            |
  reviewed, versioned web workflow
            |
 Flask UI / approved destination site
```

Keep source-specific adapters separate. Start with read-only access and a dry-run that reports item counts, byte totals, rejected content, and destination mapping. Add publishing or CRM writes only after a human approves a preview and the target system's permissions are confirmed.

## Connector requirements

- **Confluence:** identify Cloud versus Data Center, tenant base URL, spaces/pages to include, OAuth method, scopes, pagination behavior, attachments policy, and whether permission trimming must be preserved. Inherit Atlassian's authorization and rate-limit requirements. Never crawl a tenant from a public or user-supplied arbitrary URL.
- **CRM:** name the product and objects (for example, approved article/case fields), OAuth flow, read/write scopes, field mapping, retention, and consent rules. Do not copy contact, customer, or case data into public search or prompts by default.
- **Website example:** treat `https://www.turingnewsnetwork.com` as a proposed destination only. Confirm that you own or are authorized to publish there, and obtain its supported CMS/API, staging endpoint, authentication method, and editorial approval workflow before enabling publishing. Do not scrape it or send content to it automatically.
- **Cloud content:** use private object storage and a queue for larger transfers. Stream with bounded chunk sizes; set per-file and total-job byte limits; validate MIME/signatures; scan files; calculate checksums; support resumable/retryable jobs; and enforce retention/deletion. Do not put large file bodies in a database row, chat prompt, or container image.
- **Containers:** keep application/container images immutable and small. Store imported documents in private object storage, not the container filesystem (which may be ephemeral). Keep import work in a separate worker with CPU/memory/time limits and least-privilege service identity.

## Safe AI-assisted workflow pattern

1. An authenticated user chooses an approved source, bounded scope, and destination from server-side allowlists.
2. The worker fetches only authorized records and records source IDs, timestamps, hashes, byte size, and access metadata—not secrets.
3. Content is normalized, scanned, permission-filtered, and stored privately. Apply explicit per-file and per-job limits.
4. If an AI model is used, send only user-approved fields after redaction and consent. The model may suggest a summary or draft; it must not decide authorization or publish by itself.
5. Validate generated output against a schema and policy, show source citations and a preview, and require a human to approve CRM writes, public publishing, or destructive actions.
6. Log who approved which action, destination, source IDs, and result. Do not log credentials or full sensitive text. Provide rollback/deletion procedures.

### Guardrails

- Use a server-side allowlist of exact source/destination hosts; reject localhost, private-network IPs, redirects to other hosts, and arbitrary URL fetches to reduce SSRF risk.
- Store OAuth client secrets and tokens in a managed secret store. Use per-environment credentials with minimum scopes, rotation, and revocation.
- Enforce authentication, authorization, CSRF protections for browser sessions, request limits, quotas, and audit records. The current prototype does not yet have these protections and must not be exposed as a multi-user production importer.
- Treat imported documents as untrusted input. Never execute embedded scripts, macros, archives, or commands. Escape output when rendering HTML.
- Do not let an agent run shell commands, install packages, deploy, publish content, or modify CRM records without explicit review. Never execute `gcloud projects delete` as a build or deployment step.

## Gulp build command

The Gulp setup in the repository runs Python syntax compilation and tests; it does not deploy or transfer data:

```sh
npm install
npm run build       # gulp build: Python syntax compilation
npm test            # gulp test: compilation followed by pytest
```

Python dependencies are installed separately with `python -m pip install -r requirements.txt`. Set `PYTHON` to the desired Python executable if it is not on PATH. The Gulp tasks intentionally do not run cloud, CRM, Confluence, or publishing commands.

## Details needed before implementing live connectors

Provide the Confluence product/tenant and approved spaces, CRM vendor and objects, desired import direction, authentication method, data classifications and size limits, queue/object-storage provider, destination CMS API for the website, and the human approval/rollback requirements. Do not paste credentials; configure them later in a secret manager.

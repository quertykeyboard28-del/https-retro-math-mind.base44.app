# Architecture and delivery plan

## Scope

Build a local-first web interface for text/image uploads and model-backed chat, with an optional local retrieval helper. This is an application integration, not artificial general intelligence, human-level robotics, or autonomous self-training. The adult persona/demographic request can be implemented as an optional, transparent style setting later; it should not be represented as a real person or used to infer protected traits about users.

## Components and request flow

```text
Browser
  | HTTPS in production / localhost in development
  v
Flask web application
  |-- /api/upload --> validate --> private local uploads (prototype)
  |-- /api/chat ----> one selected provider: WiCi One OR Gemini API
  |-- /health ------> liveness endpoint
  `-- JCodePy helper --> local FAQ retrieval and arithmetic only
```

Provider secrets remain server-side. The browser sends the chosen provider and user message; the server forwards the message to exactly one configured provider. Uploaded files are not included in prompts. Add explicit user consent and a threat/privacy review before introducing document-to-model features.

## Phase 1 — local prototype

- Run Flask on a trusted development host; WiCi must be reachable over that host's LAN.
- Pair WiCi through its official SDK and inject the device token through the process environment.
- For Gemini, configure the API key and a currently valid model identifier using environment variables. Check Google's official current model catalog, quotas, terms, and data handling before use. Do not rely on an unverified alias such as “Gemini 4 Carbon.”
- Test upload validation, unsupported and oversized files, malformed provider responses, missing secrets, and offline/time-out behavior.
- Use Antigravity, VS Code, or another editor as a development tool; it does not itself train a model or guarantee general intelligence.

## Phase 2 — production web app

1. **Identity/access:** add authentication, per-user file ownership, CSRF protections for cookie sessions, rate limits, quotas, and authorization on every read/delete operation.
2. **Files:** use private object storage, random keys, content inspection and malware scanning, attachment delivery on a separate origin, explicit retention/deletion, and backups. Never execute uploads or expose the storage bucket publicly.
3. **Runtime:** deploy with a production WSGI server behind TLS; add secure headers, health/readiness probes, dependency scanning, redacted logs, monitoring, and incident response.
4. **Secrets:** use a managed secret store, separate credentials by environment, least privilege and rotation. Never put keys in frontend code, browser storage, source, or logs.
5. **Cloud Run:** Cloud Run can host the web tier, but it does not automatically connect to Wi-Fi-only WiCi One. Keep the UI local or design a reviewed private network path (VPN/private connector/secure gateway) with strict firewall/access controls. Otherwise choose a permitted cloud inference endpoint rather than exposing the device token.
6. **Optional search/workflow SaaS:** index only approved, non-sensitive fields. Restrict write keys to server-side ingestion and use search-only credentials in the client. Establish consent and data-processing rules before connecting automation/SaaS tools.

## Phase 3 — firmware and robotics

Firmware work is separate from the web app. Verify exact board, firmware provenance/checksum, serial port, bootloader/tool versions, stable power, backups, rollback/recovery, and a test device before flashing. Commands such as `mpremote cp` and `reset` must be tailored to the board and firmware format. Never expose firmware flashing as a web endpoint. Keep signed builds and release history for deployments beyond a lab device.

A human-capacity assistant should be designed with clear identity disclosure, safety limits, privacy controls, accessibility, and escalation paths. A conversational style prompt is not a real human identity or evidence of expertise. Do not market a retrieval script or model API wrapper as AGI.

## Model updates and evaluation

“Sync models” should mean a controlled selection of provider/model IDs and a versioned configuration—not copying proprietary weights, fine-tuning without data rights, or letting an agent alter production model settings. Store approved model IDs/configuration, test prompts and outputs for quality, safety, and regressions, and require human review before deployment. Model calls, embeddings, retrieval, and fine-tuning are distinct operations with different privacy and cost implications.

## Destructive cloud operations

Deleting a Cloud Run job or Google Cloud project is not part of setup. Before any deletion, verify active identity/project, list affected resources, export needed data, confirm backups and dependencies, and obtain owner approval. Prefer removing a named test resource over deleting a project. Never interpolate untrusted strings into shell commands.

# Private assistant: uploads, WiCi chat, Gemini, and local memory

This starter combines the four requested parts:

1. A Flask app for file uploads and downloads.
2. A browser chat UI with server-side WiCi One and Google Gemini API adapters.
3. A cleaned-up JCodePy local FAQ/memory helper and calculator.
4. A phased architecture plan for local development, cloud deployment, and device firmware.

JCodePy is lexical retrieval plus arithmetic, not AGI, a trained model, or a substitute for a model provider. Gemini and WiCi are called as configured services; this app does not train, synchronize, or autonomously modify models. Antigravity can be used as a coding environment to edit and test the project, subject to your account's available features.

## Run locally

Python 3.9+ (3.10+ recommended):

```sh
python -m venv .venv
. .venv/bin/activate          # Windows: .venv\\Scripts\\activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Populate `.env`, then export the variables into the shell (or use your preferred local environment loader; the app intentionally does not parse `.env`):

```sh
export CHAT_PROVIDER=wici
export WICI_BASE_URL=http://wici.local:8787
export WICI_DEVICE_TOKEN='your-new-paired-device-token'
python main.py
```

For Gemini instead, set `CHAT_PROVIDER=gemini`, `GEMINI_API_KEY`, and `GEMINI_MODEL` to a currently supported model ID from Google's official model list. The label “Gemini 4 Carbon” is not assumed to be a valid API model ID. Never put API keys in browser code or source control. Open http://127.0.0.1:5000. Health endpoint: http://127.0.0.1:5000/health.

### WiCi pairing

Install the private WiCi SDK/CLI using its official installation instructions, then pair and check the device, for example with `wici discover`, `wici pair`, and `wici doctor`. Confirm `http://wici.local:8787/v1/health/live` works from the app host. The server-side adapter uses WiCi's `/v1/responses` endpoint. Keep the device on a trusted network.

### Gemini configuration

The API key is sent only from the server to Google's Generative Language API. Select the current model identifier available for your Google API project and set it with `GEMINI_MODEL`; model names and availability can change. Review Google's current docs, data handling, quotas, and billing before sending prompts. Requests are not silently sent to both providers; the UI selects one per request.

## Upload behavior

Accepts UTF-8 TXT, JPEG, PNG, and GIF up to 10 MiB by default. It checks basic file signatures, sanitizes submitted names, stores objects under random UUID names in `uploads/`, and serves downloads as attachments. The folder is excluded from Git. Configure `UPLOAD_FOLDER` and `MAX_UPLOAD_BYTES` as needed.

This is a local single-user prototype without authentication. Before any shared/public use, add authentication and ownership checks, CSRF protections as applicable, quotas/rate limits, malware scanning, private object storage, retention/deletion controls, and backups. Never execute uploaded files.

## JCodePy helper

```sh
python jcodepy_agent.py
```

The helper creates `_base.json` with reviewed sample facts. Add vetted entries explicitly. It does not learn from arbitrary user prompts or fabricate a new answer when there is no match. The volume calculator validates inputs and returns a null ratio when the second box has zero volume.

## Tests

```sh
pytest
```

## Credential safety

A credential-like value was included in the original project notes. Treat it as compromised: revoke/rotate it with its issuer immediately, then supply only the replacement through environment variables or a secret manager. Avoid quoting the old value in logs, issues, or commits. The `.env` file and generated knowledge base are ignored by Git.

Do not run `gcloud projects delete` as an app setup step. Project deletion is destructive and unrelated to this web app.

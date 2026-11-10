import math
import os
import re
import tempfile
import uuid
from pathlib import Path

import requests
from flask import Flask, jsonify, render_template, request, send_from_directory
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = Path(os.environ.get("UPLOAD_FOLDER", BASE_DIR / "uploads")).resolve()
ALLOWED_EXTENSIONS = {"txt", "jpg", "jpeg", "png", "gif"}
MAX_UPLOAD_BYTES = int(os.environ.get("MAX_UPLOAD_BYTES", 10 * 1024 * 1024))
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_BYTES
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_upload(file_storage, extension):
    header = file_storage.stream.read(12)
    file_storage.stream.seek(0)
    if extension == "png":
        return header.startswith(b"\x89PNG\r\n\x1a\n")
    if extension in {"jpg", "jpeg"}:
        return header.startswith(b"\xff\xd8\xff")
    if extension == "gif":
        return header.startswith((b"GIF87a", b"GIF89a"))
    if extension == "txt":
        try:
            file_storage.stream.read().decode("utf-8")
            return True
        except UnicodeDecodeError:
            return False
        finally:
            file_storage.stream.seek(0)
    return False


def extract_gemini_text(payload):
    candidates = payload.get("candidates", [])
    if not candidates:
        return ""
    return "\n".join(
        part["text"] for part in candidates[0].get("content", {}).get("parts", [])
        if isinstance(part.get("text"), str)
    ).strip()


def extract_wici_text(payload):
    if isinstance(payload.get("output_text"), str):
        return payload["output_text"].strip()
    parts = []
    for item in payload.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"} and isinstance(content.get("text"), str):
                parts.append(content["text"])
    return "\n".join(parts).strip()


def ask_model(provider, message):
    if provider == "wici":
        base_url = os.environ.get("WICI_BASE_URL", "").rstrip("/")
        token = os.environ.get("WICI_DEVICE_TOKEN", "")
        if not base_url or not token:
            raise RuntimeError("WiCi is not configured. Set WICI_BASE_URL and WICI_DEVICE_TOKEN on the server.")
        response = requests.post(
            f"{base_url}/v1/responses",
            headers={"Authorization": f"Bearer {token}"},
            json={"model": os.environ.get("WICI_MODEL", "wici-assistant"), "input": message},
            timeout=(3.05, 90),
        )
        response.raise_for_status()
        return extract_wici_text(response.json())

    if provider == "gemini":
        api_key = os.environ.get("GEMINI_API_KEY", "")
        model = os.environ.get("GEMINI_MODEL", "")
        if not api_key or not model:
            raise RuntimeError("Gemini is not configured. Set GEMINI_API_KEY and GEMINI_MODEL on the server.")
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
            headers={"x-goog-api-key": api_key},
            json={"contents": [{"role": "user", "parts": [{"text": message}]}]},
            timeout=(3.05, 90),
        )
        response.raise_for_status()
        return extract_gemini_text(response.json())
    raise ValueError("Choose a supported provider: wici or gemini.")


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/health")
def health():
    return jsonify(ok=True)


@app.post("/api/upload")
def upload_file():
    if "file" not in request.files:
        return jsonify(error="Choose a file to upload."), 400
    uploaded = request.files["file"]
    if not uploaded.filename:
        return jsonify(error="Choose a file to upload."), 400
    original_name = secure_filename(uploaded.filename)
    if not original_name or not allowed_file(original_name):
        return jsonify(error="Allowed file types: TXT, JPG, JPEG, PNG, GIF."), 415
    extension = original_name.rsplit(".", 1)[1].lower()
    if not validate_upload(uploaded, extension):
        return jsonify(error="File content does not match the selected type, or the text is not UTF-8."), 415
    stored_name = f"{uuid.uuid4().hex}.{extension}"
    uploaded.save(UPLOAD_DIR / stored_name)
    return jsonify(success=True, filename=stored_name, original_name=original_name), 201


@app.get("/api/uploads/<filename>")
def download_upload(filename):
    if not re.fullmatch(r"[0-9a-f]{32}\.(txt|jpg|jpeg|png|gif)", filename):
        return jsonify(error="File not found."), 404
    return send_from_directory(UPLOAD_DIR, filename, as_attachment=True, download_name=filename)


@app.post("/api/chat")
def chat():
    body = request.get_json(silent=True) or {}
    message = body.get("message")
    provider = body.get("provider", os.environ.get("CHAT_PROVIDER", "wici"))
    if not isinstance(message, str) or not message.strip():
        return jsonify(error="Enter a message."), 400
    if len(message) > 4000:
        return jsonify(error="Message is too long (maximum 4,000 characters)."), 413
    if provider not in {"wici", "gemini"}:
        return jsonify(error="Choose a supported provider: WiCi or Gemini."), 400
    try:
        answer = ask_model(provider, message.strip())
        if not answer:
            return jsonify(error="The model returned no text. Please try again."), 502
        return jsonify(answer=answer, provider=provider)
    except RuntimeError as exc:
        return jsonify(error=str(exc)), 503
    except requests.Timeout:
        return jsonify(error="The model request timed out. Check its availability and try again."), 504
    except requests.RequestException:
        app.logger.exception("Model provider request failed (%s)", provider)
        return jsonify(error="Could not reach the configured model provider."), 502
    except (ValueError, KeyError, TypeError):
        app.logger.exception("Model provider returned an invalid response (%s)", provider)
        return jsonify(error="The model provider returned an invalid response."), 502


@app.errorhandler(413)
def upload_too_large(_error):
    return jsonify(error=f"Request exceeds the configured {MAX_UPLOAD_BYTES // (1024 * 1024)} MB limit."), 413


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")), debug=False)

"""Opt-in loopback-only Ollama adapter using the existing requests dependency.

Never pulls/installs models, accepts a remote endpoint, follows redirects, uses
environment proxies, retries, or makes requests on import/ordinary UI rendering.
"""

import re

import requests

from .analysis import MODEL, OPTIONS, strict_json


ENDPOINT = "http://127.0.0.1:11434"


class BackendError(ValueError):
    """Sanitized backend failure, safe to show without research content."""


class OllamaLocal:
    def _request(self, path, body=None, generation=False):
        try:
            with requests.Session() as session:
                session.trust_env = False
                with session.request("GET" if body is None else "POST", ENDPOINT + path,
                                     json=body, timeout=(2, 120 if generation else 3),
                                     allow_redirects=False, stream=True) as response:
                    if response.status_code != 200:
                        raise BackendError("Local model request failed. Check the local runtime; review work is unchanged.")
                    data = bytearray()
                    for part in response.iter_content(chunk_size=4096):
                        data.extend(part)
                        if len(data) > 32 * 1024:
                            raise BackendError("Local model response exceeded the safe size limit.")
                    return strict_json(data.decode("utf-8"))
        except (requests.RequestException, UnicodeError, ValueError, RecursionError) as error:
            # Never render backend body, parser detail, request prompt or exception URL.
            if isinstance(error, BackendError):
                raise
            raise BackendError("Local model unavailable, timed out or returned invalid data. Review work is unchanged.") from error

    def _model(self):
        payload = self._request("/api/tags")
        if not isinstance(payload, dict) or not isinstance(payload.get("models"), list):
            raise BackendError("Invalid local model inventory.")
        matches = [m for m in payload["models"] if isinstance(m, dict) and m.get("name") == MODEL]
        if len(matches) != 1:
            raise BackendError("The selected local model is not installed. See docs/LOCAL_MODEL_SETUP.md; no model was downloaded.")
        model = matches[0]
        if model.get("remote_host") or model.get("remote_model") or not isinstance(model.get("digest"), str) or not re.fullmatch(
                r"[0-9a-f]{64}", model["digest"]):
            raise BackendError("A local model with a recorded digest is required; cloud models are disabled.")
        return model

    def inspect(self):
        version = self._request("/api/version")
        if not isinstance(version, dict) or not isinstance(version.get("version"), str) or not version["version"].strip():
            raise BackendError("Invalid local runtime version.")
        model = self._model()
        show = self._request("/api/show", {"model": MODEL})
        if not isinstance(show, dict) or show.get("remote_host") or show.get("remote_model") or not isinstance(show.get("details"), dict):
            raise BackendError("The backend must serve local model weights.")
        details = show["details"]
        if any(details.get(k) != v for k, v in {
                "format": "gguf", "parameter_size": "1.5B", "quantization_level": "Q4_K_M"}.items()):
            raise BackendError("The installed model does not match the selected local model configuration.")
        return {"backend": "ollama-local", "endpoint": ENDPOINT, "model": MODEL,
                "model_digest": model["digest"], "runtime_version": version["version"]}

    def generate(self, request):
        identity = self.inspect()  # Never sends paper text until the local model is confirmed.
        result = self._request("/api/generate", {**request, "model": MODEL}, generation=True)
        if not isinstance(result, dict) or result.get("model") != MODEL or result.get("done") is not True or result.get("done_reason") != "stop":
            raise BackendError("Local generation was incomplete or identified a different model; no proposal was saved.")
        count = result.get("prompt_eval_count")
        if type(count) is not int or count < 1 or count >= OPTIONS["num_ctx"] - OPTIONS["num_predict"]:
            raise BackendError("Local prompt exceeded the reserved context budget; no proposal was saved.")
        if self._model()["digest"] != identity["model_digest"]:
            raise BackendError("The local model changed during generation; no proposal was saved.")
        if not isinstance(result.get("response"), str):
            raise BackendError("Local generation returned invalid response text.")
        return {**identity, "response": result["response"]}

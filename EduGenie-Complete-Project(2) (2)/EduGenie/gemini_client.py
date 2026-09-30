import os
import re
import time

from google import genai
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
SUPPORTED_MODELS = {"gemini-3.8-flash"}


def get_configured_model() -> str:
    configured = (os.getenv("GEMINI_MODEL") or "").strip()
    if configured in SUPPORTED_MODELS:
        return configured
    return "gemini-3.8-flash"


DEFAULT_MODELS = [get_configured_model()]
_client = None


def get_client():
    global _client
    if not API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Create a .env file and add your Gemini API key."
        )
    if _client is None:
        _client = genai.Client(api_key=API_KEY)
    return _client


def _candidate_models():
    seen = set()
    for model in DEFAULT_MODELS:
        if model and model not in seen:
            seen.add(model)
            yield model


def _extract_status_code(error: Exception):
    for attribute in ("status_code", "code"):
        value = getattr(error, attribute, None)
        if isinstance(value, int):
            return value

    response = getattr(error, "response", None)
    if response is not None:
        status = getattr(response, "status_code", None)
        if isinstance(status, int):
            return status

    message = str(error)
    for token in ("429", "503", "400", "401", "404"):
        if token in message:
            try:
                return int(token)
            except ValueError:
                pass
    return None


def _extract_retry_after(error: Exception):
    response = getattr(error, "response", None)
    if response is not None:
        headers = getattr(response, "headers", {}) or {}
        for key in ("Retry-After", "retry-after"):
            value = headers.get(key)
            if value is not None:
                try:
                    return float(value)
                except (TypeError, ValueError):
                    pass

    message = str(error)
    match = re.search(r"retry[_ -]?after[:= ](\d+(?:\.\d+)?)", message, flags=re.IGNORECASE)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            pass
    return None


def _classify_error(error: Exception) -> str:
    status_code = _extract_status_code(error)
    message = str(error).lower()

    if status_code == 429 or "resource_exhausted" in message or "quota" in message or "free_tier" in message:
        if "rate limit" in message or "rate_limit" in message:
            return "rate_limit"
        return "quota"

    if status_code == 503 or "unavailable" in message or "temporarily" in message:
        return "server_unavailable"

    if status_code in (400, 401) and (
        "api key" in message or "api_key" in message or "invalid key" in message or "auth" in message
    ):
        return "api_key"

    if status_code == 404 and (
        "model" in message or "not available" in message or "deprecated" in message
    ):
        return "unsupported_model"

    return "unknown"


def _friendly_error_message(error: Exception, kind: str = None) -> str:
    kind = kind or _classify_error(error)

    if kind == "quota":
        return (
            "Gemini API daily quota has been reached. Please try again after the quota resets "
            "or check your Gemini API usage/billing settings."
        )
    if kind == "rate_limit":
        return "Gemini API is temporarily rate-limited. Please try again shortly."
    if kind == "server_unavailable":
        return "Gemini is temporarily unavailable. Please try again shortly."
    if kind == "api_key":
        return "Gemini API key configuration error. Please check the .env configuration."
    if kind == "unsupported_model":
        return "Gemini model configuration error. Please check the configured model in .env."
    return "Gemini API request failed. Please try again shortly."


def generate_text(prompt: str, max_retries: int = 3) -> str:
    client = get_client()
    last_error = None

    for attempt in range(max_retries + 1):
        for model_name in _candidate_models():
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )
                text = getattr(response, "text", None)
                if text:
                    return text.strip()
                raise RuntimeError("Gemini returned an empty response.")
            except Exception as exc:  # pragma: no cover - depends on live Google API
                last_error = exc
                kind = _classify_error(exc)

                if kind in ("quota", "api_key", "unsupported_model"):
                    raise RuntimeError(_friendly_error_message(exc, kind))

                if kind in ("rate_limit", "server_unavailable"):
                    if attempt < max_retries:
                        delay = _extract_retry_after(exc) or (2 ** attempt)
                        time.sleep(delay)
                        continue
                    raise RuntimeError(_friendly_error_message(exc, kind))

                raise RuntimeError(_friendly_error_message(exc, kind))

    if last_error is not None:
        raise RuntimeError(_friendly_error_message(last_error, _classify_error(last_error)))

    raise RuntimeError("Gemini generation failed. Please try again shortly.")

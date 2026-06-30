"""Zoho OAuth token management with automatic refresh and .env persistence."""

from __future__ import annotations

import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(ENV_PATH)

# In-memory cache so we refresh only when needed, not on every import.
_token_cache: dict[str, float | str | None] = {
    "access_token": None,
    "expires_at": 0.0,
}


def _env(key: str, default: str = "") -> str:
    return os.getenv(key, default)


def _accounts_url() -> str:
    return _env("ZOHO_ACCOUNTS_URL", "https://accounts.zoho.in")


def update_env_file(updates: dict[str, str]) -> None:
    """Update or append keys in .env without touching other values."""
    lines: list[str] = []
    if ENV_PATH.exists():
        lines = ENV_PATH.read_text(encoding="utf-8").splitlines()

    remaining = dict(updates)
    new_lines: list[str] = []

    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in line:
            key = line.split("=", 1)[0].strip()
            if key in remaining:
                new_lines.append(f"{key}={remaining.pop(key)}")
                continue
        new_lines.append(line)

    for key, value in remaining.items():
        new_lines.append(f"{key}={value}")

    ENV_PATH.write_text("\n".join(new_lines).rstrip() + "\n", encoding="utf-8")

    for key, value in updates.items():
        os.environ[key] = value


def _persist_tokens(data: dict) -> str:
    """Save refreshed tokens to .env and process env."""
    access_token = data["access_token"]
    updates: dict[str, str] = {"ZOHO_ACCESS_TOKEN": access_token}

    if data.get("refresh_token"):
        updates["ZOHO_REFRESH_TOKEN"] = data["refresh_token"]

    update_env_file(updates)

    expires_in = int(data.get("expires_in", 3600))
    _token_cache["access_token"] = access_token
    # Refresh one minute before expiry.
    _token_cache["expires_at"] = time.time() + max(expires_in - 60, 60)

    return access_token


def _refresh_error_message(data: dict) -> str:
    error = data.get("error", "unknown_error")
    if error in {"invalid_code", "invalid_grant"}:
        return (
            "Zoho refresh token is invalid or expired. Run once:\n"
            "  python get_zoho_token.py\n"
            "Approve access in the browser, then:\n"
            "  python get_zoho_token.py <auth_code>\n"
            "Tokens will be saved to .env automatically."
        )
    return f"Unable to refresh Zoho access token: {data}"


def refresh_access_token(*, force: bool = False) -> str:
    """
    Exchange the refresh token for a new access token and persist it to .env.
    Uses an in-memory cache unless force=True or the token is near expiry.
    """
    # The MCP server process can stay alive for a long time; reload .env so
    # tokens refreshed by external helpers (e.g. get_zoho_token.py) are picked up.
    load_dotenv(ENV_PATH, override=True)

    if not force:
        cached = _token_cache.get("access_token")
        expires_at = float(_token_cache.get("expires_at") or 0)
        if isinstance(cached, str) and cached and time.time() < expires_at:
            return cached

    refresh_token = _env("ZOHO_REFRESH_TOKEN")
    client_id = _env("ZOHO_CLIENT_ID")
    client_secret = _env("ZOHO_CLIENT_SECRET")

    if not refresh_token:
        access_token = _env("ZOHO_ACCESS_TOKEN")
        if access_token:
            return access_token
        raise RuntimeError(
            "No ZOHO_REFRESH_TOKEN configured. Run: python get_zoho_token.py"
        )

    if not client_id or not client_secret:
        raise RuntimeError("ZOHO_CLIENT_ID and ZOHO_CLIENT_SECRET must be set in .env")

    url = f"{_accounts_url()}/oauth/v2/token"
    params = {
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
    }

    response = requests.post(url, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    if "access_token" not in data:
        raise RuntimeError(_refresh_error_message(data))

    return _persist_tokens(data)


def get_access_token(*, force: bool = False) -> str:
    """Return a valid Zoho access token, refreshing automatically when needed."""
    return refresh_access_token(force=force)


def zoho_request(
    method: str,
    url: str,
    *,
    headers: dict | None = None,
    data: dict | None = None,
    timeout: int = 30,
) -> requests.Response:
    """
    Call the Zoho API with automatic token refresh.
    Retries once on 401 after forcing a new access token.
    """
    request_headers = dict(headers or {})
    access_token = get_access_token()
    request_headers["Authorization"] = f"Zoho-oauthtoken {access_token}"

    response = requests.request(
        method,
        url,
        headers=request_headers,
        data=data,
        timeout=timeout,
    )

    if response.status_code != 401:
        return response

    access_token = refresh_access_token(force=True)
    request_headers["Authorization"] = f"Zoho-oauthtoken {access_token}"
    return requests.request(
        method,
        url,
        headers=request_headers,
        data=data,
        timeout=timeout,
    )

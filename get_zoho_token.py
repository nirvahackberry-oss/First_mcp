import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

import requests

from config import (
    ZOHO_ACCOUNTS_URL,
    ZOHO_CLIENT_ID,
    ZOHO_CLIENT_SECRET,
    ZOHO_REDIRECT_URI,
)
from zoho_auth import update_env_file

SCOPES = "ZohoSheet.dataAPI.READ,ZohoSheet.dataAPI.UPDATE"
AUTH_URL = (
    f"{ZOHO_ACCOUNTS_URL}/oauth/v2/auth"
    f"?scope={SCOPES}"
    f"&client_id={ZOHO_CLIENT_ID}"
    "&response_type=code"
    "&access_type=offline"
    f"&redirect_uri={ZOHO_REDIRECT_URI}"
)


def exchange_code(auth_code: str) -> dict:
    url = f"{ZOHO_ACCOUNTS_URL}/oauth/v2/token"
    params = {
        "grant_type": "authorization_code",
        "client_id": ZOHO_CLIENT_ID,
        "client_secret": ZOHO_CLIENT_SECRET,
        "redirect_uri": ZOHO_REDIRECT_URI,
        "code": auth_code,
    }
    response = requests.post(url, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    if "access_token" not in data:
        raise RuntimeError(f"Token exchange failed: {data}")

    updates = {"ZOHO_ACCESS_TOKEN": data["access_token"]}
    if data.get("refresh_token"):
        updates["ZOHO_REFRESH_TOKEN"] = data["refresh_token"]

    update_env_file(updates)
    return data


def auto_authorize() -> dict:
    """Open browser, capture OAuth callback on localhost, and exchange the code."""
    parsed = urlparse(ZOHO_REDIRECT_URI)
    host = parsed.hostname or "localhost"
    port = parsed.port or 8080
    result: dict = {}
    event = threading.Event()

    class CallbackHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            query = parse_qs(urlparse(self.path).query)
            if "code" in query:
                result["code"] = query["code"][0]
                body = b"<html><body><h2>Zoho authorized. You can close this tab.</h2></body></html>"
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(body)
            else:
                error = query.get("error", ["unknown"])[0]
                result["error"] = error
                body = f"<html><body><h2>Authorization failed: {error}</h2></body></html>".encode()
                self.send_response(400)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(body)
            event.set()

        def log_message(self, format, *args):
            return

    server = HTTPServer((host, port), CallbackHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    print("Opening browser for Zoho authorization...")
    print(f"If it does not open, visit:\n{AUTH_URL}\n")
    webbrowser.open(AUTH_URL)

    if not event.wait(timeout=180):
        server.shutdown()
        raise TimeoutError("Timed out waiting for Zoho authorization (3 minutes).")

    server.shutdown()

    if "error" in result:
        raise RuntimeError(f"Zoho authorization failed: {result['error']}")
    if "code" not in result:
        raise RuntimeError("No authorization code received from Zoho.")

    return exchange_code(result["code"])


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] in {"--auto", "-a"}:
        data = auto_authorize()
        print("Tokens saved to .env")
        print("access_token: received")
        if data.get("refresh_token"):
            print("refresh_token: received and saved")
        else:
            print("refresh_token: not returned (existing refresh token in .env is still used)")
        sys.exit(0)

    if len(sys.argv) < 2:
        print("Open this URL in your browser, approve access, then copy the code from the redirect URL:")
        print(AUTH_URL)
        print()
        print("Run: python get_zoho_token.py <auth_code>")
        print("Or:  python get_zoho_token.py --auto")
        print("Tokens are saved to .env automatically.")
        sys.exit(0)

    result = exchange_code(sys.argv[1])
    print("Tokens saved to .env")
    print("access_token: received")
    if result.get("refresh_token"):
        print("refresh_token: received and saved")
    else:
        print("refresh_token: not returned (existing refresh token in .env is still used)")

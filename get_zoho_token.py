import sys

import requests

from config import (
    ZOHO_ACCOUNTS_URL,
    ZOHO_CLIENT_ID,
    ZOHO_CLIENT_SECRET,
    ZOHO_REDIRECT_URI,
)

SCOPES = "ZohoSheet.dataAPI.READ,ZohoSheet.dataAPI.UPDATE"
AUTH_URL = (
    f"{ZOHO_ACCOUNTS_URL}/oauth/v2/auth"
    f"?scope={SCOPES}"
    f"&client_id={ZOHO_CLIENT_ID}"
    "&response_type=code"
    "&access_type=offline"
    f"&redirect_uri={ZOHO_REDIRECT_URI}"
)


def exchange_code(auth_code: str):
    url = f"{ZOHO_ACCOUNTS_URL}/oauth/v2/token"
    params = {
        "grant_type": "authorization_code",
        "client_id": ZOHO_CLIENT_ID,
        "client_secret": ZOHO_CLIENT_SECRET,
        "redirect_uri": ZOHO_REDIRECT_URI,
        "code": auth_code,
    }
    response = requests.post(url, params=params)
    print(response.status_code)
    print(response.json())


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Open this URL in your browser, approve access, then copy the code from the redirect URL:")
        print(AUTH_URL)
        print()
        print("Run: python get_zoho_token.py <auth_code>")
        print("Then copy refresh_token and access_token into your .env file.")
        sys.exit(0)

    exchange_code(sys.argv[1])

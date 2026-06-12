import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")


def _env(key: str, default: str = "") -> str:
    return os.getenv(key, default)


PROJECTS = {
    "vlab": r"C:\isolated-lab",
    "laajavaab": r"C:\boutique\boutique",
}

# Only include git activity from these branches in daily reports.
REPORT_BRANCHES = {
    "vlab": ["Nirva", "main"],
    "laajavaab": ["Nirva"],
}

# Cursor workspace slugs under %USERPROFILE%\.cursor\projects\
CURSOR_TRANSCRIPTS_ROOT = r"C:\Users\baps\.cursor\projects"
CURSOR_PROJECTS = {
    "vlab": "c-isolated-lab",
    "laajavaab": "c-boutique-boutique",
}

EXCEL_FILE = r"c:\Nirva Padaliya Task Sheet.xlsx"

# Zoho credentials loaded from .env
ZOHO_CLIENT_ID = _env("ZOHO_CLIENT_ID")
ZOHO_CLIENT_SECRET = _env("ZOHO_CLIENT_SECRET")
ZOHO_REFRESH_TOKEN = _env("ZOHO_REFRESH_TOKEN")
ZOHO_ACCESS_TOKEN = _env("ZOHO_ACCESS_TOKEN")
ZOHO_WORKBOOK_ID = _env("ZOHO_WORKBOOK_ID")
ZOHO_SHEET_ID = _env("ZOHO_SHEET_ID", "0")
ZOHO_ACCOUNTS_URL = _env("ZOHO_ACCOUNTS_URL", "https://accounts.zoho.in")
ZOHO_SHEET_API_URL = _env("ZOHO_SHEET_API_URL", "https://sheet.zoho.in/api/v2")
ZOHO_REDIRECT_URI = _env("ZOHO_REDIRECT_URI", "http://localhost:8080/callback")

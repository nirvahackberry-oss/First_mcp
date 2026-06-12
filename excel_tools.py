# from openpyxl import load_workbook
# from copy import copy
# from datetime import datetime

# EXCEL_FILE = "Nirva Padaliya Task Sheet.xlsx"   # Change to your file
# SHEET_NAME = "Sheet1"             # Change if needed


# def add_report_row(
#     project_name: str,
#     task_module: str,
#     description: str,
#     status: str = "Completed"
# ):
#     """
#     Append a new work report row without changing spreadsheet formatting.

#     Rules:
#     - Never overwrite existing rows.
#     - Always append a new row.
#     - Copy formatting, styles, formulas, and validations from
#       the previous row.
#     - Only update the new row values.
#     """

#     wb = load_workbook(EXCEL_FILE)
#     ws = wb[SHEET_NAME]

#     # Last row containing data
#     last_row = ws.max_row
#     new_row = last_row + 1

#     # Create a new row
#     ws.insert_rows(new_row)

#     # Copy formatting from previous row
#     for col in range(1, ws.max_column + 1):
#         source = ws.cell(row=last_row, column=col)
#         target = ws.cell(row=new_row, column=col)

#         if source.has_style:
#             target._style = copy(source._style)

#         target.font = copy(source.font)
#         target.fill = copy(source.fill)
#         target.border = copy(source.border)
#         target.alignment = copy(source.alignment)
#         target.number_format = source.number_format
#         target.protection = copy(source.protection)

#         # Copy formulas if any
#         if (
#             isinstance(source.value, str)
#             and source.value.startswith("=")
#         ):
#             target.value = source.value

#     # Copy row height
#     if last_row in ws.row_dimensions:
#         ws.row_dimensions[new_row].height = (
#             ws.row_dimensions[last_row].height
#         )

#     # ------------------------------------------------------------------
#     # Update only the required cells.
#     # Adjust the column numbers below to match your Excel layout.
#     #
#     # Example:
#     # B = Serial No
#     # C = Date
#     # D = Project
#     # E = Description
#     # G = Updated Date
#     # H = Status
#     # ------------------------------------------------------------------

#     ws.cell(new_row, 2).value = new_row - 1  # Optional serial number
#     ws.cell(new_row, 3).value = datetime.now().strftime("%d/%m/%Y")
#     ws.cell(new_row, 4).value = project_name
#     ws.cell(new_row, 5).value = task_module
#     ws.cell(new_row, 6).value = description
#     ws.cell(new_row, 7).value = screen_short
#     ws.cell(new_row, 7).value = datetime.now().strftime("%d/%m/%Y")
#     ws.cell(new_row, 8).value = status

#     wb.save(EXCEL_FILE)

#     return {
#         "success": True,
#         "message": "Report added successfully.",
#         "row": new_row
#     }


import json
import requests
from datetime import datetime

from config import (
    ZOHO_ACCESS_TOKEN,
    ZOHO_ACCOUNTS_URL,
    ZOHO_CLIENT_ID,
    ZOHO_CLIENT_SECRET,
    ZOHO_REFRESH_TOKEN,
    ZOHO_SHEET_API_URL,
    ZOHO_WORKBOOK_ID,
)

SHEET_NAME = "Sheet1"


def get_access_token():
    """Get a fresh access token using the refresh token, or fall back to config."""
    if not ZOHO_REFRESH_TOKEN:
        if ZOHO_ACCESS_TOKEN:
            return ZOHO_ACCESS_TOKEN
        raise Exception("No ZOHO_REFRESH_TOKEN or ZOHO_ACCESS_TOKEN configured.")

    url = f"{ZOHO_ACCOUNTS_URL}/oauth/v2/token"

    params = {
        "refresh_token": ZOHO_REFRESH_TOKEN,
        "client_id": ZOHO_CLIENT_ID,
        "client_secret": ZOHO_CLIENT_SECRET,
        "grant_type": "refresh_token",
    }

    response = requests.post(url, params=params)
    response.raise_for_status()

    data = response.json()

    if "access_token" not in data:
        raise Exception(f"Unable to get access token: {data}")

    return data["access_token"]


def add_report_row(
    project_name: str,
    task_module: str,
    description: str,
    status: str = "Completed",
    report_date: str | None = None,
):
    """
    Add a NEW record to the Zoho Sheet.
    Rules:
    - Never overwrite existing rows.
    - Always append a new row.
    - Copy formatting, styles, formulas, and validations from
    the previous row.
    - Only update the new row values.
    """
    



    access_token = get_access_token()
    date_str = report_date or datetime.now().strftime("%d/%m/%Y")

    url = f"{ZOHO_SHEET_API_URL}/{ZOHO_WORKBOOK_ID}"

    headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}",
        "Content-type": "application/x-www-form-urlencoded;charset=UTF-8",
    }

    # Keys MUST exactly match the column headers in Sheet1.
    row_data = [{
        "SR NO.": "",  # Leave blank if you want Zoho/formulas to handle it
        "DATE": date_str,
        "PROJECT NAME": project_name,
        "TASK /MODULE": task_module,
        "DESCRIPTION": description,
        "SCREENSHORT": "",  # Or put a screenshot URL/path if you have one
        "DUE DATE": date_str,
        "STATUS": status
    }]

    payload = {
        "method": "worksheet.records.add",
        "worksheet_name": SHEET_NAME,
        "json_data": json.dumps(row_data)
    }

    response = requests.post(
        url,
        headers=headers,
        data=payload,
        timeout=30
    )

    try:
        result = response.json()
    except Exception:
        result = response.text

    return {
        "success": response.ok,
        "status_code": response.status_code,
        "response": result
    }
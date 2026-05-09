import os
import base64
import json
from datetime import date

import gspread


def get_sheet():
    raw = os.environ["GOOGLE_CREDENTIALS"]
    try:
        creds_dict = json.loads(raw)
    except json.JSONDecodeError:
        creds_dict = json.loads(base64.b64decode(raw).decode("utf-8"))
    client = gspread.service_account_from_dict(creds_dict)
    return client.open_by_key(os.environ["SPREADSHEET_ID"].strip()).sheet1


def main():
    target_date = os.environ.get("TARGET_DATE", "").strip() or date.today().isoformat()
    sheet = get_sheet()
    all_values = sheet.get_all_values()

    updated = 0
    for i, row in enumerate(all_values[1:], start=2):
        if len(row) >= 4 and row[2].strip() == target_date and row[3].strip().upper() != "TRUE":
            sheet.update_cell(i, 4, "TRUE")
            updated += 1
            print(f"  行{i} [{target_date}] を投稿済みにしました: {row[1][:40]}...")

    if updated == 0:
        print(f"{target_date} に投稿済みにする対象がありませんでした。")
    else:
        print(f"{updated}件を投稿済みにしました。")


if __name__ == "__main__":
    main()

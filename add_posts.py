import os
import base64
import json
from datetime import date, timedelta

import gspread

HEADER_ROW = 1


def get_sheet():
    raw = os.environ["GOOGLE_CREDENTIALS"]
    try:
        creds_dict = json.loads(raw)
    except json.JSONDecodeError:
        creds_dict = json.loads(base64.b64decode(raw).decode("utf-8"))
    client = gspread.service_account_from_dict(creds_dict)
    return client.open_by_key(os.environ["SPREADSHEET_ID"].strip()).sheet1


def main():
    posts_text = os.environ.get("POSTS", "").strip()
    if not posts_text:
        print("No posts provided.")
        return

    lines = [line.strip() for line in posts_text.split("\n") if line.strip()]
    if not lines:
        print("No valid posts found.")
        return

    sheet = get_sheet()
    all_values = sheet.get_all_values()

    last_row = len(all_values)
    next_id = 1
    if last_row > 1:
        try:
            next_id = int(all_values[-1][0]) + 1
        except (ValueError, IndexError):
            next_id = last_row

    tomorrow = date.today() + timedelta(days=1)
    next_date = tomorrow
    if last_row > 1:
        for row in reversed(all_values[1:]):
            try:
                d = date.fromisoformat(row[2])
                if d >= tomorrow:
                    next_date = d + timedelta(days=1)
                break
            except (ValueError, IndexError):
                continue

    rows = []
    for i, text in enumerate(lines):
        rows.append([next_id + i, text, next_date.isoformat(), "FALSE"])
        next_date += timedelta(days=1)

    sheet.append_rows(rows, value_input_option="RAW")
    print(f"{len(rows)}件をスプレッドシートに追加しました。")
    for row in rows:
        print(f"  [{row[2]}] {row[1][:40]}...")


if __name__ == "__main__":
    main()

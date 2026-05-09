import os
import base64
import json
from datetime import date

import tweepy
import gspread

HEADER_ROW = 1
COL_ID = 1
COL_TEXT = 2
COL_SCHEDULED_DATE = 3
COL_POSTED = 4


def get_spreadsheet():
    raw = os.environ["GOOGLE_CREDENTIALS"]
    try:
        creds_dict = json.loads(raw)
    except json.JSONDecodeError:
        creds_dict = json.loads(base64.b64decode(raw).decode("utf-8"))
    print(f"[DEBUG] service_account: {creds_dict.get('client_email')}")
    client = gspread.service_account_from_dict(creds_dict)
    spreadsheet_id = os.environ["SPREADSHEET_ID"].strip()
    print(f"[DEBUG] spreadsheet_id: '{spreadsheet_id}' (len={len(spreadsheet_id)})")
    return client.open_by_key(spreadsheet_id).sheet1


def get_x_client():
    return tweepy.Client(
        consumer_key=os.environ["X_API_KEY"],
        consumer_secret=os.environ["X_API_KEY_SECRET"],
        access_token=os.environ["X_ACCESS_TOKEN"],
        access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"],
    )


def find_todays_posts(sheet):
    today = date.today().isoformat()
    records = sheet.get_all_records()
    results = []
    for i, row in enumerate(records, start=HEADER_ROW + 1):
        if str(row.get("scheduled_date", "")).strip() == today and str(row.get("posted", "")).strip().upper() != "TRUE":
            results.append((i, row))
    return results


def mark_as_posted(sheet, row_index):
    sheet.update_cell(row_index, COL_POSTED, "TRUE")


def main():
    sheet = get_spreadsheet()
    x_client = get_x_client()

    targets = find_todays_posts(sheet)

    if not targets:
        print("No posts scheduled for today.")
        return

    for row_index, row in targets:
        text = str(row["text"]).strip()
        print(f"Posting row {row_index}: {text[:50]}...")
        x_client.create_tweet(text=text)
        mark_as_posted(sheet, row_index)
        print(f"Row {row_index} posted and marked as done.")


if __name__ == "__main__":
    main()

import os
import base64
import json
from datetime import date

import tweepy
import gspread
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

HEADER_ROW = 1
COL_ID = 1
COL_TEXT = 2
COL_SCHEDULED_DATE = 3
COL_POSTED = 4


def get_spreadsheet():
    raw = os.environ["GOOGLE_CREDENTIALS"]
    # Base64エンコード済みでも生JSONでも両方対応
    try:
        creds_dict = json.loads(raw)
    except json.JSONDecodeError:
        creds_dict = json.loads(base64.b64decode(raw).decode("utf-8"))
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    client = gspread.authorize(creds)
    spreadsheet_id = os.environ["SPREADSHEET_ID"]
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

#!/usr/bin/env python3
"""One-time helper to obtain GOOGLE_CALENDAR_REFRESH_TOKEN. Run locally, not in Docker."""

import os

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]


def main():
    client_file = os.environ.get("GOOGLE_OAUTH_CLIENT_FILE", "client_secret.json")
    if not os.path.isfile(client_file):
        print(f"Download OAuth client JSON from Google Cloud Console and save as {client_file}")
        print("Or set GOOGLE_OAUTH_CLIENT_FILE=/path/to/client_secret.json")
        raise SystemExit(1)

    flow = InstalledAppFlow.from_client_secrets_file(client_file, SCOPES)
    creds = flow.run_local_server(port=0)
    print("\nAdd to server/.env:\n")
    print(f"GOOGLE_OAUTH_CLIENT_ID={creds.client_id}")
    print(f"GOOGLE_OAUTH_CLIENT_SECRET={creds.client_secret}")
    print(f"GOOGLE_CALENDAR_REFRESH_TOKEN={creds.refresh_token}")


if __name__ == "__main__":
    main()

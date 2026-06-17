#!/usr/bin/env python3
"""Legacy local helper — prefer connecting Google Calendar in Settings (OAuth UI).

Prints GOOGLE_OAUTH_CLIENT_ID/SECRET for server/.env. Per-user refresh tokens are stored in DB.
"""

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
    print("\nAdd to server/.env (OAuth app credentials only):\n")
    print(f"GOOGLE_OAUTH_CLIENT_ID={creds.client_id}")
    print(f"GOOGLE_OAUTH_CLIENT_SECRET={creds.client_secret}")
    print("GOOGLE_OAUTH_REDIRECT_URI=http://localhost:3000/settings/google-callback")
    print("\nThen each user connects Google in Settings → Connect Google.")


if __name__ == "__main__":
    main()

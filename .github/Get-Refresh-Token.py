"""
Hae YouTube Refresh Token KERRAN omalla koneella
Tämä ajetaan VAIN kerran omalla koneella, ei GitHubissa

Ohje:
1. Mene console.cloud.google.com -> Luo projekti -> Enable YouTube Data API v3
2. Credentials -> Create Credentials -> OAuth Client ID -> Desktop App
3. Lataa client_secret.json tähän kansioon
4. pip install google-auth-oauthlib google-api-python-client
5. python get_refresh_token.py
6. Selain aukeaa -> Kirjaudu World Viral Google-tilillä -> Salli
7. Saat refresh_tokenin - kopioi se GitHub Secretsiin
"""

import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def main():
    if not os.path.exists("client_secret.json"):
        print("❌ Puuttuu client_secret.json")
        print("1. Mene console.cloud.google.com")
        print("2. APIs & Services -> Credentials -> Create Credentials -> OAuth Client ID")
        print("3. Application type: Desktop App")
        print("4. Lataa JSON ja nimeä se client_secret.json tähän kansioon")
        return

    flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
    creds = flow.run_local_server(port=0)

    print("\n" + "="*60)
    print("✅ ONNISTUI! Kopioi nämä GitHub Secretsiin:")
    print("="*60)
    print(f"\nYOUTUBE_CLIENT_ID: {creds.client_id}")
    print(f"\nYOUTUBE_CLIENT_SECRET: {creds.client_secret}")
    print(f"\nYOUTUBE_REFRESH_TOKEN: {creds.refresh_token}")
    print("\n" + "="*60)
    print("\nMene GitHub -> Settings -> Secrets and variables -> Actions")
    print("Lisää 3 uutta secretia yllä olevilla arvoilla")
    print("\nTärkeää: Lisää myös itsesi Test Useriksi Google Cloudissa:")
    print("console.cloud.google.com -> OAuth consent screen -> Test users -> Add your email")

    # Save for local test
    with open("token.json", "w") as f:
        json.dump({
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "refresh_token": creds.refresh_token
        }, f, indent=2)

if __name__ == "__main__":
    main()

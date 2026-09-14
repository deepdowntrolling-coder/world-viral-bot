"""
WORLD VIRAL - YouTube Auto Uploader
100% Free - Uses YouTube Data API v3

Tarvitset:
1. client_secret.json Google Cloudista (ilmainen)
2. refresh_token joka luodaan kerran omalla koneella

Tämän jälkeen botti lataa automaattisesti GitHub Actionsissa.
"""

import os
import pickle
import json
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Scopes for YouTube upload
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_authenticated_service():
    """
    Hakee autentikoinnin env muuttujista (GitHub Secrets)
    """
    client_id = os.getenv("YOUTUBE_CLIENT_ID")
    client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
    refresh_token = os.getenv("YOUTUBE_REFRESH_TOKEN")

    if not all([client_id, client_secret, refresh_token]):
        print("❌ Puuttuu YOUTUBE_CLIENT_ID, CLIENT_SECRET tai REFRESH_TOKEN GitHub Secretsistä")
        print("Katso ohje: get_refresh_token.py")
        return None

    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=SCOPES
    )
    
    # Refresh access token
    creds.refresh(Request())
    
    return build("youtube", "v3", credentials=creds)

def upload_video(file_path, title, description, tags, category_id="25", privacy="public"):
    """
    Lataa videon YouTubeen
    category_id 25 = News & Politics (turvallinen)
    privacy: public, private, unlisted
    """
    youtube = get_authenticated_service()
    if not youtube:
        return None

    # Tags for World Viral
    default_tags = ["world viral", "breaking news", "earth today", "nasa", "usgs", "news"]

    body = {
        "snippet": {
            "title": title[:95],  # YouTube max 100
            "description": description + "\n\nSources: USGS, NASA, NOAA, Reuters\n#worldviral #breakingnews #earthtoday",
            "tags": tags + default_tags,
            "categoryId": category_id
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(file_path, chunksize=-1, resumable=True, mimetype="video/mp4")

    print(f"📤 Ladataan YouTubeen: {title}")
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    response = request.execute()
    video_id = response.get("id")
    print(f"✅ Ladattu! https://youtube.com/watch?v={video_id}")
    return video_id

if __name__ == "__main__":
    # Test upload
    upload_video(
        "world_viral_output.mp4",
        "TEST - World Viral Bot",
        "This is a test upload from World Viral automation bot.",
        ["test"]
    )

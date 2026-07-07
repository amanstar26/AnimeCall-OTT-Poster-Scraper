from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from curl_cffi import requests
import re
from datetime import datetime
import base64
import json
from Crypto.Cipher import AES
from Crypto.Hash import MD5

router = APIRouter()

NETFLIX_GRAPHQL_URL = "https://web.prod.cloud.netflix.com/graphql"

def fetch_primary_metadata(video_url: str):
    # Extract video ID from URL
    video_id = re.search(r"/(title|watch)/(\d+)", video_url).group(2)
    print(f"Fetching metadata for Netflix video ID: {video_id}")

    # Base payload (shared for both requests)
    payload = {
        "operationName": "MiniModalQuery",
        "variables": {
            "opaqueImageFormat": "WEBP",
            "transparentImageFormat": "WEBP",
            "videoMerchEnabled": True,
            "fetchPromoVideoOverride": False,
            "hasPromoVideoOverride": False,
            "promoVideoId": 0,
            "videoMerchContext": "BROWSE",
            "isLiveEpisodic": False,
            "artworkContext": {
                "groupLoc": "eyJrLnR5cGUiOiJ3aW5kb3dlZGNvbWluZ3Nvb24iLCJrLnRpbWVXaW5kb3ciOiJuZXh0d2VlayJ9"
            },
            "textEvidenceUiContext": "BOB",
            "unifiedEntityIds": [f"Video:{video_id}"]
        },
        "extensions": {
            "persistedQuery": {
                "id": "96c87721-2e20-416f-aa6f-87c8a889c955",
                "version": 102
            }
        }
    }

    headers = {
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0"
    }

    # ---------- First request: English (default) ----------
    response = requests.post(
        NETFLIX_GRAPHQL_URL,
        headers=headers,
        json=payload,
        timeout=15
    )
    if response.status_code != 200:
        raise Exception(f"Netflix API error (English): {response.status_code}")

    data = response.json()
    content = data["data"]["unifiedEntities"]

    # Extract basic metadata from the first entity (assuming at least one exists)
    # We'll use the first item, but you could also loop to find the correct one
    item = content[0] if content else {}
    title = item.get("title")
    year = item.get("availabilityStartTime", "").split("-")[0]
    landscape = item.get("boxartHighRes", {}).get("url")          # English landscape
    cover = item.get("storyArt", {}).get("url")
    logo = item.get("titleLogoUnbranded", {}).get("url")

    # ---------- Second request: Hindi (hi-in) ----------
    hindi_headers = headers.copy()
    hindi_headers["x-netflix.context.locales"] = "hi-in"

    try:
        hindi_response = requests.post(
            NETFLIX_GRAPHQL_URL,
            headers=hindi_headers,
            json=payload,
            timeout=15
        )
        if hindi_response.status_code == 200:
            hindi_data = hindi_response.json()
            hindi_content = hindi_data["data"]["unifiedEntities"]
            if hindi_content:
                hindi_item = hindi_content[0]
                # Get the Hindi boxart; verify the key contains "|hi" to be safe
                boxart = hindi_item.get("boxartHighRes", {})
                if boxart.get("key") and "|hi" in boxart["key"]:
                    hindi_landscape = boxart.get("url")
                else:
                    # Fallback: still use the URL, but log a warning
                    print("Warning: Hindi boxart key does not contain '|hi'")
                    hindi_landscape = boxart.get("url")
            else:
                hindi_landscape = None
        else:
            print(f"Hindi request failed with status {hindi_response.status_code}")
            hindi_landscape = None
    except Exception as e:
        print(f"Error fetching Hindi landscape: {e}")
        hindi_landscape = None

    # Build return dict with the new key
    return {
        "title": f"{title} - ({year})" if year else title,
        "landscape": landscape,                 # English
        "hindi_landscape": hindi_landscape,     # New key
        "cover": cover,
        "logo": logo
    }

# ---------------- FASTAPI ROUTE ----------------

@router.get("/nf")
def netflix_poster(url: str = Query(..., description="Netflix URL or Title ID")):
    result = fetch_primary_metadata(url)

    if "error" in result:
        return JSONResponse(content=result, status_code=400)

    return result

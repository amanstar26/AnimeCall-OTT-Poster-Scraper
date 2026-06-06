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

PASSWORD = "netflix-metadata-secret-key-2024"


# ---------------- CRYPTO HELPERS ----------------

def evp_bytes_to_key(password: bytes, salt: bytes, key_len: int, iv_len: int):
    dt = b""
    md5_hash = b""
    while len(dt) < key_len + iv_len:
        md5 = MD5.new()
        md5.update(md5_hash + password + salt)
        md5_hash = md5.digest()
        dt += md5_hash
    return dt[:key_len], dt[key_len:key_len + iv_len]


def openssl_decrypt(enc_b64: str, password: str):
    raw = base64.b64decode(enc_b64)

    if raw[:8] != b"Salted__":
        raise ValueError("Invalid OpenSSL data")

    salt = raw[8:16]
    ciphertext = raw[16:]

    key, iv = evp_bytes_to_key(password.encode(), salt, 32, 16)

    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt = cipher.decrypt(ciphertext)

    pad = pt[-1]
    return pt[:-pad].decode("utf-8", errors="ignore")


# ---------------- CORE LOGIC ----------------

def fetch_netflix_metadata(netflix_url: str):
    if "netflix.com" not in netflix_url:
        netflix_url = f"https://www.netflix.com/title/{netflix_url}"

    session = requests.Session(impersonate="chrome")

    api = "https://postersuniverse.pages.dev/api/metadata"

    res = session.get(api, params={"url": netflix_url}, timeout=20)

    if res.status_code != 200:
        return {"error": f"API failed {res.status_code}", "details": res.text}

    try:
        j = res.json()
    except Exception:
        return {"error": "Invalid JSON from API", "raw": res.text}

    enc = j.get("data")
    if not enc:
        return {"error": "Encrypted data missing", "raw": j}

    try:
        decrypted = openssl_decrypt(enc, PASSWORD)
        data = json.loads(decrypted)
    except Exception as e:
        return {"error": "Decrypt failed", "details": str(e)}

    box = data.get("boxarts", {})
    cover,logo = fetch_primary_metadata(data.get("nfid") or data.get("video_id"))
    year = data.get("availability", {}).get("year")
    return {
        "title": f"{data.get('title')} - ({year})" if year else data.get("title"),
        "portrait": box.get("poster_426x607") or box.get("poster_166x236"),
        "cover": cover,
        "logo": logo,
        "landscape": box.get("storyArt_1920x1080"),
    }

NETFLIX_GRAPHQL_URL = "https://web.prod.cloud.netflix.com/graphql"

def fetch_primary_metadata(video_id: str) -> dict:
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

    response = requests.post(
        NETFLIX_GRAPHQL_URL,
        headers=headers,
        json=payload,
        timeout=15
    )

    if response.status_code != 200:
        raise Exception(f"Netflix API error: {response.status_code}")

    data = response.json()
    content = data["data"]["unifiedEntities"]

    for item in content:
        cover = item.get("storyArt", {}).get("url")
        logo = item.get("titleLogoUnbranded", {}).get("url")
        return cover,logo

# ---------------- FASTAPI ROUTE ----------------

@router.get("/nf")
def netflix_poster(url: str = Query(..., description="Netflix URL or Title ID")):
    result = fetch_netflix_metadata(url)

    if "error" in result:
        return JSONResponse(content=result, status_code=400)

    return result

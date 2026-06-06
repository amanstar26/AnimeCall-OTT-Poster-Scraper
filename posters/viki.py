import re
import json
from curl_cffi import requests
from datetime import datetime
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter()

def scrape_viki_api(container_id: str):
    url = f"https://api.viki.io/v4/containers/{container_id}/episodes.json"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "*/*",
        "Accept-Language": "en",
        "Content-Type": "application/json",
        "Origin": "https://www.viki.com",
        "Referer": "https://www.viki.com/",
        "X-Viki-App-Ver": "26.2.3-4.56.0",
    }

    params = {
        "token": "undefined",
        "direction": "desc",
        "with_upcoming": "true",
        "sort": "number",
        "blocked": "true",
        "per_page": 1,
        "app": "100000a",
    }

    r = requests.get(url, headers=headers, params=params, timeout=15)
    r.raise_for_status()

    data = r.json()
    # print(json.dumps(data, indent=2))
    response = data.get("response", [])[0]

    # 🎬 Title
    container = response.get("container", {})
    titles = container.get("titles", {})
    title = titles.get("en")

    # 🖼 Landscape
    images = container.get("images", {})
    landscape = images.get("atv_cover")["url"]

    # 📅 Year
    created_at = response.get("updated_at")
    year = ""
    if created_at:
        try:
            year = datetime.fromisoformat(
                created_at.replace("Z", "")
            ).year
        except Exception:
            pass

    return {
        "title": f"{title} - ({year})",
        "landscape": landscape,
    }

def viki(url: str):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        html = requests.get(url, headers=headers).text

        title = None
        image = None
        year = None

        # ✅ Extract <title>
        title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        if title_match:
            full_title = title_match.group(1)
            title = full_title.split(" |")[0].strip()

        # ✅ Extract from __NEXT_DATA__ block
        json_match = re.search(r'<script[^>]*id=["\']__NEXT_DATA__["\'][^>]*>(.*?)</script>', html, re.DOTALL)
        if json_match:
            json_data = json_match.group(1)

            # ✅ Match atv_cover.url value
            image_match = re.search(r'"atv_cover"\s*:\s*{[^}]*?"url"\s*:\s*"([^"]+)"', json_data)
            if image_match:
                image = image_match.group(1)
            
            year_match = re.search(
                r'"created_at"\s*:\s*"(\d{4})-',
                json_data
            )
            if year_match:
                year = year_match.group(1)

        return {"title": f"{title} - ({year})" if year else title, "landscape": image}
    except json.JSONDecodeError:
        return {"error": "JSON decode error"}

@router.get("/viki")
def viki_poster(url: str = Query(..., description="Viki content URL")):
    if "/movies/" in url:
        result = viki(url)

    # TV / Series URLs
    else:
        container_id = url.rsplit("/")[-1].split("-")[0]
        # print("Extracted container_id:", container_id)
        if not container_id:
            return JSONResponse(
                content={"error": "Invalid Viki URL"},
                status_code=400
            )

        result = scrape_viki_api(container_id)
    
    if "error" in result:
        return JSONResponse(content=result, status_code=400)

    return JSONResponse(content=result, status_code=200)
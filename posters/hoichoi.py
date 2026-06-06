from curl_cffi import requests
import re
from urllib.parse import urlparse, parse_qs
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter()

def clean_hoichoi_url(url: str):
    parsed = urlparse(url)

    query = parse_qs(parsed.query)

    if "permalink" in query:
        permalink = query["permalink"][0]

        if permalink.startswith("/movie/"):
            permalink = permalink.replace("/movie/", "/movies/")
        elif permalink.startswith("/show/"):
            permalink = permalink.replace("/show/", "/shows/")

        return f"https://www.hoichoi.tv{permalink}"

    return url

def hoichoi_content_id(url: str):
    session = requests.Session(impersonate="chrome120")

    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/133.0.0.0 Safari/537.36",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "cookie": "NEXT_LOCALE=en;",
        "RSC": "1",
        "referer": url,
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
    }

    res = session.get(url, headers=headers)
    html = res.text

    match = re.search(r'"contentId"\s*:\s*"([a-f0-9\-]{36})"', html)

    if match:
        return match.group(1)
    else:
        raise Exception("❌ Content ID not found")

def get_api_url(user_url):
    if "/shows/" in user_url:
        return "https://prod-contents-api.hoichoi.dev/contents/api/v1/series", "series"
    elif "/movies/" in user_url:
        return "https://prod-contents-api.hoichoi.dev/contents/api/v1/videos", "movie"
    else:
        raise Exception("❌ Unsupported URL format")


def fetch_hoichoi_data(content_id, api_url):
    params = {
        "platform": "WEB",
        "language": "english",
        "contentIds": content_id
    }

    headers = {
        "accept": "*/*",
        "origin": "https://www.hoichoi.tv",
        "referer": "https://www.hoichoi.tv/",
        "user-agent": "Mozilla/5.0",

        "x-bypass-proxy": "true",
        "x-hoichoi-siteid": "hoichoitv",
    }

    res = requests.get(
        api_url,
        headers=headers,
        params=params,
        impersonate="chrome120"
    )

    if res.status_code != 200:
        raise Exception(f"❌ API Error: {res.status_code}")

    return res.json()

def extract_hoichoi(data, content_type):
    item = data[0]

    title = item.get("title")
    year = item.get("releaseYear")

    landscape = cover = portrait = logo = None

    if content_type == "series":
        season = item.get("seasons", [])[0]
        images = season.get("images", [])

        title_image = season.get("titleImage")
        if title_image:
            logo = title_image.get("imageUrl")

    else:
        images = item.get("images", [])

        if item.get("titleImage"):
            logo = item["titleImage"].get("imageUrl")

    landscape_list = []

    for img in images:
        reso = img.get("resolution")
        img_url = img.get("imageUrl")

        if reso == "16x9":
            landscape_list.append(img_url)

        elif reso == "3x4" and not portrait:
            portrait = img_url

    if len(landscape_list) >= 1:
        landscape = landscape_list[0]

    if len(landscape_list) >= 2:
        cover = landscape_list[1]

    return {
        "title": f"{title} - ({year})",
        "landscape": landscape,
        "cover": cover,
        "portrait": portrait,
        "logo": logo,
    }

def hoichoi_scraper(url):
    # print("🔍 Extracting content ID...")
    content_id = hoichoi_content_id(url)
    # print("✅ Content ID:", content_id)

    api_url, content_type = get_api_url(url)
    # print("🎯 Type:", content_type)

    # print("📡 Fetching API...")
    data = fetch_hoichoi_data(content_id, api_url)

    # print("🎯 Extracting data...")
    result = extract_hoichoi(data, content_type)

    return result


# if __name__ == "__main__":
#     url = "https://www.hoichoi.tv/movies/byomkesh-hotyamancha"
#     print(clean_hoichoi_url(url))
#     result = hoichoi_scraper(clean_hoichoi_url(url))

#     print("\n🔥 FINAL OUTPUT:\n")
#     for k, v in result.items():
#         print(f"{k}: {v}")

@router.get("/hoichoi")
def hoichoi_endpoint(
    url: str = Query(..., description="Hoichoi movie/series URL")
):
    try:
        clean_url = clean_hoichoi_url(url)
        result = hoichoi_scraper(clean_url)
        return JSONResponse(content=result, status_code=200)

    except Exception as e:
        print("❌ Hoichoi error:", e)
        return JSONResponse(
            content={"error": "Failed to fetch data from Hoichoi"},
            status_code=400
        )
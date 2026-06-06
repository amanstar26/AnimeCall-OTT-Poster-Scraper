from curl_cffi import requests
import json
import html
import re
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter()

def amazon_scrap(url: str):
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code != 200:
            return {"title": None, "landscape": None, "portrait": None}

        html_text = html.unescape(r.text)

        posters = {
            "title": None,
            "landscape": None,
            "portrait": None
        }

        title_match = re.search(
            r'<title[^>]*>(.*?)</title>',
            html_text,
            re.IGNORECASE | re.DOTALL
        )
        if title_match:
            raw_title = re.sub(r'\s+', ' ', title_match.group(1)).strip()
            raw_title = re.sub(r'^Prime Video:\s*', '', raw_title, flags=re.I)
            posters["title"] = raw_title

        image_block_match = re.search(
            r'"images"\s*:\s*({.*?})\s*,',
            html_text,
            re.DOTALL
        )

        if image_block_match:
            image_block = image_block_match.group(1)

            covershot_match = re.search(
                r'"covershot"\s*:\s*"([^"]+)"',
                image_block
            )
            packshot_match = re.search(
                r'"packshot"\s*:\s*"([^"]+)"',
                image_block
            )

            if covershot_match:
                posters["landscape"] = covershot_match.group(1)

            if packshot_match:
                posters["portrait"] = packshot_match.group(1)

        return posters
    except json.JSONDecodeError:
        return {"error": "JSON decode error"}

def amazon(url: str):
    api = f"{url}&dvWebAppClientVersion=1.0.120924.0"

    headers = {
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
        "x-requested-with": "WebAppSPA",
        "x-purpose": "navigation",
        "Referer": url,
    }

    r = requests.get(
        api,
        headers=headers,
        timeout=20
    )
    print("Status Code:", r.status_code)
    if r.status_code != 200:
        return amazon_scrap(url)
    data = r.json()
    result = {
        "title": None,
        "landscape": None,
        "portrait": None,
        "cover": None,
        "logo": None,
    }

    try:
        page = data.get("body", [])
        if not page:
            return result

        atf = page.get("atf", {})
        state = atf.get("state", {})
        detail = state.get("detail", {})
        header_detail = detail.get("headerDetail", {})

        # headerDetail key is dynamic (titleID)
        for _, info in header_detail.items():
            result["title"] = info.get("title")
            year = info.get("releaseYear")

            images = info.get("images", {})
            result["landscape"] = images.get("covershot")
            result["portrait"] = images.get("packshot")
            result["cover"] = images.get("heroshot")
            result["logo"] = images.get("titleLogo")
            break

    except Exception as e:
        pass

    # Format title
    if result["title"]:
        result["title"] = f"{result['title']} - ({year})"

    return result

@router.get("/amazon")
def amazon_poster(url: str = Query(..., description="Amazon content URL")):
    result = amazon(url)

    if "error" in result:
        return JSONResponse(content=result, status_code=400)

    return JSONResponse(content=result, status_code=200)

# if __name__ == "__main__":
#     test_url = "https://www.primevideo.com/detail/0LDC8RWW51I5H7Q212ODF5JBAY/ref=atv_sr_fle_c_Tn74RA_1_1_1"
#     print(amazon(test_url))
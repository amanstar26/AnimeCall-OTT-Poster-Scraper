from curl_cffi import requests
import re
import json
import html as html_lib
from urllib.parse import unquote
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter()

def clean_title(text: str) -> str | None:
    text = text.strip()

    # -------- Case 0: Remove "Release Date..." type suffix --------
    pattern0 = r"^(.*?)\s*(?:•|-)\s*(Season\s*\d+).*?Release Date.*"
    match0 = re.search(pattern0, text, re.IGNORECASE)

    if match0:
        title = match0.group(1).strip()
        season = match0.group(2).strip()
        return f"{title} {season}"

    # -------- Case 1: Watch XYZ Movie / TV Show --------
    pattern1 = r"Watch\s+(.*?)\s+(?:TV Show|Full Movie|Movie)"
    match1 = re.search(pattern1, text, re.IGNORECASE)

    if match1:
        return match1.group(1).strip()

    # -------- Case 2: Title (Year) --------
    pattern2 = r"^(.*?)\s*\(\d{4}\)"
    match2 = re.search(pattern2, text)

    if match2:
        title = match2.group(1).strip()
        year = re.search(r"\(\d{4}\)", text)
        return f"{title} {year.group(0)}" if year else title

    return text.strip()

def extract_balanced_json(text, start_pattern):
    """
    Extract balanced JSON object starting from a pattern like '"seo":{'
    """
    match = re.search(start_pattern, text)
    if not match:
        return None

    start = match.end() - 1  # position of first {
    brace_count = 0

    for i in range(start, len(text)):
        if text[i] == "{":
            brace_count += 1
        elif text[i] == "}":
            brace_count -= 1

            if brace_count == 0:
                return text[start:i+1]

    return None


def plex(url):
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.7",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
        "Referer": url,
        "rsc": "1"
    }

    # Optional (only if needed)
    cookies = {
        "NEXT_LOCALE": "no"
    }

    response = requests.get(url, headers=headers, cookies=cookies)
    html = response.text
    result = {}

    # -------- SEO --------
    seo_json = extract_balanced_json(html, r'"seo"\s*:\s*{')
    if seo_json:
        seo_data = json.loads(seo_json)
        title = clean_title(seo_data.get("title"))
        result["title"] = title if title else seo_data.get("title")
        
    # -------- OpenGraph (Landscape) --------
    og_json = extract_balanced_json(html, r'"openGraph"\s*:\s*{')
    if og_json:
        og_data = json.loads(og_json)
        images = og_data.get("images", [])
        if images:
            result["landscape"] = images[0].get("url")

    # -------- StructuredData (Portrait) --------
    structured_json = extract_balanced_json(html, r'"structuredData"\s*:\s*{')
    if structured_json:
        structured_data = json.loads(structured_json)
        graph = structured_data.get("@graph", [])
        if graph:
            result["portrait"] = graph[0].get("image")

    return result

@router.get("/plex")
def plex_poster(url: str = Query(..., description="Plex content URL")):
    result = plex(url)

    if "error" in result:
        return JSONResponse(content=result, status_code=400)

    return JSONResponse(content=result, status_code=200)

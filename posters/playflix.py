from curl_cffi import requests
import re
from urllib.parse import urlparse, urlunparse
import json
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter()

new_domain = "qn-01273-mum-1-06-1---7235-nigq.http.global.dns.qwilted-cds.cqloud.com"

def replace_domain(url, new_domain):
    parsed = urlparse(url)

    return urlunparse((
        parsed.scheme,
        new_domain,
        parsed.path,
        parsed.params,
        parsed.query,
        parsed.fragment
    ))

def extract_title_from_document_title(url):
    html = requests.get(url, timeout=20).text

    match = re.search(
        r'document\.title\s*=\s*"Watch\s+(.*?)\s+Full',
        html,
        re.I
    )

    if not match:
        return "failed to fetch"

    return match.group(1)

def playflix(url):
    title = extract_title_from_document_title(url)
    html = requests.get(url, timeout=20).text

    # -------- FIND IMAGES --------
    match = re.search(
        r'https?://[^\s"\']*(1500|333)\.jpg',
        html,
        re.I
    )

    match1 = re.search(
        r'https?://[^\s"\']*(1280|1080)\.jpg',
        html,
        re.I
    )

    if not match or not match1:
        return "failed to fetch"

    portrait = replace_domain(match.group(0), new_domain)
    landscape = replace_domain(match1.group(0), new_domain)

    # -------- REMOVE EpX FROM LANDSCAPE --------
    landscape = re.sub(r'_Ep\d+', '', landscape, flags=re.I)

    # -------- BUILD PORTRAIT FROM CLEAN LANDSCAPE --------
    portrait = (
        landscape
        .replace("1080", "1500")
        .replace("1280", "333")
    )

    # -------- KEYWORD VALIDATION --------
    keyword = title.split(" ")[0].lower()

    if keyword not in landscape.lower():
        landscape = portrait.replace("1500", "1080").replace("333", "1280")

    if keyword not in portrait.lower():
        portrait = landscape.replace("1080", "1500").replace("1280", "333")

    return {
        "title": title,
        "landscape": landscape,
        "portrait": portrait
    }

@router.get("/playflix")
def playflix_poster(url: str = Query(..., description="Playflix Content Url")):
    result = playflix(url)
    if "error" in result:
        return JSONResponse(content=result, status_code=400)
    return JSONResponse(content=result, status_code=200)
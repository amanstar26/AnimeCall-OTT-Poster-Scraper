# 🎬 AnimeCall Posters API — Multi-OTT Poster Scraper

A fast, modular **FastAPI** service that extracts **title, landscape, portrait, cover, logo, and thumbnails** from major OTT platforms using lightweight scraping and JSON parsing.

Built for automation, & bots that need **clean poster assets** from content URLs.

---

## 🚀 Supported Platforms

- Aha
- Aaonxt
- Addatimes
- Airtel Xstream
- Amazon Prime Video
- AppleTV
- Atrangii
- BookMyShow
- Chaupal
- Crunchyroll
- Dangal
- Erosnow
- Hoichoi
- Hulu
- Hungama
- iQIYI
- Jojo App
- Lionsgate Play
- Mubi
- MX Player
- Netflix
- Plex TV
- Playflix
- SaiNaPlay
- Shemaroo
- SonyLiv
- Sunnxt
- Tata Play
- TicketNew
- Tubi
- Ultraplay
- Ultrajhakaas
- Viki
- Viu
- Vivamax
- WeTV
- Youku
- YouTube
- ZEE5

---

## ✨ Features

- 🔐 Token-protected API
- 🧩 Modular router per platform
- 🖼️ Extracts **maximum quality posters**
- ⚡ Pure regex + JSON parsing (no browser, no Selenium)
- 🧠 Smart fallbacks for layout changes
- 🧪 CLI-testable scrapers
- 🤖 Bot-friendly JSON responses

---

## 📦 Project Structure
```bash
animecall-poster/
│
├── main.py
├── auth.py
├── posters/
│ ├── aaonxt.py
│ ├── addatimes.py
│ ├── aha.py
│ ├── airtel.py
│ ├── amz.py
│ ├── appletv.py
│ ├── atrangii.py
│ ├── bms.py
│ ├── chaupal.py
│ ├── crunchyroll.py
│ ├── dangal.py
│ ├── eros.py
│ ├── hoichoi.py
│ ├── hulu.py
│ ├── hungama.py
│ ├── iqyi.py
│ ├── jojo.py
│ ├── lionsgate.py
│ ├── mubi.py
│ ├── mxplayer.py
│ ├── nf.py
│ ├── playflix.py
│ ├── plextv.py
│ ├── sainaplay.py
│ ├── shemaroo.py
│ ├── sonyliv.py
│ ├── sunnxt.py
│ ├── tataplay.py
│ ├── ticketnew.py
│ ├── tubi.py
│ ├── ultra.py
│ ├── ultrajhakaas.py
│ ├── viki.py
│ ├── viu.py
│ ├── vivamax.py
│ ├── wetv.py
│ ├── youku.py
│ ├── yt.py
│ └── zee5.py
```
---

## ⚙️ Installation

```bash
git clone https://github.com/amanstar26/animecall-poster.git
cd animecall-poster
```

Install Requirements:
```bash
pip install -r requirements.txt
```

Run the server:
```bash 
uvicorn main:app --reload
```

## 🔑 Authentication

All /posters/* routes are protected.

Send token in headers:
```bash
Authorization: Bearer YOUR_API_TOKEN
```

Token verification logic is implemented in auth.py.

## 🌐 API Usage

### Example: MX Player
```bash
GET /posters/mxplayer?url=https://www.mxplayer.in/show/...
```
### Example: YouTube
```bash 
GET /posters/youtube?url=https://www.youtube.com/watch?v=VIDEO_ID
```

## ✅ Sample JSON Response
```bash
{
  "title": "The Secret Of Love",
  "landscape": "https://example.com/landscape_3840x2160.jpg",
  "portrait": "https://example.com/portrait_640x960.jpg",
  "logo": "https://example.com/logo.png"
}
```
## 🧪 Local Testing (CLI)

Each scraper can be tested independently:
```bash
python posters/mxplayer.py "https://www.mxplayer.in/show/..."
```
## 🛠️ Tech Stack

1. FastAPI
2. Requests / Custom HTTP client
3. Regex + JSON parsing
4. No headless browser
5. No Selenium

## 🎯 Use Cases

1. Telegram / Discord bots
2. Media automation
3. Poster scraping
4. OTT metadata extraction
5. Content cataloging systems

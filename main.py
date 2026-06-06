from fastapi import FastAPI, Depends
from auth import verify_token

from posters.crunchyroll import router as crunchy_router
from posters.bms import router as bms_router
from posters.nf import router as nf_router
from posters.iqyi import router as iq_router
from posters.mxplayer import router as mx_router
from posters.amz import router as amz_router
from posters.airtel import router as airtel_router
from posters.zee5 import router as zee5_router
from posters.ultra import router as ultra_router
from posters.yt import router as yt_router
from posters.viki import router as viki_router
from posters.youku import router as youku_router
from posters.wetv import router as wetv_router
from posters.hulu import router as hulu_router
from posters.ticketnew import router as ticketnew_router
from posters.sonyliv import router as sonyliv_router
from posters.shemaroo import router as shemaroo_router
from posters.appletv import router as apple_router
from posters.chaupal import router as chaupal_router
from posters.aha import router as aha_router
from posters.vivamax import router as viva_router
from posters.plextv import router as plex_router
from posters.atrangii import router as atrangii_router
from posters.sunnxt import router as sunnxt_router
from posters.playflix import router as playflix_router
from posters.lionsgate import router as lionsgate_router
from posters.eros import router as erosnow_router
from posters.hungama import router as hungama_router
from posters.hoichoi import router as hoichoi_router
from posters.jojo import router as jojo_router
from posters.ultrajhakaas import router as ultrajhakaas_router
from posters.mubi import router as mubi_router
from posters.sainaplay import router as splay_router
from posters.addatimes import router as adda_router
from posters.aaonxt import router as aaonxt_router
from posters.viu import router as viu_router
from posters.dangal import router as dangal_router
from posters.tataplay import router as tataplay_router
from posters.tubi import router as tubi_router

app = FastAPI(title="AnimeCall Botz Posters API", version="1.0")

poster_routers = [
    crunchy_router,
    bms_router,
    nf_router,
    iq_router,
    mx_router,
    amz_router,
    airtel_router,
    zee5_router,
    ultra_router,
    yt_router,
    viki_router,
    youku_router,
    wetv_router,
    hulu_router,
    ticketnew_router,
    sonyliv_router,
    shemaroo_router,
    apple_router,
    chaupal_router,
    aha_router,
    viva_router,
    plex_router,
    atrangii_router,
    sunnxt_router,
    playflix_router,
    lionsgate_router,
    erosnow_router,
    hungama_router,
    hoichoi_router,
    jojo_router,
    ultrajhakaas_router,
    mubi_router,
    splay_router,
    adda_router,
    aaonxt_router,
    viu_router,
    dangal_router,
    tataplay_router,
    tubi_router
]

for router in poster_routers:
    app.include_router(
        router,
        prefix="/posters",
        tags=["Posters"],
        dependencies=[Depends(verify_token)]
    )

@app.get("/")
def home():
    return {"message": "🎬 Welcome to AnimeCall Posters API"}

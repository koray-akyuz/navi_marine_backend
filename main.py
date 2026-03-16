from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from api.v1 import spatial as api_v1_spatial_router
from api.v1 import reports as api_v1_reports_router
from api.v1 import weather as api_v1_weather_router
from api.v1 import auth as api_v1_auth_router
from api.v1 import fish as api_v1_fish_router
from api.v1 import tracks as api_v1_tracks_router

app = FastAPI(title="Vira Bismillah API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API v1 Routers
app.include_router(api_v1_spatial_router.router, prefix="/api/v1/spatial", tags=["spatial"])
app.include_router(api_v1_reports_router.router, prefix="/api/v1/reports", tags=["reports"])
app.include_router(api_v1_weather_router.router, prefix="/api/v1/weather", tags=["weather"])
app.include_router(api_v1_auth_router.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(api_v1_fish_router.router, prefix="/api/v1/fish", tags=["fish"])
app.include_router(api_v1_tracks_router.router, prefix="/api/v1/tracks", tags=["tracks"])

@app.get("/")
async def root():
    return {"message": "Vira Bismillah! Navi Marine Backend çalışıyor."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
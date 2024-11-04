from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.endpoints import image_detection, video_detection, skin_passport, real_time_detection
from backend.core.logger import logger
from backend.models.yolonas import YOLONAS

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting MoleScane API...")
    app.state.model = YOLONAS()
    yield
    logger.info("Shutting down MoleScane API...")

app = FastAPI(
    title="MoleScane API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(image_detection.router, prefix="/api/image")
app.include_router(video_detection.router, prefix="/api/video")
app.include_router(skin_passport.router, prefix="/api/skin")
app.include_router(real_time_detection.router, prefix="/api/realTimeVideo")

@app.get("/")
async def root():
    return {"message": "Welcome to the main API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
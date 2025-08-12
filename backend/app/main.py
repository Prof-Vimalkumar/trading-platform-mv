from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from app.routers import health, stocks

load_dotenv()

app = FastAPI(title="Trading Platform MVP API", version="0.1.0")

# Allow frontend requests during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(stocks.router)

@app.get("/version")
def version():
    return {
        "version": os.getenv("APP_VERSION", "0.1.0"),
        "env": os.getenv("APP_ENV", "dev")
    }

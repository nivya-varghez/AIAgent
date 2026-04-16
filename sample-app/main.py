import os
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Sample Containerized App", version="1.0.0")


class AppInfo(BaseModel):
    app_name: str
    version: str
    environment: str
    message: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/info", response_model=AppInfo)
def info() -> AppInfo:
    return AppInfo(
        app_name=os.getenv("APP_NAME", "sample-containerized-app"),
        version=os.getenv("APP_VERSION", "1.0.0"),
        environment=os.getenv("APP_ENV", "dev"),
        message="Sample containerized application is running.",
    )


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "Welcome to the sample containerized application",
        "docs": "/docs",
        "health": "/health",
        "info": "/info",
    }

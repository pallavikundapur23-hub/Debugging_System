import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.webhook.github_webhook import router as github_webhook_router
from app.utils.logger import configure_logging

LOG_DIR = BASE_DIR / "logs"
configure_logging(LOG_DIR / "workflow.log")

app = FastAPI(title="Autonomous GitHub Issue Remediation")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(github_webhook_router)

@app.get("/")
def health_check():
    return {"status": "ok", "service": "autonomous-remediation"}

# pyright: reportMissingImports=false
import sys
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# Allow Python to find files inside ml/
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT / "ml"))

from security_engine_v2 import analyze_url


app = FastAPI(
    title="PhishGuard API",
    description="Explainable phishing URL detection API",
    version="1.0.0"
)


# Allow Chrome Extension to communicate with the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class URLRequest(BaseModel):
    url: str


@app.get("/")
def root():
    return {
        "message": "PhishGuard API is running"
    }


@app.post("/analyze")
def analyze(request: URLRequest):
    return analyze_url(request.url)
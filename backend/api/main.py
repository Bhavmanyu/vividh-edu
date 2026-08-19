"""
IndiaLens Backend — FastAPI Application
Week 3: ML model loading at startup, new ML management router
"""
import logging
import os
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import uvicorn
import sentry_sdk

from .routers import colleges, analyze, admin, scrape, external as external_router, ai as ai_router
from .db.database import init_db
from .config import settings

logger = logging.getLogger(__name__)

if os.getenv('SENTRY_DSN'):
    sentry_sdk.init(dsn=os.getenv('SENTRY_DSN'), traces_sample_rate=0.1)

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="IndiaLens API",
    description="India's quantitative education and career intelligence platform — backend API",
    version="2.0.0-week3",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS — allow Next.js dev server and production domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        os.getenv('FRONTEND_URL', 'http://localhost:3000'),
        "https://indialens.in",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    """
    Startup sequence:
    1. Init DB connection pool
    2. Warm-up ML models (lazy-loaded but cached on first call)
    """
    await init_db()

    # Warm up XGBoost predictor (trains from seed if no artifact exists)
    try:
        from ..ml.salary_predictor import get_predictor
        predictor = get_predictor(settings.current_model_version)
        logger.info(f"[Startup] XGBoost loaded — {len(predictor.models)} horizon models")
    except Exception as e:
        logger.warning(f"[Startup] XGBoost warmup skipped: {e}")

    # Warm up LSTM (may use compound growth fallback)
    try:
        from ..ml.lstm_trajectory import get_lstm_model
        lstm = get_lstm_model(settings.current_model_version)
        logger.info(f"[Startup] LSTM loaded — torch_available={lstm._torch_available}")
    except Exception as e:
        logger.warning(f"[Startup] LSTM warmup skipped: {e}")

    # Warm up BERT NER extractor
    try:
        from ..ml.salary_ner import get_ner_extractor
        ner = get_ner_extractor()
        logger.info(f"[Startup] NER extractor — bert={ner._bert_available}")
    except Exception as e:
        logger.warning(f"[Startup] NER warmup skipped: {e}")

    logger.info("[Startup] IndiaLens API ready")


@app.get("/health")
async def root_health():
    return {"status": "ok", "version": "1.0.0", "timestamp": datetime.utcnow().isoformat()}


@app.get("/api/health")
async def health():
    """Health check — used by Docker and load balancer."""
    try:
        from ..ml.salary_predictor import get_predictor
        predictor = get_predictor(settings.current_model_version)
        ml_status = "ready" if predictor.models else "seed_only"
    except Exception:
        ml_status = "unavailable"

    return {
        "status": "ok",
        "version": "2.0.0-week3",
        "model_version": settings.current_model_version,
        "ml_status": ml_status,
        "db": "connected",
    }


# ── Mount routers ────────────────────────────────────────────────────
app.include_router(colleges.router, prefix="/api",          tags=["colleges"])
app.include_router(analyze.router,  prefix="/api",          tags=["analyze"])
app.include_router(admin.router,    prefix="/api/admin",    tags=["admin"])
app.include_router(scrape.router,   prefix="/api/scrape",   tags=["scrape"])
app.include_router(external_router.router, prefix="/api/v1", tags=["external"])
app.include_router(ai_router.router,       prefix="/api/v1", tags=["ai"])

# Week 3: ML management endpoints
try:
    from .routers import ml as ml_router
    app.include_router(ml_router.router, prefix="/api/ml", tags=["ml"])
    logger.info("[Main] ML router mounted at /api/ml")
except Exception as e:
    logger.warning(f"[Main] ML router not mounted: {e}")


if __name__ == "__main__":
    uvicorn.run("backend.api.main:app", host="0.0.0.0", port=8000, reload=True)

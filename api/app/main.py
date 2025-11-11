import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from .database.db import engine
from .routers.article_router import router as article_router
from .config.logging_config import configure_logging
from .config.settings import settings


if settings.sentry_dsn:
    sentry_sdk.init(dsn=settings.sentry_dsn, traces_sample_rate=settings.sentry_traces_sample_rate)

configure_logging(settings.log_level)

app = FastAPI(title="News API", version="0.1.0")

origins = settings.cors_origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/health/ready")
def health_ready():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception:
        return {"status": "degraded"}


# App routers
app.include_router(article_router)

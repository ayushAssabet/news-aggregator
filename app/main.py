import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from .database.db import engine
from .database.base import Base
from .api.article_router import router as article_router
from .api.auth_router import router as auth_router
from .api.user_preference_router import router as user_preference_router
from .config.logging_config import configure_logging
from .config.settings import settings
from .middleware.auth_middleware import AuthMiddleware


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
app.add_middleware(AuthMiddleware)


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


# Optional: create tables automatically in environments where migrations aren't run
if settings.enable_auto_create_tables:
    try:
        Base.metadata.create_all(bind=engine)
    except Exception:
        # Don't block app startup if this fails; rely on migrations otherwise
        pass


# App routers
app.include_router(article_router)
app.include_router(auth_router)
app.include_router(user_preference_router)

# Optional dev-only auto table creation
if settings.enable_auto_create_tables:
    try:
        # Import models to populate metadata
        from .database.base import Base  # type: ignore
        import app.models  # noqa: F401
        Base.metadata.create_all(engine)
    except Exception:
        pass

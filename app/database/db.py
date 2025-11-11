from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..config.settings import settings


_engine_kwargs = dict(pool_pre_ping=True, future=True)
if settings.database_url.startswith("postgres"):
    _engine_kwargs.update(pool_size=settings.db_pool_size, max_overflow=settings.db_max_overflow)
engine = create_engine(settings.database_url, **_engine_kwargs)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

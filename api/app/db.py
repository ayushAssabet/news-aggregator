import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
DATABASE_URL=os.getenv('DATABASE_URL','sqlite:///./app.db')
engine=create_engine(DATABASE_URL, pool_pre_ping=True, future=True)
SessionLocal=sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

def get_db():
    from contextlib import contextmanager
    @contextmanager
    def _s():
        db=SessionLocal()
        try:
            yield db
        finally:
            db.close()
    return _s()

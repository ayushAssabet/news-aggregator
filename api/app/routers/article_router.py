from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid

from ..database.db import get_db
from ..database.schemas import ArticleCreate, ArticleRead
from ..controllers import article_controller


router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("/", response_model=list[ArticleRead])
def list_articles(limit: int = 50, offset: int = 0, db: Session = Depends(get_db)):
    return article_controller.list_articles(db, limit=limit, offset=offset)


@router.post("/", response_model=ArticleRead)
def create_article(payload: ArticleCreate, db: Session = Depends(get_db)):
    try:
        return article_controller.create_article(db, payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{article_id}", response_model=ArticleRead)
def get_article(article_id: uuid.UUID, db: Session = Depends(get_db)):
    item = article_controller.get_article(db, article_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    return item

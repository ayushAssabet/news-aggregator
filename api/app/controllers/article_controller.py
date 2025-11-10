from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..schemas import ArticleCreate, ArticleRead
from ..db import get_db
from ..services import article_service
import uuid


router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("/", response_model=list[ArticleRead])
def list_articles(limit: int = 50, offset: int = 0, db: Session = Depends(lambda: next(get_db()))):
    return article_service.list_articles(db, limit=limit, offset=offset)


@router.post("/", response_model=ArticleRead)
def create_article(payload: ArticleCreate, db: Session = Depends(lambda: next(get_db()))):
    try:
        return article_service.create_article(db, payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{article_id}", response_model=ArticleRead)
def get_article(article_id: uuid.UUID, db: Session = Depends(lambda: next(get_db()))):
    item = article_service.get_article(db, article_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    return item

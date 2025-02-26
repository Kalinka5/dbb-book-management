from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from typing import List

from .. import models, schemas
from ..database import get_db
from ..auth.utils import get_current_user
from ..auth.schemas import User

router = APIRouter()


@router.post("/", response_model=schemas.Author,
             summary="Create a new author",
             description="""
## ✍️ Create a new author with:

- #### 👤 **name**: Author's full name (must be unique);
- #### 📅 **birthdate**: Author's date of birth (YYYY-MM-DD).

### ⚠️ The birthdate cannot be in the future.
### 🔐 Requires authentication.
""",
             response_description="The created author details"
             )
async def create_author(
    author: schemas.AuthorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if author with same name exists
    db_author = db.query(models.Author).filter(
        models.Author.name == author.name).first()
    if db_author:
        raise HTTPException(status_code=400, detail="Author already exists")

    db_author = models.Author(**author.model_dump())
    db.add(db_author)
    db.commit()
    db.refresh(db_author)
    return db_author


@router.get("/{author_id}/books", response_model=List[schemas.Book],
            summary="Get author's books",
            description="""
## 📚 Retrieve all books written by a specific author:

- #### 📖 Returns full book details;
- #### 📅 Ordered by publication date;
- #### ✅ Includes availability status.

### 🔑 Requires a valid author ID.
""",
            response_description="List of author's books"
            )
async def get_author_books(
    author_id: int,
    db: Session = Depends(get_db)
):
    author = db.query(models.Author).filter(
        models.Author.id == author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    return author.books

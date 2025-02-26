from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from typing import List

from datetime import datetime

from .. import models, schemas
from ..database import get_db
from ..auth.utils import get_current_user
from ..auth.schemas import User

router = APIRouter()


@router.get("/", response_model=List[schemas.Book],
            summary="Get all books",
            description="""
## 📚 Get a list of books with pagination and sorting options:

#### 📖 **skip**: Number of records to skip (default: 0);
#### 📖 **limit**: Maximum number of records to return (default: 10, max: 100);
#### 📖 **sort_by**: Sort by field (title, author, or publish_date).

### 🔍 Returns a list of books ordered by the specified field.
""",
            response_description="List of books"
            )
def get_books(
    db: Session = Depends(get_db),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = Query("title", pattern="^(title|author|publish_date)$")
):
    query = db.query(models.Book)

    if sort_by == "title":
        query = query.order_by(models.Book.title)
    elif sort_by == "author":
        query = query.join(models.Author).order_by(models.Author.name)
    elif sort_by == "publish_date":
        query = query.order_by(models.Book.publish_date)

    return query.offset(offset).limit(limit).all()


@router.post("/", response_model=schemas.Book,
             summary="Create a new book",
             description="""
## 📕 Create a new book with the following details:

#### 📖 **title**: Book title;
#### 📖 **isbn**: 13-digit ISBN number;
#### 📖 **publish_date**: Publication date (YYYY-MM-DD);
#### 📖 **author_id**: ID of the existing author;
#### 📖 **genre_ids**: List of genre IDs;
#### 📖 **publisher_id**: ID of the existing publisher.

### ⚠️ The publish date cannot be in the future.
""",
             response_description="The created book details"
             )
def create_book(
    book: schemas.BookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Validate ISBN uniqueness
    existing_isbn = db.query(models.Book).filter(
        models.Book.isbn == book.isbn).first()
    if existing_isbn:
        raise HTTPException(
            status_code=400, detail="Book with this ISBN already exists"
        )

    # Validate Publish Date
    if book.publish_date > datetime.now().date():
        raise HTTPException(
            status_code=400, detail="Publish date cannot be in the future"
        )

    # Validate author exists
    author = db.query(models.Author).filter(
        models.Author.id == book.author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    # Validate publisher exists
    publisher = db.query(models.Publisher).filter(
        models.Publisher.id == book.publisher_id).first()
    if not publisher:
        raise HTTPException(status_code=404, detail="Publisher not found")

    # Create book without genres first
    book_data = book.model_dump(exclude={'genre_ids'})
    db_book = models.Book(**book_data)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)

    # Add genres
    for genre_id in book.genre_ids:
        genre = db.query(models.Genre).filter(
            models.Genre.id == genre_id).first()
        if not genre:
            raise HTTPException(
                status_code=404, detail=f"Genre {genre_id} not found")
        book_genre = models.BookGenre(book_id=db_book.id, genre_id=genre_id)
        db.add(book_genre)

    db.commit()
    db.refresh(db_book)

    return db_book


@router.get("/{book_id}/history", response_model=List[schemas.Borrowing],
            summary="Get book borrowing history",
            description="""
## 📖 Retrieve the complete borrowing history of a specific book:

#### 📅 Shows all past and current borrowings;
#### 👤 Includes borrower names and dates;
#### 🔄 Ordered by borrow date.

### 🔐 Requires authentication.
""",
            response_description="List of borrowing records"
            )
def get_book_history(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book.borrowing_history

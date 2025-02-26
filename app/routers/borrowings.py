from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from datetime import datetime, UTC
from ..auth.utils import get_current_user
from ..auth.schemas import User

router = APIRouter()

MAX_BOOKS_PER_BORROWER = 3  # Configure as needed


@router.post("/borrow", response_model=schemas.Borrowing,
             summary="Borrow a book",
             description="""
## 📖 Create a new borrowing record:

- #### 📚 **book_id**: ID of the book to borrow;
- #### 👤 **borrower_name**: Name of the person borrowing the book.

### ⚠️ Conditions:
- #### 📌 Book must be available (not currently borrowed)
- #### 📌 Borrower cannot have more than 3 books at a time

### 🔐 Requires authentication.
""",
             response_description="The created borrowing record"
             )
async def borrow_book(
    borrowing: schemas.BorrowingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if book exists and is available
    book = db.query(models.Book).filter(
        models.Book.id == borrowing.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if not book.is_available:
        raise HTTPException(status_code=400, detail="Book is not available")

    # Check borrower's current borrowed books
    active_borrows = db.query(models.BorrowingHistory).filter(
        models.BorrowingHistory.borrower_name == borrowing.borrower_name,
        models.BorrowingHistory.return_date == None
    ).count()

    if active_borrows >= MAX_BOOKS_PER_BORROWER:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot borrow more than {MAX_BOOKS_PER_BORROWER} books"
        )

    # Create borrowing record
    db_borrowing = models.BorrowingHistory(**borrowing.model_dump())
    book.is_available = False

    db.add(db_borrowing)
    db.commit()
    db.refresh(db_borrowing)
    return db_borrowing


@router.post("/return/{borrowing_id}", response_model=schemas.Borrowing,
             summary="Return a borrowed book",
             description="""
## 📚 Return a borrowed book:

- #### 📅 Updates the return date;
- #### ✅ Makes the book available for new borrowings.

### ⚠️ Requires:
- #### 🔑 Valid borrowing ID
- #### 📖 Book must be currently borrowed (not already returned)

### 🔐 Requires authentication.
""",
             response_description="The updated borrowing record"
             )
async def return_book(
    borrowing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    borrowing = db.query(models.BorrowingHistory).filter(
        models.BorrowingHistory.id == borrowing_id
    ).first()

    if not borrowing:
        raise HTTPException(
            status_code=404, detail="Borrowing record not found")
    if borrowing.return_date:
        raise HTTPException(status_code=400, detail="Book already returned")

    borrowing.return_date = datetime.now(UTC)
    borrowing.book.is_available = True

    db.commit()
    db.refresh(borrowing)
    return borrowing

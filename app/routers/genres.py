from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..database import get_db
from ..auth.utils import get_current_user
from ..auth.schemas import User

router = APIRouter()


@router.get("/", response_model=List[schemas.Genre],
            summary="Get all genres",
            description="""
## 📚 Get a list of all available book genres.

- #### Returns a list of genres with their IDs and names;
- #### Can be used for book categorization;
- #### Supports pagination.

### No authentication required.
""",
            response_description="List of genres"
            )
def get_genres(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    return db.query(models.Genre).offset(skip).limit(limit).all()


@router.post("/", response_model=schemas.Genre,
             summary="Create a new genre",
             description="""
## 📚 Create a new book genre.

- #### 📚 **name**: Unique genre name;
- #### 📚 **Name** must not already exist in the system.

### 🔐 Requires authentication.
""",
             response_description="Created genre information"
             )
def create_genre(
    genre: schemas.GenreCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if genre with same name exists
    db_genre = db.query(models.Genre).filter(
        models.Genre.name == genre.name).first()
    if db_genre:
        raise HTTPException(status_code=400, detail="Genre already exists")

    db_genre = models.Genre(**genre.model_dump())
    db.add(db_genre)
    db.commit()
    db.refresh(db_genre)
    return db_genre

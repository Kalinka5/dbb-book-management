from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..database import get_db
from ..auth.utils import get_current_user
from ..auth.schemas import User

router = APIRouter()


@router.get("/", response_model=List[schemas.Publisher],
            summary="Get all publishers",
            description="""
## 📚 Get a list of all book publishers.

- #### Returns publisher details including name and established year;
- #### Supports pagination;
- #### Can be filtered by established year.

### 🔐 No authentication required.
""",
            response_description="List of publishers"
            )
def get_publishers(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    return db.query(models.Publisher).offset(skip).limit(limit).all()


@router.post("/", response_model=schemas.Publisher,
             summary="Create a new publisher",
             description="""
## 📚 Create a new book publisher.

- #### **name**: Unique publisher name;
- #### **established_year**: Year when publisher was established;
- #### **Name** must not already exist in the system.

### 🔐 Requires authentication.
""",
             response_description="Created publisher information"
             )
def create_publisher(
    publisher: schemas.PublisherCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if publisher with same name exists
    db_publisher = db.query(models.Publisher).filter(
        models.Publisher.name == publisher.name
    ).first()
    if db_publisher:
        raise HTTPException(status_code=400, detail="Publisher already exists")

    db_publisher = models.Publisher(**publisher.model_dump())
    db.add(db_publisher)
    db.commit()
    db.refresh(db_publisher)
    return db_publisher

from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import date, datetime
from typing import Optional, List


class AuthorBase(BaseModel):
    name: str
    birthdate: date

    @field_validator('birthdate')
    def birthdate_not_in_future(cls, v):
        if v > date.today():
            raise ValueError('Birthdate cannot be in the future')
        return v


class AuthorCreate(AuthorBase):
    pass


class Author(AuthorBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class BookBase(BaseModel):
    title: str
    # Must be exactly 13 digits
    isbn: int = Field(ge=1000000000000, le=9999999999999)
    publish_date: date
    author_id: int
    genre_ids: List[int]
    publisher_id: int

    @field_validator('isbn')
    def validate_isbn(cls, v):
        if len(str(v)) != 13:
            raise ValueError('ISBN must be exactly 13 digits')
        return v

    @field_validator('publish_date')
    def publish_date_not_in_future(cls, v):
        if v > date.today():
            raise ValueError('Publish date cannot be in the future')
        return v


class BookCreate(BookBase):
    pass


class Book(BookBase):
    id: int
    is_available: bool

    @classmethod
    def model_validate(cls, obj):
        # Create a dict with all the data
        data = {
            "id": obj.id,
            "title": obj.title,
            "isbn": obj.isbn,
            "publish_date": obj.publish_date,
            "author_id": obj.author_id,
            "publisher_id": obj.publisher_id,
            "is_available": obj.is_available,
            "genre_ids": obj.genre_ids
        }
        return cls(**data)

    model_config = ConfigDict(from_attributes=True)


class GenreBase(BaseModel):
    name: str


class GenreCreate(GenreBase):
    pass


class Genre(GenreBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class PublisherBase(BaseModel):
    name: str
    established_year: int

    @field_validator('established_year')
    def year_not_in_future(cls, v):
        if v > datetime.now().year:
            raise ValueError('Established year cannot be in the future')
        return v


class PublisherCreate(PublisherBase):
    pass


class Publisher(PublisherBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class BorrowingBase(BaseModel):
    book_id: int
    borrower_name: str


class BorrowingCreate(BorrowingBase):
    pass


class Borrowing(BorrowingBase):
    id: int
    borrow_date: datetime
    return_date: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)

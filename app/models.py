from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, UTC
from .database import Base
from .auth.models import User  # Import User model


class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    birthdate = Column(Date)
    books = relationship("Book", back_populates="author")


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    isbn = Column(Integer, unique=True, index=True)
    publish_date = Column(Date)
    author_id = Column(Integer, ForeignKey("authors.id"))
    genres = relationship("BookGenre", back_populates="book")
    publisher_id = Column(Integer, ForeignKey("publishers.id"))
    is_available = Column(Boolean, default=True)

    author = relationship("Author", back_populates="books")
    publisher = relationship("Publisher", back_populates="books")
    borrowing_history = relationship("BorrowingHistory", back_populates="book")

    @property
    def genre_ids(self) -> list[int]:
        return [genre.genre_id for genre in self.genres]


class BookGenre(Base):
    __tablename__ = "book_genres"

    book_id = Column(Integer, ForeignKey("books.id"), primary_key=True)
    genre_id = Column(Integer, ForeignKey("genres.id"), primary_key=True)

    book = relationship("Book", back_populates="genres")
    genre = relationship("Genre", back_populates="books")


class Genre(Base):
    __tablename__ = "genres"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    books = relationship("BookGenre", back_populates="genre")


class Publisher(Base):
    __tablename__ = "publishers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    established_year = Column(Integer)
    books = relationship("Book", back_populates="publisher")


class BorrowingHistory(Base):
    __tablename__ = "borrowing_history"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"))
    borrower_name = Column(String)
    borrow_date = Column(DateTime, default=lambda: datetime.now(UTC))
    return_date = Column(DateTime, nullable=True)

    book = relationship("Book", back_populates="borrowing_history")

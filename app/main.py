from fastapi import FastAPI
from .database import engine
from . import models
from .routers import books, authors, borrowings, genres, publishers
from .auth.router import router as auth_router

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Library Management System API")

app.include_router(auth_router, tags=["authentication"])
app.include_router(books.router, prefix="/books", tags=["books"])
app.include_router(authors.router, prefix="/authors", tags=["authors"])
app.include_router(borrowings.router, tags=["borrowings"])
app.include_router(genres.router, prefix="/genres", tags=["genres"])
app.include_router(publishers.router, prefix="/publishers",
                   tags=["publishers"])

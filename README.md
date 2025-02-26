# Library Management System API

A FastAPI-based Library Management System with support for books, authors, genres, publishers, and borrowing management.

## 🚀 Quick Start

1. Clone the repository:

```bash
git clone https://github.com/Kalinka5/dbb-book-management.git
cd dbb-book-management
```

2. Create and activate virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the application:

```bash
uvicorn app.main:app --reload
```

## 📚 API Documentation

Access the interactive API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔑 Authentication

The API uses JWT token authentication:

1. Create a user account: `POST /users/`
2. Get access token: `POST /token`
3. Use the token in the Authorization header: `Bearer <token>`

## 📖 API Endpoints

### Authentication

- `POST /token` - Get access token (OAuth2)
  - Required fields: username, password
  - Returns JWT token valid for 30 minutes
- `POST /users/` - Create new user
  - Required fields: username, password
  - Username must be unique

### Books

- `GET /books/` - List all books
  - Supports pagination (skip, limit)
  - Sorting by title, author, or publish_date
  - Optional authentication
- `POST /books/` - Create a new book
  - Requires authentication
  - Required fields: title, isbn (13 digits), publish_date, author_id, genre_ids, publisher_id
  - Validates ISBN format and publish date
- `GET /books/{id}/history` - Get book borrowing history
  - Requires authentication
  - Shows all past and current borrowings

### Authors

- `GET /authors/` - List all authors
  - Supports pagination
  - Optional authentication
- `POST /authors/` - Create a new author
  - Requires authentication
  - Required fields: name (unique), birthdate
  - Validates birthdate not in future
- `GET /authors/{id}/books` - List author's books
  - Shows all books by specific author
  - Includes availability status

### Genres

- `GET /genres/` - List all genres
  - Supports pagination
  - Optional authentication
- `POST /genres/` - Create a new genre
  - Requires authentication
  - Required field: name (unique)

### Publishers

- `GET /publishers/` - List all publishers
  - Supports pagination
  - Optional authentication
- `POST /publishers/` - Create a new publisher
  - Requires authentication
  - Required fields: name (unique), established_year
  - Validates established_year not in future

### Borrowing

- `POST /borrow` - Borrow a book
  - Requires authentication
  - Required fields: book_id, borrower_name
  - Validates book availability
  - Limits borrowings per user
- `POST /return/{id}` - Return a book
  - Requires authentication
  - Updates return date
  - Makes book available again

## ✅ Validation Rules

### Books

- ISBN must be exactly 13 digits
- Publish date cannot be in the future
- Title is required
- Author must exist in the system
- Publisher must exist in the system
- Genres must exist in the system

### Authors

- Name must be unique
- Birth date cannot be in the future
- Name is required

### Publishers

- Name must be unique
- Established year cannot be in the future
- Name and established year are required

### Borrowing

- Maximum 3 books per borrower
- Book must be available to borrow
- Cannot return already returned books
- Borrower name is required

## 🧪 Testing

Run the tests:

```bash
pytest
```

Generate coverage report:

```bash
pytest --cov=app tests/
```

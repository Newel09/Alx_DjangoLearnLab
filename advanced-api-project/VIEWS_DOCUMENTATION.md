# View Configuration Documentation

## Overview
This document outlines the custom generic views implemented in the Advanced API Project for the Book model. Each view is designed following Django REST Framework best practices with proper permission handling, validation, and customization hooks.

---

## Views Architecture

### 1. **BookListCreateView** (Generic: ListCreateAPIView)

**Endpoints:**
- `GET /api/books/` — List all books (public, no auth required)
- `POST /api/books/` — Create a new book (authenticated users only)

**Features:**
- **Query Filtering:** Supports filtering by `author_id`
  - Example: `GET /api/books/?author_id=1`
- **Pagination:** Enabled via DRF settings (default 50 items per page)
- **Select Related:** Uses `select_related('author')` for optimized database queries
- **Custom Permission:** Uses `IsAuthenticatedForWrite` to allow public read, authenticated write
- **Validation:** Full model validation on book creation (publication year cannot be in future)

**Custom Methods:**
```python
get_queryset()      # Filters by author_id if provided in query params
perform_create()    # Handles validation errors gracefully
create()            # Custom response handling with 201 Created status
```

**Request/Response Examples:**

**List Books (GET):**
```bash
curl http://localhost:8000/api/books/
```
Response (200 OK):
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "The Great Gatsby",
      "publication_year": 1925,
      "author": 1
    },
    {
      "id": 2,
      "title": "To Kill a Mockingbird",
      "publication_year": 1960,
      "author": 2
    }
  ]
}
```

**Create Book (POST) — Authenticated Only:**
```bash
curl -X POST http://localhost:8000/api/books/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "1984",
    "publication_year": 1949,
    "author": 3
  }'
```
Response (201 Created):
```json
{
  "id": 3,
  "title": "1984",
  "publication_year": 1949,
  "author": 3
}
```

**Filter by Author (GET):**
```bash
curl http://localhost:8000/api/books/?author_id=1
```

---

### 2. **BookDetailView** (Generic: RetrieveAPIView)

**Endpoint:**
- `GET /api/books/<pk>/` — Retrieve a single book by ID (public, no auth required)

**Features:**
- **Read-Only:** Only supports GET requests
- **No Authentication Required:** Public access for read operations
- **Query Optimization:** Uses `select_related('author')` for efficient queries
- **Not Found Handling:** Returns 404 if book ID does not exist

**Custom Methods:**
None (uses DRF defaults)

**Request/Response Examples:**

**Retrieve Single Book (GET):**
```bash
curl http://localhost:8000/api/books/1/
```
Response (200 OK):
```json
{
  "id": 1,
  "title": "The Great Gatsby",
  "publication_year": 1925,
  "author": 1
}
```

**Invalid Book ID (GET):**
```bash
curl http://localhost:8000/api/books/999/
```
Response (404 Not Found):
```json
{
  "detail": "Not found."
}
```

---

### 3. **BookUpdateView** (Generic: UpdateAPIView)

**Endpoints:**
- `PUT /api/books/<pk>/` — Full update (authenticated users only)
- `PATCH /api/books/<pk>/` — Partial update (authenticated users only)

**Features:**
- **Requires Authentication:** Only authenticated users can update books
- **Full & Partial Updates:** Supports both PUT (all fields required) and PATCH (partial fields)
- **Validation:** Full model validation on update (publication year, etc.)
- **Optimized Queries:** Uses `select_related('author')`
- **Custom Error Handling:** Validation errors are captured and returned

**Custom Methods:**
```python
perform_update()    # Handles validation during save
update()            # Supports both full and partial updates with custom response
```

**Request/Response Examples:**

**Full Update (PUT) — All Fields Required:**
```bash
curl -X PUT http://localhost:8000/api/books/1/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "The Great Gatsby (Revised)",
    "publication_year": 1925,
    "author": 1
  }'
```
Response (200 OK):
```json
{
  "id": 1,
  "title": "The Great Gatsby (Revised)",
  "publication_year": 1925,
  "author": 1
}
```

**Partial Update (PATCH) — Only Some Fields:**
```bash
curl -X PATCH http://localhost:8000/api/books/1/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "The Great Gatsby (New Edition)"
  }'
```
Response (200 OK):
```json
{
  "id": 1,
  "title": "The Great Gatsby (New Edition)",
  "publication_year": 1925,
  "author": 1
}
```

**Validation Error (Future Year):**
```bash
curl -X PATCH http://localhost:8000/api/books/1/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "publication_year": 2025
  }'
```
Response (400 Bad Request):
```json
{
  "publication_year": ["Publication year cannot be in the future."]
}
```

**Unauthorized Access (No Token):**
```bash
curl -X PATCH http://localhost:8000/api/books/1/
```
Response (401 Unauthorized):
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

### 4. **BookDeleteView** (Generic: DestroyAPIView)

**Endpoint:**
- `DELETE /api/books/<pk>/delete/` — Delete a book (authenticated users only)

**Features:**
- **Requires Authentication:** Only authenticated users can delete books
- **No Content Response:** Returns 204 No Content on successful deletion
- **Cascade Delete:** Related data is handled per model configuration (CASCADE)

**Custom Methods:**
```python
perform_destroy()   # Custom deletion logic (if needed)
destroy()           # Custom response with 204 status
```

**Request/Response Examples:**

**Delete Book (DELETE):**
```bash
curl -X DELETE http://localhost:8000/api/books/3/delete/ \
  -H "Authorization: Token YOUR_TOKEN"
```
Response (204 No Content):
```
(empty response body)
```

**Unauthorized Delete:**
```bash
curl -X DELETE http://localhost:8000/api/books/1/delete/
```
Response (401 Unauthorized):
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

## Permission Model

### Custom Permission Class: `IsAuthenticatedForWrite`
```python
class IsAuthenticatedForWrite(AllowAny):
    """
    Allows:
    - Anyone (public) to read (GET, HEAD, OPTIONS)
    - Only authenticated users to write (POST, PUT, PATCH, DELETE)
    """
```

**Applied To:**
- `BookListCreateView` — Public read, authenticated write

**Other Views:**
- `BookDetailView` — Public (AllowAny)
- `BookUpdateView` — Authenticated only (IsAuthenticated)
- `BookDeleteView` — Authenticated only (IsAuthenticated)

---

## URL Routing Summary

| Method | Endpoint | View | Auth | Purpose |
|--------|----------|------|------|---------|
| GET | `/api/books/` | BookListCreateView | Public | List all books |
| POST | `/api/books/` | BookListCreateView | Required | Create a new book |
| GET | `/api/books/<pk>/` | BookDetailView | Public | Retrieve single book |
| PUT | `/api/books/<pk>/update/` | BookUpdateView | Required | Full update book |
| PATCH | `/api/books/<pk>/update/` | BookUpdateView | Required | Partial update book |
| DELETE | `/api/books/<pk>/delete/` | BookDeleteView | Required | Delete book |

---

## Testing Guide

### 1. Get Authentication Token
```bash
# First, create a superuser (if not already done)
python manage.py createsuperuser

# Obtain token (using DRF's default token endpoint)
curl -X POST http://localhost:8000/api-token-auth/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'
```

### 2. Test Public Read Access
```bash
# Should work without token
curl http://localhost:8000/api/books/
curl http://localhost:8000/api/books/1/
```

### 3. Test Protected Write Access
```bash
# Should fail without token
curl -X POST http://localhost:8000/api/books/ \
  -d '{"title": "New Book", "publication_year": 2020, "author": 1}'

# Should succeed with token
curl -X POST http://localhost:8000/api/books/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "New Book", "publication_year": 2020, "author": 1}'
```

### 4. Test Validation
```bash
# Should fail: future year
curl -X POST http://localhost:8000/api/books/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Future Book", "publication_year": 2030, "author": 1}'
```

---

## Key DRF Features Used

1. **Generic Views:** ListCreateAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView
2. **Permissions:** IsAuthenticated, AllowAny, custom IsAuthenticatedForWrite
3. **Validation:** Model-level and serializer-level validation
4. **Query Optimization:** select_related() for efficient DB queries
5. **Response Customization:** Custom response objects with appropriate status codes
6. **Error Handling:** ValidationError and proper error response formats

---

## Future Enhancements (Optional)

1. **Throttling:** Add rate limiting to prevent API abuse
2. **Pagination:** Implement cursor-based pagination for large datasets
3. **Filtering:** Add advanced filtering by multiple fields (title, author, year range)
4. **Sorting:** Allow sorting by publication_year, title, etc.
5. **Caching:** Add Redis caching for frequently accessed books
6. **Search:** Implement full-text search on book titles and author names
7. **Versioning:** Implement API versioning if needed
8. **Logging:** Add detailed logging for auditing and debugging

---

## Troubleshooting

**Issue:** 401 Unauthorized on write operations
- **Solution:** Ensure your request includes the `Authorization: Token YOUR_TOKEN` header

**Issue:** 400 Bad Request on book creation
- **Solution:** Check that all required fields are provided and `publication_year` is not in the future

**Issue:** 404 Not Found on detail/update/delete
- **Solution:** Verify the book ID exists with a GET /api/books/ first

**Issue:** 405 Method Not Allowed
- **Solution:** Ensure you're using the correct HTTP method for the endpoint

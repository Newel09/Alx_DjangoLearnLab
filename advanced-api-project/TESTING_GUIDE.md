# API Testing Guide

This guide provides step-by-step instructions for testing all the Book API endpoints implemented in the advanced-api-project.

## Prerequisites

1. Development server running:
```bash
python manage.py runserver
```

2. Superuser created:
```bash
python manage.py createsuperuser
```

3. At least one Author in the database. You can create one via Django admin at `http://localhost:8000/admin/`

---

## Step 1: Obtain Authentication Token

Before testing protected endpoints, get your authentication token:

```bash
curl -X POST http://localhost:8000/api-token-auth/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "your_password_here"
  }'
```

**Expected Response (200 OK):**
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
}
```

**Save this token** - you'll need it for all protected endpoints.

---

## Step 2: Test Public Read Endpoints (No Auth Required)

### 2.1 List All Books
```bash
curl http://localhost:8000/api/books/
```

**Expected Response (200 OK):**
```json
{
  "count": 0,
  "next": null,
  "previous": null,
  "results": []
}
```

### 2.2 Retrieve Single Book
```bash
curl http://localhost:8000/api/books/1/
```

**Expected Response (200 OK):**
```json
{
  "id": 1,
  "title": "The Great Gatsby",
  "publication_year": 1925,
  "author": 1
}
```

**Expected Response (404 Not Found) if book doesn't exist:**
```json
{
  "detail": "Not found."
}
```

### 2.3 Filter Books by Author
```bash
curl http://localhost:8000/api/books/?author_id=1
```

---

## Step 3: Test Protected Write Endpoints (Auth Required)

### 3.1 Create a Book (POST)

```bash
curl -X POST http://localhost:8000/api/books/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "1984",
    "publication_year": 1949,
    "author": 1
  }'
```

**Expected Response (201 Created):**
```json
{
  "id": 1,
  "title": "1984",
  "publication_year": 1949,
  "author": 1
}
```

**Test without token - Expected (401 Unauthorized):**
```bash
curl -X POST http://localhost:8000/api/books/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Book", "publication_year": 2000, "author": 1}'
```

Response:
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 3.2 Full Update (PUT)

```bash
curl -X PUT http://localhost:8000/api/books/1/update/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "1984 (Revised Edition)",
    "publication_year": 1949,
    "author": 1
  }'
```

**Expected Response (200 OK):**
```json
{
  "id": 1,
  "title": "1984 (Revised Edition)",
  "publication_year": 1949,
  "author": 1
}
```

**Note:** PUT requires ALL fields. If you omit a field, you'll get a 400 error.

### 3.3 Partial Update (PATCH)

```bash
curl -X PATCH http://localhost:8000/api/books/1/update/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "1984 (New Title)"
  }'
```

**Expected Response (200 OK):**
```json
{
  "id": 1,
  "title": "1984 (New Title)",
  "publication_year": 1949,
  "author": 1
}
```

### 3.4 Delete a Book (DELETE)

```bash
curl -X DELETE http://localhost:8000/api/books/1/delete/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

**Expected Response (204 No Content):**
```
(empty response body)
```

---

## Step 4: Test Permission & Validation Errors

### 4.1 Future Publication Year (Validation Error)

```bash
curl -X POST http://localhost:8000/api/books/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Future Book",
    "publication_year": 2030,
    "author": 1
  }'
```

**Expected Response (400 Bad Request):**
```json
{
  "publication_year": [
    "Publication year cannot be in the future."
  ]
}
```

### 4.2 Missing Required Field (Validation Error)

```bash
curl -X POST http://localhost:8000/api/books/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Book Without Author"
  }'
```

**Expected Response (400 Bad Request):**
```json
{
  "author": [
    "This field is required."
  ]
}
```

### 4.3 Invalid Author ID (Foreign Key Error)

```bash
curl -X POST http://localhost:8000/api/books/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Book",
    "publication_year": 2000,
    "author": 9999
  }'
```

**Expected Response (400 Bad Request):**
```json
{
  "author": [
    "Invalid pk \"9999\" - object does not exist."
  ]
}
```

---

## Step 5: Test with Postman (Alternative)

If you prefer using Postman instead of curl:

1. **Import endpoints** or manually create requests for each URL pattern
2. **Set Authorization:** In the Authorization tab, select "Bearer Token" and enter your token
3. **Set Headers:** Add `Content-Type: application/json`
4. **Test** each endpoint

---

## Summary of Test Coverage

| Feature | Status | Test Completed |
|---------|--------|----------------|
| List books (public) | ✅ | [ ] |
| Get book detail (public) | ✅ | [ ] |
| Filter by author | ✅ | [ ] |
| Create book (auth required) | ✅ | [ ] |
| Full update book (auth required) | ✅ | [ ] |
| Partial update book (auth required) | ✅ | [ ] |
| Delete book (auth required) | ✅ | [ ] |
| Validation: future year | ✅ | [ ] |
| Missing required field | ✅ | [ ] |
| Unauthorized create attempt | ✅ | [ ] |
| Invalid author ID | ✅ | [ ] |

---

## Common Issues & Solutions

**Issue:** 401 Unauthorized on protected endpoints
- **Solution:** Make sure token is included in the `-H "Authorization: Token YOUR_TOKEN"` header

**Issue:** 404 Not Found for book retrieval
- **Solution:** Verify the book ID exists by listing all books first

**Issue:** 400 Bad Request with "This field is required"
- **Solution:** Ensure all required fields (title, publication_year, author) are provided

**Issue:** Pagination returns empty results
- **Solution:** Default page size is 50. Use `?page=2` to access subsequent pages

**Issue:** Token doesn't work
- **Solution:** Get a fresh token from the `/api-token-auth/` endpoint; tokens may expire depending on your configuration

---

## Next Steps

Once all tests pass, you can:
1. Deploy to a production environment
2. Add more features (filtering, search, ordering)
3. Implement rate limiting and throttling
4. Add automated tests in `api/tests.py`
5. Set up CI/CD pipeline

# Quick Start Guide - LMS Lite

## Server Status
✅ Server is running at: **http://127.0.0.1:8000/**

## Common 404 Errors & Solutions

### ❌ Error: 404 Not Found

**Possible causes:**
1. **Missing trailing slash** - Django requires trailing slashes for most URLs
   - ❌ Wrong: `http://127.0.0.1:8000/api/auth/login`
   - ✅ Correct: `http://127.0.0.1:8000/api/auth/login/`

2. **Wrong HTTP method** - Some endpoints only accept specific methods
   - Register/Login require **POST**, not GET
   - ❌ GET `/api/auth/register/` → 405 Method Not Allowed
   - ✅ POST `/api/auth/register/` → 201 Created

3. **Incorrect URL path**
   - Check the exact endpoint path below

## Working Endpoints

### ✅ Root API (GET)
```
GET http://127.0.0.1:8000/
```
Returns API documentation with all available endpoints.

### ✅ Authentication Endpoints

**Register User (POST)**
```bash
POST http://127.0.0.1:8000/api/auth/register/
Content-Type: application/json

{
  "username": "student1",
  "email": "student1@example.com",
  "password": "password123",
  "password2": "password123",
  "first_name": "John",
  "last_name": "Doe",
  "role": "student"
}
```

**Login (POST)**
```bash
POST http://127.0.0.1:8000/api/auth/login/
Content-Type: application/json

{
  "username": "student1",
  "password": "password123"
}
```

**Get Profile (GET - Requires Auth)**
```bash
GET http://127.0.0.1:8000/api/auth/profile/
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### ✅ Courses (GET - Requires Auth)
```bash
GET http://127.0.0.1:8000/api/courses/
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### ✅ Reports Dashboard (GET - Requires Auth)
```bash
GET http://127.0.0.1:8000/api/reports/dashboard/
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## Testing with cURL

### Register a User
```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"testuser\",\"email\":\"test@example.com\",\"password\":\"test123\",\"password2\":\"test123\",\"first_name\":\"Test\",\"last_name\":\"User\",\"role\":\"student\"}"
```

### Login
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"testuser\",\"password\":\"test123\"}"
```

## Expected Status Codes

- **200 OK** - Successful GET request
- **201 Created** - Successful POST (register, create)
- **400 Bad Request** - Invalid data
- **401 Unauthorized** - Missing or invalid token
- **403 Forbidden** - Insufficient permissions
- **404 Not Found** - URL doesn't exist (check trailing slash!)
- **405 Method Not Allowed** - Wrong HTTP method (e.g., GET on POST-only endpoint)

## Admin Panel
```
http://127.0.0.1:8000/admin/
```
Create a superuser first:
```bash
python manage.py createsuperuser
```





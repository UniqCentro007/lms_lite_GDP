# Student Login Guide

## 🎓 Student Login Endpoints

There are **two ways** to login as a student:

### Option 1: **Dedicated Student Login** (Recommended)
**URL:** `POST http://127.0.0.1:8000/api/auth/student/login/`

This endpoint is **exclusively for students** - only users with `role='student'` can login here. Non-students will be rejected.

### Option 2: **General Login**
**URL:** `POST http://127.0.0.1:8000/api/auth/login/`

This endpoint accepts all user types (students, instructors, admins).

---

## Login Methods

You can login using **any of these methods** with either endpoint:

### 1. **Username**
```json
{
  "username": "student1",
  "password": "student123"
}
```

### 2. **Email**
```json
{
  "email": "student@lms.com",
  "password": "student123"
}
```

Or:
```json
{
  "username": "student@lms.com",
  "password": "student123"
}
```

### 3. **Student ID** (User Database ID)
```json
{
  "student_id": "3",
  "password": "student123"
}
```

Or:
```json
{
  "username": "3",
  "password": "student123"
}
```

## Current Student Account

- **Student ID**: 3
- **Username**: student1
- **Email**: student@lms.com
- **Password**: student123

**Content-Type:** `application/json`

## Example Requests

### 🎯 Using Dedicated Student Login Endpoint

#### Method 1: Login with Username
```bash
curl -X POST http://127.0.0.1:8000/api/auth/student/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "student1",
    "password": "student123"
  }'
```

#### Method 2: Login with Email
```bash
curl -X POST http://127.0.0.1:8000/api/auth/student/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@lms.com",
    "password": "student123"
  }'
```

#### Method 3: Login with Student ID
```bash
curl -X POST http://127.0.0.1:8000/api/auth/student/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "3",
    "password": "student123"
  }'
```

### 🔄 Using General Login Endpoint (Alternative)

#### Using Username
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "student1",
    "password": "student123"
  }'
```

#### Using Email
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "student@lms.com",
    "password": "student123"
  }'
```

#### Using Student ID
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "3",
    "password": "student123"
  }'
```

### 💻 Using PowerShell (Windows)

```powershell
# Login with username
$loginData = @{
    username = "student1"
    password = "student123"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/auth/student/login/" `
    -Method POST `
    -ContentType "application/json" `
    -Body $loginData
```

### 🐍 Using Python

```python
import requests

url = "http://127.0.0.1:8000/api/auth/student/login/"
data = {
    "username": "student1",
    "password": "student123"
}

response = requests.post(url, json=data)
print(response.json())
```

## Response

### ✅ Successful Login Response

```json
{
  "user": {
    "id": 3,
    "username": "student1",
    "email": "student@lms.com",
    "first_name": "Jane",
    "last_name": "Student",
    "role": "student",
    "is_active": true
  },
  "tokens": {
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  },
  "message": "Student login successful"
}
```

### ❌ Error Responses

#### Invalid Credentials (401)
```json
{
  "error": "Invalid credentials. Use username, email, or student ID."
}
```

#### Non-Student User (403) - Only for `/api/auth/student/login/`
```json
{
  "error": "Access denied. Student privileges required."
}
```

#### Missing Fields (400)
```json
{
  "error": "Username/Student ID/Email and password are required."
}
```

## Using the Access Token

After successful login, use the `access` token to authenticate API requests:

```bash
curl -X GET http://127.0.0.1:8000/api/courses/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

## Notes

- ✅ **Dedicated Student Login** (`/api/auth/student/login/`) only accepts students
- ✅ **General Login** (`/api/auth/login/`) accepts all user types
- ✅ Student ID login works for users with `role='student'`
- ✅ The system tries username first, then email, then student ID
- ✅ All methods require the correct password
- ✅ The `username` field accepts username, email, or student ID
- ✅ Save the `access` token for authenticated requests
- ✅ Use `refresh` token to get a new access token when it expires





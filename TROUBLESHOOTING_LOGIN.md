# Troubleshooting Student Login Issues

## ✅ Login Endpoint Status
The login endpoint is **working correctly**. Test shows:
- Status: 200 OK
- User authenticated successfully
- Tokens generated properly

## Common Login Errors & Solutions

### 1. **400 Bad Request - "Username and password are required"**
**Cause:** Missing username or password in request body

**Solution:**
```json
{
  "username": "student1",
  "password": "student123"
}
```
Make sure both fields are included in your POST request.

### 2. **401 Unauthorized - "Invalid credentials"**
**Cause:** Wrong username or password

**Solution:**
- Username: `student1` (exact, case-sensitive)
- Password: `student123` (exact, case-sensitive)
- Check for extra spaces or typos

### 3. **403 Forbidden - "User account is disabled"**
**Cause:** User account is inactive

**Solution:**
```python
# In Django shell:
from accounts.models import User
user = User.objects.get(username='student1')
user.is_active = True
user.save()
```

### 4. **404 Not Found**
**Cause:** Wrong URL or missing trailing slash

**Solution:**
- ✅ Correct: `http://127.0.0.1:8000/api/auth/login/`
- ❌ Wrong: `http://127.0.0.1:8000/api/auth/login` (missing trailing slash)

### 5. **405 Method Not Allowed**
**Cause:** Using GET instead of POST

**Solution:**
- Must use **POST** method
- Not GET, PUT, or DELETE

### 6. **500 Internal Server Error**
**Cause:** Server-side issue

**Solution:**
- Check server logs
- Verify database connection
- Check if migrations are applied

## Correct Login Request Format

### Using cURL:
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "student1",
    "password": "student123"
  }'
```

### Using PowerShell:
```powershell
$loginData = @{
    username = "student1"
    password = "student123"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/auth/login/" `
    -Method Post `
    -Body $loginData `
    -ContentType "application/json"
```

### Using JavaScript (fetch):
```javascript
fetch('http://127.0.0.1:8000/api/auth/login/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    username: 'student1',
    password: 'student123'
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

### Using Python (requests):
```python
import requests

response = requests.post(
    'http://127.0.0.1:8000/api/auth/login/',
    json={
        'username': 'student1',
        'password': 'student123'
    }
)
print(response.json())
```

## Expected Successful Response

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
  }
}
```

## Test Credentials

- **Username:** `student1`
- **Password:** `student123`
- **Email:** `student@lms.com`
- **Role:** `student`

## Still Having Issues?

1. Check server is running: `python manage.py runserver`
2. Verify user exists in database
3. Check browser console for errors
4. Verify Content-Type header is `application/json`
5. Check network tab for actual request/response





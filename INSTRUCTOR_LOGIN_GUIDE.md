# Instructor Login Guide

## Login Credentials

**Test Instructor Account:**
- **Username:** `test_instructor`
- **Email:** `test_instructor@lms.com`
- **Password:** `instructor123`

---

## Method 1: Web Interface (Easiest)

1. **Open your browser** and navigate to:
   ```
   http://127.0.0.1:8000/instructor/login/
   ```

2. **Enter your credentials:**
   - Username/Email: `test_instructor` or `test_instructor@lms.com`
   - Password: `instructor123`

3. **Click "Login as Instructor"**

4. You'll be redirected to the instructor dashboard at:
   ```
   http://127.0.0.1:8000/instructor/dashboard/
   ```

---

## Method 2: REST API Endpoint

### Using cURL

**Login with username:**
```bash
curl -X POST http://127.0.0.1:8000/api/auth/instructor/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_instructor",
    "password": "instructor123"
  }'
```

**Login with email:**
```bash
curl -X POST http://127.0.0.1:8000/api/auth/instructor/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test_instructor@lms.com",
    "password": "instructor123"
  }'
```

### Using Python (requests library)

```python
import requests

url = "http://127.0.0.1:8000/api/auth/instructor/login/"
credentials = {
    "username": "test_instructor",
    "password": "instructor123"
}

response = requests.post(url, json=credentials)
data = response.json()

if response.status_code == 200:
    print("Login successful!")
    print(f"Access Token: {data['tokens']['access']}")
    print(f"User: {data['user']['username']}")
    print(f"Role: {data['user']['role']}")
else:
    print(f"Login failed: {data}")
```

### Using JavaScript (fetch)

```javascript
fetch('http://127.0.0.1:8000/api/auth/instructor/login/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    username: 'test_instructor',
    password: 'instructor123'
  })
})
.then(response => response.json())
.then(data => {
  if (data.tokens) {
    console.log('Login successful!');
    console.log('Access Token:', data.tokens.access);
    console.log('User:', data.user);
  } else {
    console.error('Login failed:', data);
  }
});
```

---

## Method 3: Using Postman

1. **Create a new POST request**
2. **URL:** `http://127.0.0.1:8000/api/auth/instructor/login/`
3. **Headers:**
   - `Content-Type: application/json`
4. **Body (raw JSON):**
   ```json
   {
     "username": "test_instructor",
     "password": "instructor123"
   }
   ```
5. **Send the request**

**Response will include:**
```json
{
  "user": {
    "id": 1,
    "username": "test_instructor",
    "email": "test_instructor@lms.com",
    "first_name": "Test",
    "last_name": "Instructor",
    "role": "instructor"
  },
  "tokens": {
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  },
  "message": "Instructor login successful"
}
```

---

## Using the Access Token

After successful login, use the access token for authenticated API requests:

**Example:**
```bash
curl -X GET http://127.0.0.1:8000/api/courses/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

---

## Available Endpoints

- **Login:** `POST /api/auth/instructor/login/`
- **Dashboard:** `GET /instructor/dashboard/` (web interface)
- **Profile:** `GET /api/auth/profile/` (requires authentication)
- **Courses:** `GET /api/courses/` (requires authentication)

---

## Troubleshooting

### Server not running?
Start the Django development server:
```bash
cd lms_project
python manage.py runserver
```

### Invalid credentials?
Make sure you're using:
- Username: `test_instructor`
- Password: `instructor123`

### Account doesn't exist?
Create the instructor account:
```bash
cd lms_project
python manage.py shell
```

Then run:
```python
from accounts.models import User
instructor = User.objects.create_user(
    username='test_instructor',
    email='test_instructor@lms.com',
    password='instructor123',
    first_name='Test',
    last_name='Instructor',
    role='instructor'
)
```

---

## Notes

- The web interface uses **session-based authentication**
- The API endpoint uses **JWT (JSON Web Token) authentication**
- Access tokens expire after **1 hour** (configurable in settings)
- Refresh tokens expire after **7 days** (configurable in settings)
- Only users with `role='instructor'` can login through the instructor login endpoint

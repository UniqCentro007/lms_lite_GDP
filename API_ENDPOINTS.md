# LMS Lite - API Endpoints

## Server Status
✅ Django development server is running on http://127.0.0.1:8000/

## Available Endpoints

### Authentication (`/api/auth/`)
- `POST /api/auth/register/` - Register a new user
- `POST /api/auth/login/` - Login and get JWT tokens
- `POST /api/auth/token/refresh/` - Refresh access token
- `GET /api/auth/profile/` - Get current user profile
- `PUT /api/auth/profile/` - Update user profile
- `GET /api/auth/users/` - List users (Admin/Instructor)

### Courses (`/api/courses/`)
- `GET /api/courses/` - List all courses
- `POST /api/courses/` - Create course (Instructor)
- `GET /api/courses/{id}/` - Get course details
- `PUT /api/courses/{id}/` - Update course (Instructor)
- `DELETE /api/courses/{id}/` - Delete course (Instructor)
- `GET /api/courses/{id}/modules/` - Get course modules
- `GET /api/courses/modules/` - List modules
- `POST /api/courses/modules/` - Create module
- `GET /api/courses/lessons/` - List lessons
- `POST /api/courses/lessons/` - Create lesson

### Enrollments (`/api/enrollments/`)
- `GET /api/enrollments/` - List enrollments
- `POST /api/enrollments/` - Enroll in a course
- `GET /api/enrollments/{id}/` - Get enrollment details
- `GET /api/enrollments/{id}/progress/` - Get enrollment progress
- `POST /api/enrollments/progress/` - Update lesson progress

### Quizzes (`/api/quizzes/`)
- `GET /api/quizzes/` - List quizzes
- `POST /api/quizzes/` - Create quiz (Instructor)
- `GET /api/quizzes/{id}/` - Get quiz details
- `GET /api/quizzes/{id}/questions/` - Get quiz questions
- `POST /api/quizzes/{id}/submit/` - Submit quiz answers
- `GET /api/quizzes/results/` - Get quiz results

### Certificates (`/api/certificates/`)
- `GET /api/certificates/` - List certificates
- `POST /api/certificates/` - Generate certificate
- `GET /api/certificates/{id}/` - Get certificate details
- `GET /api/certificates/{id}/download/` - Download certificate PDF
- `POST /api/certificates/{id}/approve/` - Approve certificate (Admin)

### Reports (`/api/reports/`)
- `GET /api/reports/dashboard/` - Get dashboard statistics
- `GET /api/reports/course/{id}/performance/` - Get course performance
- `GET /api/reports/enrollments/` - Get enrollment report

### Admin Panel
- `http://127.0.0.1:8000/admin/` - Django admin interface

## Example API Usage

### Register a User
```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "student1",
    "email": "student1@example.com",
    "password": "password123",
    "password2": "password123",
    "first_name": "John",
    "last_name": "Doe",
    "role": "student"
  }'
```

### Login
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "student1",
    "password": "password123"
  }'
```

### Access Protected Endpoint
```bash
curl -X GET http://127.0.0.1:8000/api/courses/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```





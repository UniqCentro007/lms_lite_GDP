# LMS Lite - Learning Management System

A comprehensive Learning Management System built with Django and Django REST Framework, designed for training institutes and corporate learning programs.

## Features

- **User Management**: Role-based access control (Student, Instructor, Admin) with JWT authentication
- **Course Management**: Create courses with modules and lessons supporting video, PDF, and text content
- **Enrollment System**: Students can enroll in courses and track progress at lesson level
- **Quiz Engine**: Automated quiz evaluation with multiple question types
- **Certificate Generation**: Automatic PDF certificate generation upon course completion
- **Reports Dashboard**: Comprehensive analytics and reporting for all user roles
- **AWS S3 Integration**: Support for storing media files on AWS S3
- **Docker Support**: Easy deployment with Docker and Docker Compose

## Technology Stack

- **Backend**: Django 4.2.7, Django REST Framework 3.14.0
- **Database**: PostgreSQL
- **Authentication**: JWT (djangorestframework-simplejwt)
- **File Storage**: AWS S3 (with local fallback)
- **PDF Generation**: ReportLab
- **Containerization**: Docker, Docker Compose

## Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Docker and Docker Compose (optional, for containerized deployment)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd lms_project
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Set up PostgreSQL database**
   - Create a database named `lms_db`
   - Update database credentials in `.env`

6. **Run migrations**
   ```bash
   python manage.py migrate
   ```

7. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

8. **Run development server**
   ```bash
   python manage.py runserver
   ```

### Docker Deployment

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **Create superuser**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

3. **Access the application**
   - API: http://localhost:8000
   - Admin Panel: http://localhost:8000/admin

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/token/refresh/` - Refresh JWT token
- `GET /api/auth/profile/` - Get user profile
- `PUT /api/auth/profile/` - Update user profile

### Courses
- `GET /api/courses/` - List all courses
- `POST /api/courses/` - Create course (Instructor)
- `GET /api/courses/{id}/` - Get course details
- `PUT /api/courses/{id}/` - Update course (Instructor)
- `GET /api/courses/{id}/modules/` - Get course modules
- `GET /api/courses/modules/` - List modules
- `POST /api/courses/modules/` - Create module
- `GET /api/courses/lessons/` - List lessons
- `POST /api/courses/lessons/` - Create lesson

### Enrollments
- `GET /api/enrollments/` - List enrollments
- `POST /api/enrollments/` - Enroll in a course
- `GET /api/enrollments/{id}/` - Get enrollment details
- `GET /api/enrollments/{id}/progress/` - Get enrollment progress
- `POST /api/enrollments/progress/` - Update lesson progress

### Quizzes
- `GET /api/quizzes/` - List quizzes
- `POST /api/quizzes/` - Create quiz (Instructor)
- `GET /api/quizzes/{id}/` - Get quiz details
- `GET /api/quizzes/{id}/questions/` - Get quiz questions
- `POST /api/quizzes/{id}/submit/` - Submit quiz answers
- `GET /api/quizzes/results/` - Get quiz results

### Certificates
- `GET /api/certificates/` - List certificates
- `POST /api/certificates/` - Generate certificate
- `GET /api/certificates/{id}/` - Get certificate details
- `GET /api/certificates/{id}/download/` - Download certificate PDF
- `POST /api/certificates/{id}/approve/` - Approve certificate (Admin)

### Reports
- `GET /api/reports/dashboard/` - Get dashboard statistics
- `GET /api/reports/course/{id}/performance/` - Get course performance
- `GET /api/reports/enrollments/` - Get enrollment report

## User Roles

### Student
- Browse and enroll in published courses
- Access course content and track progress
- Take quizzes and view results
- Download certificates upon completion

### Instructor
- Create and manage courses
- Upload course materials (videos, PDFs, text)
- Create quizzes and questions
- View student progress and performance
- Access instructor dashboard

### Admin
- Manage users and roles
- Approve certificates (if required)
- Access platform-wide statistics
- Manage all courses and content

## Database Models

- **User**: Custom user model with role-based access
- **Course**: Course information and metadata
- **Module**: Course sections
- **Lesson**: Individual lessons with content
- **Enrollment**: Student course enrollments
- **Progress**: Lesson-level progress tracking
- **Quiz**: Course quizzes
- **Question**: Quiz questions
- **Choice**: Multiple choice options
- **QuizResult**: Student quiz attempts and scores
- **Answer**: Individual question answers
- **Certificate**: Course completion certificates

## Configuration

### AWS S3 Setup (Optional)

To use AWS S3 for file storage:

1. Create an S3 bucket
2. Configure IAM user with S3 access
3. Update `.env` with AWS credentials:
   ```
   AWS_ACCESS_KEY_ID=your-access-key
   AWS_SECRET_ACCESS_KEY=your-secret-key
   AWS_STORAGE_BUCKET_NAME=your-bucket-name
   AWS_S3_REGION_NAME=us-east-1
   ```

If AWS credentials are not provided, the system will use local file storage.

### Certificate Settings

Configure certificate requirements in `.env`:
- `CERTIFICATE_MIN_SCORE`: Minimum quiz score required (default: 70)
- `CERTIFICATE_REQUIRE_APPROVAL`: Require admin approval (default: False)

## Development

### Running Tests
```bash
python manage.py test
```

### Creating Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Collecting Static Files
```bash
python manage.py collectstatic
```

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please open an issue on the repository.





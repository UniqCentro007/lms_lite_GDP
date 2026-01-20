"""
Script to create test data for LMS Lite
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_project.settings')
django.setup()

from accounts.models import User
from courses.models import Course, Module, Lesson
from quizzes.models import Quiz, Question, Choice

# Create test users
print("Creating test users...")

# Create admin user
admin, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@lms.com',
        'first_name': 'Admin',
        'last_name': 'User',
        'role': 'admin',
        'is_staff': True,
        'is_superuser': True
    }
)
if created:
    admin.set_password('admin123')
    admin.save()
    print(f"✅ Created admin user: {admin.username}")
else:
    print(f"ℹ️  Admin user already exists: {admin.username}")

# Create instructor
instructor, created = User.objects.get_or_create(
    username='instructor1',
    defaults={
        'email': 'instructor@lms.com',
        'first_name': 'John',
        'last_name': 'Instructor',
        'role': 'instructor'
    }
)
if created:
    instructor.set_password('instructor123')
    instructor.save()
    print(f"✅ Created instructor: {instructor.username}")
else:
    print(f"ℹ️  Instructor already exists: {instructor.username}")

# Create student
student, created = User.objects.get_or_create(
    username='student1',
    defaults={
        'email': 'student@lms.com',
        'first_name': 'Jane',
        'last_name': 'Student',
        'role': 'student'
    }
)
if created:
    student.set_password('student123')
    student.save()
    print(f"✅ Created student: {student.username}")
else:
    print(f"ℹ️  Student already exists: {student.username}")

# Create a test course
print("\nCreating test course...")
course, created = Course.objects.get_or_create(
    title='Introduction to Python Programming',
    defaults={
        'instructor': instructor,
        'description': 'Learn Python programming from scratch. This course covers basics to intermediate concepts.',
        'difficulty_level': 'beginner',
        'duration_hours': 20,
        'price': 0.00,
        'is_published': True
    }
)
if created:
    print(f"✅ Created course: {course.title}")
else:
    print(f"ℹ️  Course already exists: {course.title}")

# Create modules
print("\nCreating modules...")
module1, _ = Module.objects.get_or_create(
    course=course,
    order=1,
    defaults={
        'title': 'Getting Started',
        'description': 'Introduction to Python and setup'
    }
)
print(f"✅ Module 1: {module1.title}")

module2, _ = Module.objects.get_or_create(
    course=course,
    order=2,
    defaults={
        'title': 'Python Basics',
        'description': 'Variables, data types, and basic operations'
    }
)
print(f"✅ Module 2: {module2.title}")

# Create lessons
print("\nCreating lessons...")
lesson1, _ = Lesson.objects.get_or_create(
    module=module1,
    order=1,
    defaults={
        'title': 'What is Python?',
        'description': 'Introduction to Python programming language',
        'content_type': 'text',
        'text_content': 'Python is a high-level, interpreted programming language known for its simplicity and readability.',
        'duration_minutes': 15,
        'is_free': True
    }
)
print(f"✅ Lesson 1: {lesson1.title}")

lesson2, _ = Lesson.objects.get_or_create(
    module=module1,
    order=2,
    defaults={
        'title': 'Installing Python',
        'description': 'How to install Python on your system',
        'content_type': 'text',
        'text_content': 'Download Python from python.org and follow the installation instructions for your operating system.',
        'duration_minutes': 10,
        'is_free': True
    }
)
print(f"✅ Lesson 2: {lesson2.title}")

lesson3, _ = Lesson.objects.get_or_create(
    module=module2,
    order=1,
    defaults={
        'title': 'Variables and Data Types',
        'description': 'Learn about variables and different data types in Python',
        'content_type': 'text',
        'text_content': 'Python supports various data types including integers, floats, strings, lists, and dictionaries.',
        'duration_minutes': 20,
        'is_free': False
    }
)
print(f"✅ Lesson 3: {lesson3.title}")

# Create quiz
print("\nCreating quiz...")
quiz, created = Quiz.objects.get_or_create(
    course=course,
    defaults={
        'title': 'Python Basics Quiz',
        'description': 'Test your knowledge of Python basics',
        'time_limit_minutes': 30,
        'passing_score': 70,
        'max_attempts': 3,
        'is_active': True
    }
)
if created:
    print(f"✅ Created quiz: {quiz.title}")
    
    # Create questions
    print("\nCreating quiz questions...")
    
    # Question 1 - Multiple Choice
    q1, _ = Question.objects.get_or_create(
        quiz=quiz,
        order=1,
        defaults={
            'question_text': 'What is Python?',
            'question_type': 'multiple_choice',
            'points': 1
        }
    )
    Choice.objects.get_or_create(question=q1, choice_text='A programming language', is_correct=True, order=1)
    Choice.objects.get_or_create(question=q1, choice_text='A snake', is_correct=False, order=2)
    Choice.objects.get_or_create(question=q1, choice_text='A database', is_correct=False, order=3)
    print(f"✅ Question 1: {q1.question_text}")
    
    # Question 2 - True/False
    q2, _ = Question.objects.get_or_create(
        quiz=quiz,
        order=2,
        defaults={
            'question_text': 'Python is a compiled language.',
            'question_type': 'true_false',
            'points': 1
        }
    )
    Choice.objects.get_or_create(question=q2, choice_text='True', is_correct=False, order=1)
    Choice.objects.get_or_create(question=q2, choice_text='False', is_correct=True, order=2)
    print(f"✅ Question 2: {q2.question_text}")
    
    # Question 3 - Short Answer
    q3, _ = Question.objects.get_or_create(
        quiz=quiz,
        order=3,
        defaults={
            'question_text': 'What keyword is used to define a function in Python?',
            'question_type': 'short_answer',
            'points': 1
        }
    )
    Choice.objects.get_or_create(question=q3, choice_text='def', is_correct=True, order=1)
    print(f"✅ Question 3: {q3.question_text}")
else:
    print(f"ℹ️  Quiz already exists: {quiz.title}")

print("\n" + "="*50)
print("✅ Test data creation complete!")
print("="*50)
print("\nTest Users:")
print(f"  Admin:      username=admin,      password=admin123")
print(f"  Instructor: username=instructor1, password=instructor123")
print(f"  Student:    username=student1,    password=student123")
print(f"\nTest Course: {course.title}")
print(f"  Modules: {course.modules.count()}")
print(f"  Lessons: {course.total_lessons}")
print(f"  Quiz: {quiz.title if hasattr(course, 'quiz') else 'None'}")





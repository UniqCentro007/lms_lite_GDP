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
from enrollments.models import Enrollment, Progress
from django.utils import timezone
from datetime import timedelta

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
    print(f"[OK] Created admin user: {admin.username}")
else:
    print(f"[INFO] Admin user already exists: {admin.username}")

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
    print(f"[OK] Created instructor: {instructor.username}")
else:
    print(f"[INFO] Instructor already exists: {instructor.username}")

# Create students
students = []
for i in range(1, 6):  # Create 5 students
    student, created = User.objects.get_or_create(
        username=f'student{i}',
        defaults={
            'email': f'student{i}@lms.com',
            'first_name': f'Student{i}',
            'last_name': 'User',
            'role': 'student'
        }
    )
    if created:
        student.set_password('student123')
        student.save()
        print(f"[OK] Created student: {student.username}")
    else:
        print(f"[INFO] Student already exists: {student.username}")
    students.append(student)

# Create multiple test courses
print("\nCreating test courses...")
courses_data = [
    {
        'title': 'Introduction to Python Programming',
        'description': 'Learn Python programming from scratch. This course covers basics to intermediate concepts.',
        'difficulty_level': 'beginner',
        'duration_hours': 20,
        'price': 0.00,
        'is_published': True
    },
    {
        'title': 'Advanced Web Development',
        'description': 'Master modern web development with Django, React, and REST APIs.',
        'difficulty_level': 'intermediate',
        'duration_hours': 40,
        'price': 99.99,
        'is_published': True
    },
    {
        'title': 'Data Science Fundamentals',
        'description': 'Introduction to data science with Python, pandas, and matplotlib.',
        'difficulty_level': 'intermediate',
        'duration_hours': 30,
        'price': 79.99,
        'is_published': True
    },
    {
        'title': 'Machine Learning Basics',
        'description': 'Learn the fundamentals of machine learning and neural networks.',
        'difficulty_level': 'advanced',
        'duration_hours': 50,
        'price': 149.99,
        'is_published': False
    }
]

courses = []
for course_data in courses_data:
    course, created = Course.objects.get_or_create(
        title=course_data['title'],
        defaults={
            'instructor': instructor,
            **course_data
        }
    )
    if created:
        print(f"[OK] Created course: {course.title}")
    else:
        print(f"[INFO] Course already exists: {course.title}")
    courses.append(course)

# Create modules and lessons for each course
print("\nCreating modules and lessons...")
for course in courses:
    # Create modules for each course
    module1, _ = Module.objects.get_or_create(
        course=course,
        order=1,
        defaults={
            'title': f'{course.title.split()[0]} - Module 1',
            'description': f'First module of {course.title}'
        }
    )
    
    module2, _ = Module.objects.get_or_create(
        course=course,
        order=2,
        defaults={
            'title': f'{course.title.split()[0]} - Module 2',
            'description': f'Second module of {course.title}'
        }
    )
    
    # Create lessons for each module
    for module in [module1, module2]:
        for i in range(1, 3):
            Lesson.objects.get_or_create(
                module=module,
                order=i,
                defaults={
                    'title': f'{module.title} - Lesson {i}',
                    'description': f'Lesson {i} content',
                    'content_type': 'text',
                    'text_content': f'This is lesson {i} content for {module.title}.',
                    'duration_minutes': 15 + (i * 5),
                    'is_free': i == 1
                }
            )
    print(f"[OK] Created modules and lessons for: {course.title}")

# Create quizzes for published courses
print("\nCreating quizzes...")
for course in courses:
    if course.is_published:
        quiz, created = Quiz.objects.get_or_create(
            course=course,
            defaults={
                'title': f'{course.title} Quiz',
                'description': f'Test your knowledge of {course.title}',
                'time_limit_minutes': 30,
                'passing_score': 70,
                'max_attempts': 3,
                'is_active': True
            }
        )
        if created:
            # Create a simple question for each quiz
            q1, _ = Question.objects.get_or_create(
                quiz=quiz,
                order=1,
                defaults={
                    'question_text': f'What is the main topic of {course.title}?',
                    'question_type': 'multiple_choice',
                    'points': 1
                }
            )
            Choice.objects.get_or_create(question=q1, choice_text='Correct Answer', is_correct=True, order=1)
            Choice.objects.get_or_create(question=q1, choice_text='Wrong Answer 1', is_correct=False, order=2)
            Choice.objects.get_or_create(question=q1, choice_text='Wrong Answer 2', is_correct=False, order=3)
            print(f"[OK] Created quiz: {quiz.title}")

# Create enrollments
print("\nCreating enrollments...")
enrollment_count = 0
for course in courses:
    if course.is_published:
        # Enroll different numbers of students in each course
        num_enrollments = len(students) if course == courses[0] else len(students) - 1
        for i, student in enumerate(students[:num_enrollments]):
            enrollment, created = Enrollment.objects.get_or_create(
                student=student,
                course=course,
                defaults={
                    'enrolled_at': timezone.now() - timedelta(days=30-i*5),
                    'is_completed': i < 2  # First 2 students completed
                }
            )
            if created:
                enrollment_count += 1
                # Create some progress for enrolled students
                if enrollment.is_completed:
                    enrollment.completed_at = timezone.now() - timedelta(days=5-i)
                    enrollment.save()
                    # Mark all lessons as completed
                    for module in course.modules.all():
                        for lesson in module.lessons.all():
                            Progress.objects.get_or_create(
                                enrollment=enrollment,
                                lesson=lesson,
                                defaults={
                                    'is_completed': True,
                                    'completed_at': timezone.now() - timedelta(days=5-i),
                                    'time_spent_minutes': lesson.duration_minutes
                                }
                            )
                else:
                    # Mark some lessons as completed for active enrollments
                    for module in course.modules.all():
                        for j, lesson in enumerate(module.lessons.all()):
                            if j < 1:  # Complete first lesson only
                                Progress.objects.get_or_create(
                                    enrollment=enrollment,
                                    lesson=lesson,
                                    defaults={
                                        'is_completed': True,
                                        'completed_at': timezone.now() - timedelta(days=2),
                                        'time_spent_minutes': lesson.duration_minutes
                                    }
                                )
print(f"[OK] Created {enrollment_count} enrollments")

print("\n" + "="*50)
print("[OK] Test data creation complete!")
print("="*50)
print("\nTest Users:")
print(f"  Admin:      username=admin,      password=admin123")
print(f"  Instructor: username=instructor1, password=instructor123")
print(f"  Students:   username=student1-5,  password=student123")
print(f"\nTest Courses: {len(courses)}")
for course in courses:
    print(f"  - {course.title} ({'Published' if course.is_published else 'Draft'})")
    print(f"    Modules: {course.modules.count()}, Lessons: {course.total_lessons}")
    enrollments = Enrollment.objects.filter(course=course).count()
    print(f"    Enrollments: {enrollments}")





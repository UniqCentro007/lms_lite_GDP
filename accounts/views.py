from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import User
from .serializers import UserRegistrationSerializer, UserSerializer, UserProfileSerializer


class RegisterView(generics.CreateAPIView):
    """
    User registration endpoint.
    """
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegistrationSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """
    User login endpoint.
    Supports login with username, email, or user ID (for students).
    """
    login_identifier = request.data.get('username') or request.data.get('student_id') or request.data.get('email')
    password = request.data.get('password')
    
    if not login_identifier or not password:
        return Response(
            {'error': 'Username/Student ID/Email and password are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = None
    
    # Try to find user by different identifiers
    try:
        # First, try as username (default Django authentication)
        user = authenticate(username=login_identifier, password=password)
        
        # If not found, try as email
        if user is None:
            try:
                user_obj = User.objects.get(email=login_identifier)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
        
        # If still not found, try as user ID (for students)
        if user is None:
            try:
                user_id = int(login_identifier)
                user_obj = User.objects.get(id=user_id, role='student')
                user = authenticate(username=user_obj.username, password=password)
            except (ValueError, User.DoesNotExist):
                pass
                
    except Exception as e:
        pass
    
    if user is None:
        return Response(
            {'error': 'Invalid credentials. Use username, email, or student ID.'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    if not user.is_active:
        return Response(
            {'error': 'User account is disabled.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'user': UserSerializer(user).data,
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    })


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def student_login_view(request):
    """
    Student-only login endpoint.
    Supports login with username, email, or student ID.
    Only users with role='student' can login through this endpoint.
    """
    login_identifier = request.data.get('username') or request.data.get('student_id') or request.data.get('email')
    password = request.data.get('password')
    
    if not login_identifier or not password:
        return Response(
            {'error': 'Username/Student ID/Email and password are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = None
    
    # Try to find user by different identifiers
    try:
        # First, try as username (default Django authentication)
        user = authenticate(username=login_identifier, password=password)
        
        # If not found, try as email
        if user is None:
            try:
                user_obj = User.objects.get(email=login_identifier)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
        
        # If still not found, try as user ID (for students)
        if user is None:
            try:
                user_id = int(login_identifier)
                user_obj = User.objects.get(id=user_id, role='student')
                user = authenticate(username=user_obj.username, password=password)
            except (ValueError, User.DoesNotExist):
                pass
                
    except Exception as e:
        pass
    
    if user is None:
        return Response(
            {'error': 'Invalid credentials. Use username, email, or student ID.'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    if not user.is_active:
        return Response(
            {'error': 'User account is disabled.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Check if user is a student
    if not user.is_student:
        return Response(
            {'error': 'Access denied. Student privileges required.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'user': UserSerializer(user).data,
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        },
        'message': 'Student login successful'
    })


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def admin_login_view(request):
    """
    Admin-only login endpoint.
    Supports login with username or email.
    Only users with role='admin' can login through this endpoint.
    """
    login_identifier = request.data.get('username') or request.data.get('email')
    password = request.data.get('password')
    
    if not login_identifier or not password:
        return Response(
            {'error': 'Username/Email and password are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = None
    
    # Try to find user by different identifiers
    try:
        # First, try as username (default Django authentication)
        user = authenticate(username=login_identifier, password=password)
        
        # If not found, try as email
        if user is None:
            try:
                user_obj = User.objects.get(email=login_identifier)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
                
    except Exception as e:
        pass
    
    if user is None:
        return Response(
            {'error': 'Invalid credentials. Use username or email.'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    if not user.is_active:
        return Response(
            {'error': 'User account is disabled.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Check if user is an admin
    if not user.is_admin:
        return Response(
            {'error': 'Access denied. Admin privileges required.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'user': UserSerializer(user).data,
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        },
        'message': 'Admin login successful'
    })


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def instructor_login_view(request):
    """
    Instructor-only login endpoint.
    Supports login with username or email.
    Only users with role='instructor' can login through this endpoint.
    """
    login_identifier = request.data.get('username') or request.data.get('email')
    password = request.data.get('password')
    
    if not login_identifier or not password:
        return Response(
            {'error': 'Username/Email and password are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = None
    
    # Try to find user by different identifiers
    try:
        # First, try as username (default Django authentication)
        user = authenticate(username=login_identifier, password=password)
        
        # If not found, try as email
        if user is None:
            try:
                user_obj = User.objects.get(email=login_identifier)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
                
    except Exception as e:
        pass
    
    if user is None:
        return Response(
            {'error': 'Invalid credentials. Use username or email.'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    if not user.is_active:
        return Response(
            {'error': 'User account is disabled.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Check if user is an instructor
    if not user.is_instructor:
        return Response(
            {'error': 'Access denied. Instructor privileges required.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'user': UserSerializer(user).data,
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        },
        'message': 'Instructor login successful'
    })


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Get and update user profile.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class UserListView(generics.ListAPIView):
    """
    List all users (Admin only).
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return User.objects.all()
        elif user.is_instructor:
            # Instructors can see students enrolled in their courses
            from courses.models import Course
            instructor_courses = Course.objects.filter(instructor=user)
            from enrollments.models import Enrollment
            student_ids = Enrollment.objects.filter(
                course__in=instructor_courses
            ).values_list('student_id', flat=True).distinct()
            return User.objects.filter(id__in=student_ids)
        return User.objects.none()


@csrf_exempt
def student_login_page(request):
    """
    Simple HTML student login page using Django session authentication.
    This wraps similar logic to the API but via a form.
    """
    if request.method == "POST":
        login_identifier = (
            request.POST.get("username")
            or request.POST.get("student_id")
            or request.POST.get("email")
        )
        password = request.POST.get("password")

        if not login_identifier or not password:
            messages.error(
                request,
                "Username / Student ID / Email and password are required.",
            )
            return render(request, "student_login.html")

        user = None

        # Try username
        user = authenticate(username=login_identifier, password=password)

        # Try email
        if user is None:
            try:
                user_obj = User.objects.get(email=login_identifier)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass

        # Try student ID
        if user is None:
            try:
                user_id = int(login_identifier)
                user_obj = User.objects.get(id=user_id, role="student")
                user = authenticate(username=user_obj.username, password=password)
            except (ValueError, User.DoesNotExist):
                pass

        if user is None:
            messages.error(
                request,
                "Invalid credentials. Use username, email, or student ID.",
            )
            return render(request, "student_login.html")

        if not user.is_active:
            messages.error(request, "User account is disabled.")
            return render(request, "student_login.html")

        if not getattr(user, "is_student", False):
            messages.error(request, "Access denied. Student privileges required.")
            return render(request, "student_login.html")

        # Successful login: create session and redirect to student dashboard
        login(request, user)
        messages.success(request, f"Welcome, {user.username}!")
        return redirect("student_dashboard_page")

    # GET request: just render the form
    return render(request, "student_login.html")


@login_required
def student_dashboard_page(request):
    """
    Enhanced HTML dashboard shown after a successful student login.
    Assumes session-based auth from student_login_page.
    """
    user = request.user
    # Guard: only students should see this page
    if not getattr(user, "is_student", False):
        messages.error(request, "Only students can access this dashboard.")
        return redirect("student_login_page")

    # Show this student's course enrollments on the dashboard
    from enrollments.models import Enrollment, Progress
    from courses.models import Course
    from quizzes.models import Quiz, QuizResult

    enrollments = (
        Enrollment.objects.select_related("course", "course__instructor")
        .filter(student=user)
        .order_by("-enrolled_at")
    )
    
    # Get enrollment stats with progress
    enrollments_with_stats = []
    for enrollment in enrollments:
        progress = Progress.objects.filter(enrollment=enrollment)
        completed_lessons = progress.filter(is_completed=True).count()
        total_lessons = enrollment.course.total_lessons
        progress_percentage = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
        
        # Get quiz info if exists
        quiz = None
        quiz_result = None
        try:
            quiz = Quiz.objects.get(course=enrollment.course, is_active=True)
            quiz_result = QuizResult.objects.filter(
                student=user,
                quiz=quiz,
                enrollment=enrollment
            ).order_by('-started_at').first()
        except Quiz.DoesNotExist:
            pass
        
        enrollments_with_stats.append({
            'enrollment': enrollment,
            'course': enrollment.course,
            'progress_percentage': round(progress_percentage, 1),
            'completed_lessons': completed_lessons,
            'total_lessons': total_lessons,
            'quiz': quiz,
            'quiz_result': quiz_result,
        })
    
    # Get available courses (published courses not enrolled in)
    enrolled_course_ids = enrollments.values_list('course_id', flat=True)
    available_courses = Course.objects.filter(
        is_published=True
    ).exclude(id__in=enrolled_course_ids).select_related('instructor')[:10]
    
    # Get quiz results for enrolled courses
    quiz_results = QuizResult.objects.filter(
        student=user
    ).select_related('quiz', 'quiz__course').order_by('-started_at')[:5]

    return render(
        request,
        "student_dashboard.html",
        {
            "student": user,
            "enrollments_with_stats": enrollments_with_stats,
            "available_courses": available_courses,
            "quiz_results": quiz_results,
            "total_enrollments": enrollments.count(),
            "completed_courses": enrollments.filter(is_completed=True).count(),
            "active_courses": enrollments.filter(is_completed=False).count(),
        },
    )


@login_required
def enroll_course(request, course_id):
    """Enroll student in a course."""
    user = request.user
    if not getattr(user, "is_student", False):
        messages.error(request, "Only students can enroll in courses.")
        return redirect("student_dashboard_page")
    
    from courses.models import Course
    from enrollments.models import Enrollment
    
    try:
        course = Course.objects.get(id=course_id, is_published=True)
    except Course.DoesNotExist:
        messages.error(request, "Course not found or not available.")
        return redirect("student_dashboard_page")
    
    # Check if already enrolled
    enrollment, created = Enrollment.objects.get_or_create(
        student=user,
        course=course
    )
    
    if created:
        messages.success(request, f"Successfully enrolled in {course.title}!")
    else:
        messages.info(request, f"You are already enrolled in {course.title}.")
    
    return redirect("student_dashboard_page")


@login_required
def take_quiz_page(request, quiz_id):
    """Page for taking a quiz."""
    user = request.user
    if not getattr(user, "is_student", False):
        messages.error(request, "Only students can take quizzes.")
        return redirect("student_dashboard_page")
    
    from quizzes.models import Quiz, QuizResult
    from enrollments.models import Enrollment
    
    try:
        quiz = Quiz.objects.get(id=quiz_id, is_active=True)
    except Quiz.DoesNotExist:
        messages.error(request, "Quiz not found.")
        return redirect("student_dashboard_page")
    
    # Check enrollment
    enrollment = Enrollment.objects.filter(
        student=user,
        course=quiz.course
    ).first()
    
    if not enrollment:
        messages.error(request, "You must be enrolled in this course to take the quiz.")
        return redirect("student_dashboard_page")
    
    # Check attempt limit
    previous_attempts = QuizResult.objects.filter(
        student=user,
        quiz=quiz,
        enrollment=enrollment
    ).count()
    
    if quiz.max_attempts > 0 and previous_attempts >= quiz.max_attempts:
        messages.error(request, f"You have reached the maximum attempts ({quiz.max_attempts}) for this quiz.")
        return redirect("student_dashboard_page")
    
    # Get questions without correct answers
    questions = quiz.questions.all().order_by('order')
    questions_data = []
    for question in questions:
        choices_data = []
        for choice in question.choices.all().order_by('order'):
            choices_data.append({
                'id': choice.id,
                'text': choice.choice_text,
            })
        questions_data.append({
            'id': question.id,
            'text': question.question_text,
            'type': question.question_type,
            'points': question.points,
            'choices': choices_data,
        })
    
    return render(
        request,
        "take_quiz.html",
        {
            "quiz": quiz,
            "enrollment": enrollment,
            "questions": questions_data,
            "attempt_number": previous_attempts + 1,
            "max_attempts": quiz.max_attempts,
            "time_limit": quiz.time_limit_minutes,
        },
    )


@login_required
def submit_quiz(request, quiz_id):
    """Submit quiz answers."""
    user = request.user
    if not getattr(user, "is_student", False):
        return JsonResponse({'error': 'Only students can submit quizzes.'}, status=403)
    
    from quizzes.models import Quiz, QuizResult
    from quizzes.models import Answer
    from enrollments.models import Enrollment
    from django.utils import timezone
    import json
    
    try:
        quiz = Quiz.objects.get(id=quiz_id, is_active=True)
    except Quiz.DoesNotExist:
        return JsonResponse({'error': 'Quiz not found.'}, status=404)
    
    enrollment = Enrollment.objects.filter(
        student=user,
        course=quiz.course
    ).first()
    
    if not enrollment:
        return JsonResponse({'error': 'You must be enrolled in this course.'}, status=403)
    
    # Parse answers
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            answers_data = data.get('answers', {})
            time_taken = int(data.get('time_taken_minutes', 0))
        else:
            answers_data_str = request.POST.get('answers', '{}')
            answers_data = json.loads(answers_data_str) if isinstance(answers_data_str, str) else answers_data_str
            time_taken = int(request.POST.get('time_taken_minutes', 0))
    except Exception as e:
        return JsonResponse({'error': 'Invalid request data.'}, status=400)
    
    # Check attempt limit
    previous_attempts = QuizResult.objects.filter(
        student=user,
        quiz=quiz,
        enrollment=enrollment
    ).count()
    
    if quiz.max_attempts > 0 and previous_attempts >= quiz.max_attempts:
        return JsonResponse({'error': f'Maximum attempts reached.'}, status=400)
    
    # Create quiz result
    result = QuizResult.objects.create(
        student=user,
        quiz=quiz,
        enrollment=enrollment,
        attempt_number=previous_attempts + 1,
        time_taken_minutes=time_taken
    )
    
    # Calculate score
    total_points = 0
    earned_points = 0
    
    for question in quiz.questions.all():
        total_points += question.points
        question_id = str(question.id)
        
        if question_id not in answers_data:
            continue
        
        answer_data = answers_data[question_id]
        is_correct = False
        choice = None
        answer_text = None
        
        if question.question_type == 'multiple_choice':
            try:
                choice = question.choices.get(id=answer_data)
                is_correct = choice.is_correct
            except:
                is_correct = False
        
        elif question.question_type == 'true_false':
            correct_choice = question.choices.filter(is_correct=True).first()
            if correct_choice:
                is_correct = correct_choice.choice_text.lower() == str(answer_data).lower()
                choice = question.choices.filter(choice_text__iexact=str(answer_data)).first()
        
        elif question.question_type == 'short_answer':
            answer_text = str(answer_data)
            correct_choice = question.choices.filter(is_correct=True).first()
            if correct_choice:
                is_correct = correct_choice.choice_text.lower().strip() == answer_text.lower().strip()
        
        if is_correct:
            earned_points += question.points
        
        Answer.objects.create(
            result=result,
            question=question,
            choice=choice,
            answer_text=answer_text,
            is_correct=is_correct,
            points_earned=question.points if is_correct else 0
        )
    
    # Calculate final score
    result.score = earned_points
    result.percentage = (earned_points / total_points * 100) if total_points > 0 else 0
    result.is_passed = result.percentage >= quiz.passing_score
    result.completed_at = timezone.now()
    result.save()
    
    return JsonResponse({
        'success': True,
        'score': float(result.score),
        'total_points': total_points,
        'percentage': float(result.percentage),
        'is_passed': result.is_passed,
        'passing_score': quiz.passing_score,
    })


@csrf_exempt
def instructor_login_page(request):
    """
    Simple HTML instructor login page using Django session authentication.
    This wraps similar logic to the API but via a form.
    """
    if request.method == "POST":
        login_identifier = (
            request.POST.get("username")
            or request.POST.get("email")
        )
        password = request.POST.get("password")

        if not login_identifier or not password:
            messages.error(
                request,
                "Username / Email and password are required.",
            )
            return render(request, "instructor_login.html")

        user = None

        # Try username
        user = authenticate(username=login_identifier, password=password)

        # Try email
        if user is None:
            try:
                user_obj = User.objects.get(email=login_identifier)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass

        if user is None:
            messages.error(
                request,
                "Invalid credentials. Use username or email.",
            )
            return render(request, "instructor_login.html")

        if not user.is_active:
            messages.error(request, "User account is disabled.")
            return render(request, "instructor_login.html")

        if not getattr(user, "is_instructor", False):
            messages.error(request, "Access denied. Instructor privileges required.")
            return render(request, "instructor_login.html")

        # Successful login: create session and redirect to instructor dashboard
        login(request, user)
        messages.success(request, f"Welcome, {user.username}!")
        return redirect("instructor_dashboard_page")

    # GET request: just render the form
    return render(request, "instructor_login.html")


@login_required
def instructor_dashboard_page(request):
    """
    Very simple HTML dashboard shown after a successful instructor login.
    Assumes session-based auth from instructor_login_page.
    """
    user = request.user
    # Guard: only instructors should see this page
    if not getattr(user, "is_instructor", False):
        messages.error(request, "Only instructors can access this dashboard.")
        return redirect("instructor_login_page")

    # Show this instructor's courses and enrollments
    from courses.models import Course
    from enrollments.models import Enrollment

    courses = Course.objects.filter(instructor=user).order_by("-created_at")
    enrollments = Enrollment.objects.filter(
        course__instructor=user
    ).select_related("course", "student").order_by("-enrolled_at")

    # Calculate statistics
    total_courses = courses.count()
    published_courses = courses.filter(is_published=True).count()
    total_enrollments = enrollments.count()
    active_enrollments = enrollments.filter(is_completed=False).count()
    completed_enrollments = enrollments.filter(is_completed=True).count()

    # Add enrollment stats to each course
    courses_with_stats = []
    for course in courses:
        course_enrollments = enrollments.filter(course=course)
        course_total = course_enrollments.count()
        course_completed = course_enrollments.filter(is_completed=True).count()
        courses_with_stats.append({
            'course': course,
            'total_enrollments': course_total,
            'completed_enrollments': course_completed,
            'completion_rate': (course_completed / course_total * 100) if course_total > 0 else 0
        })

    return render(
        request,
        "instructor_dashboard.html",
        {
            "instructor": user,
            "courses_with_stats": courses_with_stats,
            "enrollments": enrollments,
            "total_courses": total_courses,
            "published_courses": published_courses,
            "total_enrollments": total_enrollments,
            "active_enrollments": active_enrollments,
            "completed_enrollments": completed_enrollments,
        },
    )


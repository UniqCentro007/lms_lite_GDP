from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
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
    Very simple HTML dashboard shown after a successful student login.
    Assumes session-based auth from student_login_page.
    """
    user = request.user
    # Guard: only students should see this page
    if not getattr(user, "is_student", False):
        messages.error(request, "Only students can access this dashboard.")
        return redirect("student_login_page")

    # Show this student's course enrollments on the dashboard
    from enrollments.models import Enrollment

    enrollments = (
        Enrollment.objects.select_related("course")
        .filter(student=user)
        .order_by("-enrolled_at")
    )
    courses = [e.course for e in enrollments]

    return render(
        request,
        "student_dashboard.html",
        {
            "student": user,
            "enrollments": enrollments,
            "courses": courses,
        },
    )


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

    return render(
        request,
        "instructor_dashboard.html",
        {
            "instructor": user,
            "courses": courses,
            "enrollments": enrollments,
            "total_courses": total_courses,
            "published_courses": published_courses,
            "total_enrollments": total_enrollments,
            "active_enrollments": active_enrollments,
            "completed_enrollments": completed_enrollments,
        },
    )


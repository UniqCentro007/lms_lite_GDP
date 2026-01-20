from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Enrollment, Progress
from .serializers import EnrollmentSerializer, EnrollmentListSerializer, ProgressSerializer
from courses.models import Course, Lesson


class EnrollmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing enrollments.
    """
    queryset = Enrollment.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['course', 'student', 'is_completed']
    ordering_fields = ['enrolled_at', 'completed_at']
    ordering = ['-enrolled_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return EnrollmentListSerializer
        return EnrollmentSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Enrollment.objects.all()
        elif user.is_instructor:
            # Instructors can see enrollments for their courses
            return Enrollment.objects.filter(course__instructor=user)
        else:
            # Students can see their own enrollments
            return Enrollment.objects.filter(student=user)
    
    def create(self, request, *args, **kwargs):
        """Enroll a student in a course."""
        course_id = request.data.get('course_id')
        if not course_id:
            return Response(
                {'error': 'course_id is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            course = Course.objects.get(id=course_id, is_published=True)
        except Course.DoesNotExist:
            return Response(
                {'error': 'Course not found or not published.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        enrollment, created = Enrollment.objects.get_or_create(
            student=request.user,
            course=course
        )
        
        if not created:
            return Response(
                {'error': 'You are already enrolled in this course.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(enrollment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):
        """Get detailed progress for an enrollment."""
        enrollment = self.get_object()
        progresses = enrollment.progresses.all()
        serializer = ProgressSerializer(progresses, many=True)
        return Response({
            'enrollment_id': enrollment.id,
            'course': enrollment.course.title,
            'progress_percentage': enrollment.progress_percentage,
            'lessons': serializer.data
        })


class ProgressViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing lesson progress.
    """
    queryset = Progress.objects.all()
    serializer_class = ProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        enrollment_id = self.request.query_params.get('enrollment_id')
        
        if enrollment_id:
            enrollments = Enrollment.objects.filter(id=enrollment_id)
            if user.is_student:
                enrollments = enrollments.filter(student=user)
            elif user.is_instructor:
                enrollments = enrollments.filter(course__instructor=user)
            return Progress.objects.filter(enrollment__in=enrollments)
        
        if user.is_student:
            return Progress.objects.filter(enrollment__student=user)
        elif user.is_instructor:
            return Progress.objects.filter(enrollment__course__instructor=user)
        elif user.is_admin:
            return Progress.objects.all()
        return Progress.objects.none()
    
    def create(self, request, *args, **kwargs):
        """Create or update progress for a lesson."""
        enrollment_id = request.data.get('enrollment_id')
        lesson_id = request.data.get('lesson_id')
        is_completed = request.data.get('is_completed', False)
        
        if not enrollment_id or not lesson_id:
            return Response(
                {'error': 'enrollment_id and lesson_id are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            enrollment = Enrollment.objects.get(id=enrollment_id)
            lesson = Lesson.objects.get(id=lesson_id)
        except (Enrollment.DoesNotExist, Lesson.DoesNotExist):
            return Response(
                {'error': 'Enrollment or lesson not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verify student owns the enrollment
        if request.user.is_student and enrollment.student != request.user:
            return Response(
                {'error': 'You can only update your own progress.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        progress, created = Progress.objects.get_or_create(
            enrollment=enrollment,
            lesson=lesson,
            defaults={'is_completed': is_completed}
        )
        
        if not created:
            progress.is_completed = is_completed
            progress.save()
        
        serializer = self.get_serializer(progress)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)





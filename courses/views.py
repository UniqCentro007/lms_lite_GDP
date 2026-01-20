from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Course, Module, Lesson
from .serializers import CourseSerializer, CourseListSerializer, ModuleSerializer, LessonSerializer
from .permissions import IsInstructorOrReadOnly, IsCourseInstructor


class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing courses.
    """
    queryset = Course.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['instructor', 'difficulty_level', 'is_published']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title', 'price']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CourseListSerializer
        return CourseSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsInstructorOrReadOnly()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsCourseInstructor()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Course.objects.all()
        elif user.is_instructor:
            return Course.objects.filter(instructor=user)
        else:
            # Students can see published courses
            return Course.objects.filter(is_published=True)
    
    @action(detail=True, methods=['get'])
    def modules(self, request, pk=None):
        """Get all modules for a course."""
        course = self.get_object()
        modules = course.modules.all()
        serializer = ModuleSerializer(modules, many=True)
        return Response(serializer.data)


class ModuleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing modules.
    """
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = [permissions.IsAuthenticated, IsCourseInstructor]
    
    def get_queryset(self):
        course_id = self.request.query_params.get('course_id')
        if course_id:
            return Module.objects.filter(course_id=course_id)
        user = self.request.user
        if user.is_admin:
            return Module.objects.all()
        elif user.is_instructor:
            return Module.objects.filter(course__instructor=user)
        return Module.objects.none()
    
    def perform_create(self, serializer):
        course_id = self.request.data.get('course')
        from .models import Course
        course = Course.objects.get(id=course_id)
        if course.instructor != self.request.user and not self.request.user.is_admin:
            raise permissions.PermissionDenied("You can only add modules to your own courses.")
        serializer.save()


class LessonViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing lessons.
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated, IsCourseInstructor]
    
    def get_queryset(self):
        module_id = self.request.query_params.get('module_id')
        if module_id:
            return Lesson.objects.filter(module_id=module_id)
        user = self.request.user
        if user.is_admin:
            return Lesson.objects.all()
        elif user.is_instructor:
            return Lesson.objects.filter(module__course__instructor=user)
        return Lesson.objects.none()
    
    def perform_create(self, serializer):
        module_id = self.request.data.get('module')
        from .models import Module
        module = Module.objects.get(id=module_id)
        if module.course.instructor != self.request.user and not self.request.user.is_admin:
            raise permissions.PermissionDenied("You can only add lessons to your own courses.")
        serializer.save()





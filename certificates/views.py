from rest_framework import viewsets, status, permissions  # pyright: ignore[reportMissingImports]
from rest_framework.decorators import action  # pyright: ignore[reportMissingImports]
from rest_framework.response import Response  # pyright: ignore[reportMissingImports]
from django_filters.rest_framework import DjangoFilterBackend  # pyright: ignore[reportMissingImports]
from rest_framework.filters import SearchFilter, OrderingFilter  # pyright: ignore[reportMissingImports]
from django.utils import timezone  # pyright: ignore[reportMissingImports]
from django.conf import settings  # pyright: ignore[reportMissingImports]
from .models import Certificate
from .serializers import CertificateSerializer, CertificateListSerializer
from enrollments.models import Enrollment
from quizzes.models import Quiz, QuizResult
from django.core.exceptions import ObjectDoesNotExist  # pyright: ignore[reportMissingImports]


class CertificateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing certificates.
    """
    queryset = Certificate.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['student', 'course', 'is_approved']
    search_fields = ['certificate_number', 'student__username', 'course__title']
    ordering_fields = ['issued_at']
    ordering = ['-issued_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CertificateListSerializer
        return CertificateSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'approve']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Certificate.objects.all()
        elif user.is_instructor:
            return Certificate.objects.filter(course__instructor=user)
        else:
            return Certificate.objects.filter(student=user)
    
    def create(self, request, *args, **kwargs):
        """Generate certificate for a completed course."""
        course_id = request.data.get('course_id')
        enrollment_id = request.data.get('enrollment_id')
        
        if not course_id or not enrollment_id:
            return Response(
                {'error': 'course_id and enrollment_id are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            enrollment = Enrollment.objects.get(
                id=enrollment_id,
                student=request.user,
                is_completed=True
            )
        except Enrollment.DoesNotExist:
            return Response(
                {'error': 'Enrollment not found or course not completed.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if certificate already exists
        certificate, created = Certificate.objects.get_or_create(
            student=request.user,
            course=enrollment.course,
            enrollment=enrollment,
            defaults={'is_approved': not settings.CERTIFICATE_REQUIRE_APPROVAL}
        )
        
        if not created:
            return Response(
                {'error': 'Certificate already exists for this course.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if quiz requirement is met
        # Safely access OneToOneField reverse relationship using getattr with exception handling
        quiz = None
        try:
            quiz = enrollment.course.quiz
        except (ObjectDoesNotExist, AttributeError):
            # If no quiz exists for this course, allow certificate generation
            pass
        
        # Only check quiz requirement if a quiz exists
        if quiz:
            quiz_result = QuizResult.objects.filter(
                student=request.user,
                quiz=quiz,
                enrollment=enrollment,
                is_passed=True
            ).first()
            
            if not quiz_result:
                certificate.delete()
                return Response(
                    {'error': 'You must pass the course quiz to receive a certificate.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Generate PDF certificate
        try:
            certificate.generate_pdf()
            certificate.save()
        except Exception as e:
            certificate.delete()
            return Response(
                {'error': f'Failed to generate certificate: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        serializer = self.get_serializer(certificate)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a certificate (Admin only)."""
        if not request.user.is_admin:
            return Response(
                {'error': 'Only admins can approve certificates.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        certificate = self.get_object()
        certificate.is_approved = True
        certificate.approved_by = request.user
        certificate.approved_at = timezone.now()
        certificate.save()
        
        serializer = self.get_serializer(certificate)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download certificate PDF."""
        certificate = self.get_object()
        
        # Check permissions
        if not certificate.is_approved and not request.user.is_admin:
            return Response(
                {'error': 'Certificate is not approved yet.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if certificate.student != request.user and not request.user.is_admin and not request.user.is_instructor:
            return Response(
                {'error': 'You do not have permission to download this certificate.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if not certificate.pdf_file:
            return Response(
                {'error': 'Certificate PDF not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        from django.http import FileResponse  # pyright: ignore[reportMissingImports]
        return FileResponse(
            certificate.pdf_file.open('rb'),
            content_type='application/pdf',
            filename=f"certificate_{certificate.certificate_number}.pdf"
        )





from rest_framework import views, status, permissions
from rest_framework.response import Response
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from accounts.models import User
from courses.models import Course
from enrollments.models import Enrollment, Progress
from quizzes.models import Quiz, QuizResult
from certificates.models import Certificate


class DashboardView(views.APIView):
    """
    Dashboard view providing aggregated statistics.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        if user.is_admin:
            return self._admin_dashboard()
        elif user.is_instructor:
            return self._instructor_dashboard(user)
        else:
            return self._student_dashboard(user)
    
    def _admin_dashboard(self):
        """Admin dashboard with platform-wide statistics."""
        total_students = User.objects.filter(role='student').count()
        total_instructors = User.objects.filter(role='instructor').count()
        total_courses = Course.objects.count()
        published_courses = Course.objects.filter(is_published=True).count()
        total_enrollments = Enrollment.objects.count()
        active_enrollments = Enrollment.objects.filter(is_completed=False).count()
        completed_enrollments = Enrollment.objects.filter(is_completed=True).count()
        total_certificates = Certificate.objects.filter(is_approved=True).count()
        
        # Recent enrollments (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_enrollments = Enrollment.objects.filter(
            enrolled_at__gte=thirty_days_ago
        ).count()
        
        # Course completion rate
        completion_rate = 0
        if total_enrollments > 0:
            completion_rate = round((completed_enrollments / total_enrollments) * 100, 2)
        
        # Top courses by enrollment
        top_courses = Course.objects.annotate(
            enrollment_count=Count('enrollments')
        ).order_by('-enrollment_count')[:5]
        
        top_courses_data = [
            {
                'id': course.id,
                'title': course.title,
                'enrollment_count': course.enrollment_count
            }
            for course in top_courses
        ]
        
        return Response({
            'users': {
                'total_students': total_students,
                'total_instructors': total_instructors,
            },
            'courses': {
                'total_courses': total_courses,
                'published_courses': published_courses,
            },
            'enrollments': {
                'total_enrollments': total_enrollments,
                'active_enrollments': active_enrollments,
                'completed_enrollments': completed_enrollments,
                'recent_enrollments': recent_enrollments,
                'completion_rate': completion_rate,
            },
            'certificates': {
                'total_issued': total_certificates,
            },
            'top_courses': top_courses_data,
        })
    
    def _instructor_dashboard(self, instructor):
        """Instructor dashboard with course-specific statistics."""
        instructor_courses = Course.objects.filter(instructor=instructor)
        total_courses = instructor_courses.count()
        published_courses = instructor_courses.filter(is_published=True).count()
        
        # Enrollment statistics
        enrollments = Enrollment.objects.filter(course__in=instructor_courses)
        total_enrollments = enrollments.count()
        active_enrollments = enrollments.filter(is_completed=False).count()
        completed_enrollments = enrollments.filter(is_completed=True).count()
        
        # Course-wise enrollment
        course_enrollments = instructor_courses.annotate(
            enrollment_count=Count('enrollments'),
            completed_count=Count('enrollments', filter=Q(enrollments__is_completed=True))
        ).values('id', 'title', 'enrollment_count', 'completed_count')
        
        # Quiz statistics
        quizzes = Quiz.objects.filter(course__in=instructor_courses)
        total_quizzes = quizzes.count()
        quiz_results = QuizResult.objects.filter(quiz__in=quizzes)
        avg_quiz_score = quiz_results.aggregate(avg_score=Avg('percentage'))['avg_score'] or 0
        
        # Certificate statistics
        certificates = Certificate.objects.filter(course__in=instructor_courses, is_approved=True)
        total_certificates = certificates.count()
        
        # Recent enrollments (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_enrollments = enrollments.filter(
            enrolled_at__gte=thirty_days_ago
        ).count()
        
        return Response({
            'courses': {
                'total_courses': total_courses,
                'published_courses': published_courses,
            },
            'enrollments': {
                'total_enrollments': total_enrollments,
                'active_enrollments': active_enrollments,
                'completed_enrollments': completed_enrollments,
                'recent_enrollments': recent_enrollments,
                'course_wise': list(course_enrollments),
            },
            'quizzes': {
                'total_quizzes': total_quizzes,
                'average_score': round(float(avg_quiz_score), 2),
            },
            'certificates': {
                'total_issued': total_certificates,
            },
        })
    
    def _student_dashboard(self, student):
        """Student dashboard with personal learning statistics."""
        enrollments = Enrollment.objects.filter(student=student)
        total_enrollments = enrollments.count()
        active_enrollments = enrollments.filter(is_completed=False).count()
        completed_enrollments = enrollments.filter(is_completed=True).count()
        
        # Progress statistics
        progresses = Progress.objects.filter(enrollment__in=enrollments)
        completed_lessons = progresses.filter(is_completed=True).count()
        total_lessons = progresses.count()
        
        # Quiz statistics
        quiz_results = QuizResult.objects.filter(student=student)
        total_quizzes_taken = quiz_results.count()
        passed_quizzes = quiz_results.filter(is_passed=True).count()
        avg_quiz_score = quiz_results.aggregate(avg_score=Avg('percentage'))['avg_score'] or 0
        
        # Certificate statistics
        certificates = Certificate.objects.filter(student=student, is_approved=True)
        total_certificates = certificates.count()
        
        # Recent activity
        recent_progress = progresses.order_by('-last_accessed_at')[:5]
        recent_progress_data = [
            {
                'lesson_title': progress.lesson.title,
                'course_title': progress.lesson.module.course.title,
                'is_completed': progress.is_completed,
                'last_accessed': progress.last_accessed_at,
            }
            for progress in recent_progress
        ]
        
        return Response({
            'enrollments': {
                'total_enrollments': total_enrollments,
                'active_enrollments': active_enrollments,
                'completed_enrollments': completed_enrollments,
            },
            'progress': {
                'completed_lessons': completed_lessons,
                'total_lessons': total_lessons,
                'completion_percentage': round((completed_lessons / total_lessons * 100), 2) if total_lessons > 0 else 0,
            },
            'quizzes': {
                'total_taken': total_quizzes_taken,
                'passed': passed_quizzes,
                'average_score': round(float(avg_quiz_score), 2),
            },
            'certificates': {
                'total_earned': total_certificates,
            },
            'recent_activity': recent_progress_data,
        })


class CoursePerformanceView(views.APIView):
    """
    Course performance report for instructors and admins.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, course_id):
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response(
                {'error': 'Course not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check permissions
        user = request.user
        if not user.is_admin and course.instructor != user:
            return Response(
                {'error': 'You do not have permission to view this report.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Enrollment statistics
        enrollments = Enrollment.objects.filter(course=course)
        total_enrollments = enrollments.count()
        completed_enrollments = enrollments.filter(is_completed=True).count()
        active_enrollments = enrollments.filter(is_completed=False).count()
        
        # Progress statistics
        progresses = Progress.objects.filter(enrollment__in=enrollments)
        avg_progress = enrollments.aggregate(
            avg_progress=Avg('progress_percentage')
        )['avg_progress'] or 0
        
        # Quiz statistics
        quiz_results = []
        avg_quiz_score = 0
        if hasattr(course, 'quiz') and course.quiz:
            quiz_results = QuizResult.objects.filter(quiz=course.quiz)
            avg_quiz_score = quiz_results.aggregate(
                avg_score=Avg('percentage')
            )['avg_score'] or 0
            passed_count = quiz_results.filter(is_passed=True).count()
        else:
            passed_count = 0
        
        # Module-wise progress
        module_progress = []
        for module in course.modules.all():
            module_lessons = module.lessons.count()
            completed_lessons = progresses.filter(
                lesson__module=module,
                is_completed=True
            ).count()
            module_progress.append({
                'module_id': module.id,
                'module_title': module.title,
                'total_lessons': module_lessons,
                'completed_lessons': completed_lessons,
                'completion_rate': round((completed_lessons / (module_lessons * total_enrollments) * 100), 2) if module_lessons > 0 and total_enrollments > 0 else 0,
            })
        
        return Response({
            'course': {
                'id': course.id,
                'title': course.title,
            },
            'enrollments': {
                'total': total_enrollments,
                'completed': completed_enrollments,
                'active': active_enrollments,
                'completion_rate': round((completed_enrollments / total_enrollments * 100), 2) if total_enrollments > 0 else 0,
            },
            'progress': {
                'average_progress': round(float(avg_progress), 2),
            },
            'quiz': {
                'total_attempts': quiz_results.count() if hasattr(course, 'quiz') and course.quiz else 0,
                'passed': passed_count,
                'average_score': round(float(avg_quiz_score), 2),
            },
            'module_progress': module_progress,
        })


class EnrollmentReportView(views.APIView):
    """
    Enrollment report with trends.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        if user.is_student:
            return Response(
                {'error': 'Students cannot access enrollment reports.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get date range (default: last 30 days)
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        if user.is_admin:
            enrollments = Enrollment.objects.filter(enrolled_at__gte=start_date)
        else:
            enrollments = Enrollment.objects.filter(
                course__instructor=user,
                enrolled_at__gte=start_date
            )
        
        # Daily enrollment count
        daily_enrollments = enrollments.extra(
            select={'day': 'date(enrolled_at)'}
        ).values('day').annotate(
            count=Count('id')
        ).order_by('day')
        
        # Course-wise enrollment
        course_enrollments = enrollments.values('course__title').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        return Response({
            'period_days': days,
            'total_enrollments': enrollments.count(),
            'daily_enrollments': list(daily_enrollments),
            'course_wise': list(course_enrollments),
        })


"""
URL configuration for lms_project project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import api_root
from accounts.views import (
    student_login_page, student_dashboard_page, 
    instructor_login_page, instructor_dashboard_page,
    enroll_course, take_quiz_page, submit_quiz
)

urlpatterns = [
    path('', api_root, name='api_root'),
    path('admin/', admin.site.urls),
    path('student/login/', student_login_page, name='student_login_page'),
    path('student/dashboard/', student_dashboard_page, name='student_dashboard_page'),
    path('student/enroll/<int:course_id>/', enroll_course, name='enroll_course'),
    path('student/quiz/<int:quiz_id>/', take_quiz_page, name='take_quiz_page'),
    path('student/quiz/<int:quiz_id>/submit/', submit_quiz, name='submit_quiz'),
    path('instructor/login/', instructor_login_page, name='instructor_login_page'),
    path('instructor/dashboard/', instructor_dashboard_page, name='instructor_dashboard_page'),
    path('api/auth/', include('accounts.urls')),
    path('api/courses/', include('courses.urls')),
    path('api/enrollments/', include('enrollments.urls')),
    path('api/quizzes/', include('quizzes.urls')),
    path('api/certificates/', include('certificates.urls')),
    path('api/reports/', include('reports.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


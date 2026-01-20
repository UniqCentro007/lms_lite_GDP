from django.urls import path
from .views import DashboardView, CoursePerformanceView, EnrollmentReportView

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('course/<int:course_id>/performance/', CoursePerformanceView.as_view(), name='course_performance'),
    path('enrollments/', EnrollmentReportView.as_view(), name='enrollment_report'),
]





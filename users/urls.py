from django.urls import path
from .views import InstructorRegisterView, InstructorLoginView, InstructorDashboardView


urlpatterns = [
    path('instructor/register/', InstructorRegisterView.as_view()),
    path('instructor/login/', InstructorLoginView.as_view()),
    path('instructor/dashboard/', InstructorDashboardView.as_view()),
]

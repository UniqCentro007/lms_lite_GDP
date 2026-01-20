from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, login_view, student_login_view, admin_login_view, instructor_login_view, UserProfileView, UserListView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', login_view, name='login'),
    path('student/login/', student_login_view, name='student_login'),
    path('instructor/login/', instructor_login_view, name='instructor_login'),
    path('admin/login/', admin_login_view, name='admin_login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('users/', UserListView.as_view(), name='user_list'),
]



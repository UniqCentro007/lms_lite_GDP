from django.http import JsonResponse  # pyright: ignore[reportMissingImports]
from django.urls import get_resolver  # pyright: ignore[reportMissingImports]

def api_root(request):
    """
    Root API endpoint showing available endpoints.
    """
    resolver = get_resolver()
    url_patterns = []
    
    def extract_urls(url_patterns_list, prefix=''):
        for pattern in url_patterns_list:
            if hasattr(pattern, 'url_patterns'):
                extract_urls(pattern.url_patterns, prefix + str(pattern.pattern))
            else:
                url_patterns.append({
                    'pattern': prefix + str(pattern.pattern),
                    'name': getattr(pattern, 'name', None)
                })
    
    extract_urls(resolver.url_patterns)
    
    endpoints = {
        'message': 'LMS Lite API',
        'version': '1.0',
        'endpoints': {
            'authentication': {
                'register': '/api/auth/register/',
                'login': '/api/auth/login/',
                'token_refresh': '/api/auth/token/refresh/',
                'profile': '/api/auth/profile/',
                'users': '/api/auth/users/',
            },
            'courses': {
                'list': '/api/courses/',
                'detail': '/api/courses/{id}/',
                'modules': '/api/courses/modules/',
                'lessons': '/api/courses/lessons/',
            },
            'enrollments': {
                'list': '/api/enrollments/',
                'detail': '/api/enrollments/{id}/',
                'progress': '/api/enrollments/progress/',
            },
            'quizzes': {
                'list': '/api/quizzes/',
                'detail': '/api/quizzes/{id}/',
                'questions': '/api/quizzes/{id}/questions/',
                'submit': '/api/quizzes/{id}/submit/',
                'results': '/api/quizzes/results/',
            },
            'certificates': {
                'list': '/api/certificates/',
                'detail': '/api/certificates/{id}/',
                'download': '/api/certificates/{id}/download/',
            },
            'reports': {
                'dashboard': '/api/reports/dashboard/',
                'course_performance': '/api/reports/course/{id}/performance/',
                'enrollments': '/api/reports/enrollments/',
            },
            'admin': '/admin/',
        }
    }
    
    return JsonResponse(endpoints, json_dumps_params={'indent': 2})





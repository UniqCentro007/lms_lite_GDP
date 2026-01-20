from rest_framework import serializers
from .models import Certificate
from courses.serializers import CourseListSerializer
from accounts.serializers import UserSerializer


class CertificateSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    course = CourseListSerializer(read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = Certificate
        fields = '__all__'
        read_only_fields = ('certificate_number', 'pdf_file', 'issued_at', 'approved_at', 'approved_by')


class CertificateListSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    pdf_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Certificate
        fields = ('id', 'student_name', 'course_title', 'certificate_number', 
                  'is_approved', 'issued_at', 'pdf_url')
    
    def get_pdf_url(self, obj):
        if obj.pdf_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.pdf_file.url)
        return None





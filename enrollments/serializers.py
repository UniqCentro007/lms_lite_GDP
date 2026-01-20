from rest_framework import serializers
from .models import Enrollment, Progress
from courses.serializers import CourseListSerializer, LessonSerializer
from accounts.serializers import UserSerializer


class ProgressSerializer(serializers.ModelSerializer):
    lesson = LessonSerializer(read_only=True)
    lesson_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Progress
        fields = '__all__'
        read_only_fields = ('completed_at', 'last_accessed_at')


class EnrollmentSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    course = CourseListSerializer(read_only=True)
    course_id = serializers.IntegerField(write_only=True)
    progress_percentage = serializers.FloatField(read_only=True)
    progresses = ProgressSerializer(many=True, read_only=True)
    
    class Meta:
        model = Enrollment
        fields = '__all__'
        read_only_fields = ('enrolled_at', 'completed_at', 'is_completed', 'student')
    
    def create(self, validated_data):
        validated_data['student'] = self.context['request'].user
        return super().create(validated_data)


class EnrollmentListSerializer(serializers.ModelSerializer):
    course = CourseListSerializer(read_only=True)
    progress_percentage = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Enrollment
        fields = ('id', 'course', 'enrolled_at', 'completed_at', 
                  'is_completed', 'progress_percentage')





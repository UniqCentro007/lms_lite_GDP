from rest_framework import serializers
from .models import Course, Module, Lesson
from accounts.serializers import UserSerializer


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    lesson_count = serializers.IntegerField(source='lessons.count', read_only=True)
    
    class Meta:
        model = Module
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class CourseSerializer(serializers.ModelSerializer):
    instructor = UserSerializer(read_only=True)
    instructor_id = serializers.IntegerField(write_only=True, required=False)
    modules = ModuleSerializer(many=True, read_only=True)
    total_modules = serializers.IntegerField(read_only=True)
    total_lessons = serializers.IntegerField(read_only=True)
    enrollment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'instructor')
    
    def get_enrollment_count(self, obj):
        return obj.enrollments.count()
    
    def create(self, validated_data):
        instructor_id = validated_data.pop('instructor_id', None)
        if instructor_id:
            from accounts.models import User
            instructor = User.objects.get(id=instructor_id)
            validated_data['instructor'] = instructor
        else:
            validated_data['instructor'] = self.context['request'].user
        return super().create(validated_data)


class CourseListSerializer(serializers.ModelSerializer):
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    total_modules = serializers.IntegerField(read_only=True)
    total_lessons = serializers.IntegerField(read_only=True)
    enrollment_count = serializers.IntegerField(source='enrollments.count', read_only=True)
    
    class Meta:
        model = Course
        fields = ('id', 'title', 'description', 'instructor_name', 'thumbnail', 
                  'price', 'duration_hours', 'difficulty_level', 'is_published',
                  'total_modules', 'total_lessons', 'enrollment_count', 'created_at')





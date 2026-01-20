from rest_framework import serializers
from .models import Quiz, Question, Choice, QuizResult, Answer
from courses.serializers import CourseListSerializer
from accounts.serializers import UserSerializer


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = '__all__'


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = '__all__'
        read_only_fields = ('created_at',)


class QuestionWithAnswersSerializer(serializers.ModelSerializer):
    """
    Serializer for questions with correct answers (for instructors/admins).
    """
    choices = ChoiceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = '__all__'


class QuizSerializer(serializers.ModelSerializer):
    course = CourseListSerializer(read_only=True)
    questions = QuestionSerializer(many=True, read_only=True)
    total_questions = serializers.IntegerField(read_only=True)
    total_points = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Quiz
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class QuizListSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    total_questions = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Quiz
        fields = ('id', 'course', 'course_title', 'title', 'description', 
                  'time_limit_minutes', 'passing_score', 'max_attempts', 
                  'is_active', 'total_questions', 'created_at')


class AnswerSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source='question.question_text', read_only=True)
    
    class Meta:
        model = Answer
        fields = '__all__'
        read_only_fields = ('is_correct', 'points_earned')


class QuizResultSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    quiz = QuizListSerializer(read_only=True)
    answers = AnswerSerializer(many=True, read_only=True)
    
    class Meta:
        model = QuizResult
        fields = '__all__'
        read_only_fields = ('score', 'percentage', 'is_passed', 'started_at', 'completed_at')


class QuizResultListSerializer(serializers.ModelSerializer):
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    
    class Meta:
        model = QuizResult
        fields = ('id', 'quiz_title', 'student_name', 'score', 'percentage', 
                  'is_passed', 'attempt_number', 'completed_at')


class QuizSubmissionSerializer(serializers.Serializer):
    """
    Serializer for submitting quiz answers.
    """
    enrollment_id = serializers.IntegerField()
    answers = serializers.DictField(
        child=serializers.CharField(),
        help_text="Format: {question_id: answer}"
    )
    time_taken_minutes = serializers.IntegerField(default=0)





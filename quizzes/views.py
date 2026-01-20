from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from .models import Quiz, Question, Choice, QuizResult, Answer
from .serializers import (
    QuizSerializer, QuizListSerializer, QuestionSerializer, QuestionWithAnswersSerializer,
    QuizResultSerializer, QuizResultListSerializer, QuizSubmissionSerializer, AnswerSerializer
)
from enrollments.models import Enrollment


class QuizViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing quizzes.
    """
    queryset = Quiz.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['course', 'is_active']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return QuizListSerializer
        return QuizSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Quiz.objects.all()
        elif user.is_instructor:
            return Quiz.objects.filter(course__instructor=user)
        else:
            # Students can see quizzes for courses they're enrolled in
            enrolled_courses = Enrollment.objects.filter(
                student=user
            ).values_list('course_id', flat=True)
            return Quiz.objects.filter(course_id__in=enrolled_courses, is_active=True)
    
    @action(detail=True, methods=['get'])
    def questions(self, request, pk=None):
        """Get quiz questions (without correct answers for students)."""
        quiz = self.get_object()
        user = request.user
        
        # Check if user is enrolled
        if user.is_student:
            enrollment = Enrollment.objects.filter(
                student=user,
                course=quiz.course
            ).first()
            if not enrollment:
                return Response(
                    {'error': 'You must be enrolled in this course to view the quiz.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Show correct answers only to instructors and admins
        if user.is_instructor or user.is_admin:
            serializer = QuestionWithAnswersSerializer(quiz.questions.all(), many=True)
        else:
            serializer = QuestionSerializer(quiz.questions.all(), many=True)
        
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Submit quiz answers and calculate score."""
        quiz = self.get_object()
        user = request.user
        
        if not user.is_student:
            return Response(
                {'error': 'Only students can submit quizzes.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        submission_serializer = QuizSubmissionSerializer(data=request.data)
        submission_serializer.is_valid(raise_exception=True)
        
        enrollment_id = submission_serializer.validated_data['enrollment_id']
        answers = submission_serializer.validated_data['answers']
        time_taken = submission_serializer.validated_data.get('time_taken_minutes', 0)
        
        try:
            enrollment = Enrollment.objects.get(id=enrollment_id, student=user, course=quiz.course)
        except Enrollment.DoesNotExist:
            return Response(
                {'error': 'Enrollment not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check attempt limit
        previous_attempts = QuizResult.objects.filter(
            student=user,
            quiz=quiz,
            enrollment=enrollment
        ).count()
        
        if quiz.max_attempts > 0 and previous_attempts >= quiz.max_attempts:
            return Response(
                {'error': f'Maximum attempts ({quiz.max_attempts}) reached for this quiz.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create quiz result
        result = QuizResult.objects.create(
            student=user,
            quiz=quiz,
            enrollment=enrollment,
            attempt_number=previous_attempts + 1,
            time_taken_minutes=time_taken
        )
        
        # Save individual answers and calculate score
        total_points = 0
        earned_points = 0
        
        for question in quiz.questions.all():
            total_points += question.points
            question_id = str(question.id)
            
            if question_id not in answers:
                continue
            
            answer_data = answers[question_id]
            is_correct = False
            choice = None
            answer_text = None
            
            if question.question_type == 'multiple_choice':
                try:
                    choice = Choice.objects.get(id=answer_data, question=question)
                    is_correct = choice.is_correct
                except (Choice.DoesNotExist, ValueError):
                    is_correct = False
            
            elif question.question_type == 'true_false':
                correct_choice = question.choices.filter(is_correct=True).first()
                if correct_choice:
                    is_correct = correct_choice.choice_text.lower() == str(answer_data).lower()
                    choice = question.choices.filter(choice_text__iexact=str(answer_data)).first()
            
            elif question.question_type == 'short_answer':
                answer_text = str(answer_data)
                correct_choice = question.choices.filter(is_correct=True).first()
                if correct_choice:
                    is_correct = correct_choice.choice_text.lower().strip() == answer_text.lower().strip()
            
            if is_correct:
                earned_points += question.points
            
            Answer.objects.create(
                result=result,
                question=question,
                choice=choice,
                answer_text=answer_text,
                is_correct=is_correct,
                points_earned=question.points if is_correct else 0
            )
        
        # Calculate final score
        result.score = earned_points
        result.percentage = (earned_points / total_points * 100) if total_points > 0 else 0
        result.is_passed = result.percentage >= quiz.passing_score
        result.completed_at = timezone.now()
        result.save()
        
        serializer = QuizResultSerializer(result)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class QuestionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing quiz questions.
    """
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        quiz_id = self.request.query_params.get('quiz_id')
        if quiz_id:
            return Question.objects.filter(quiz_id=quiz_id)
        user = self.request.user
        if user.is_admin:
            return Question.objects.all()
        elif user.is_instructor:
            return Question.objects.filter(quiz__course__instructor=user)
        return Question.objects.none()


class QuizResultViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing quiz results.
    """
    queryset = QuizResult.objects.all()
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['quiz', 'student', 'enrollment', 'is_passed']
    ordering_fields = ['started_at', 'score', 'percentage']
    ordering = ['-started_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return QuizResultListSerializer
        return QuizResultSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return QuizResult.objects.all()
        elif user.is_instructor:
            return QuizResult.objects.filter(quiz__course__instructor=user)
        else:
            return QuizResult.objects.filter(student=user)





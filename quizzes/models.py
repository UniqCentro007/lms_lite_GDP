from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Quiz(models.Model):
    """
    Quiz model mapped to courses.
    """
    course = models.OneToOneField(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='quiz'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    time_limit_minutes = models.PositiveIntegerField(
        default=30,
        help_text="Time limit in minutes (0 for no limit)"
    )
    passing_score = models.PositiveIntegerField(
        default=70,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Minimum score percentage required to pass"
    )
    max_attempts = models.PositiveIntegerField(
        default=3,
        help_text="Maximum number of attempts allowed (0 for unlimited)"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'quizzes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
    @property
    def total_questions(self):
        return self.questions.count()
    
    @property
    def total_points(self):
        return sum(question.points for question in self.questions.all())


class Question(models.Model):
    """
    Question model for quiz questions.
    """
    QUESTION_TYPE_CHOICES = [
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('short_answer', 'Short Answer'),
    ]
    
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    question_text = models.TextField()
    question_type = models.CharField(
        max_length=20,
        choices=QUESTION_TYPE_CHOICES,
        default='multiple_choice'
    )
    points = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'questions'
        ordering = ['quiz', 'order']
        unique_together = ['quiz', 'order']
    
    def __str__(self):
        return f"{self.quiz.title} - Question {self.order}"


class Choice(models.Model):
    """
    Choice model for multiple choice and true/false questions.
    """
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='choices'
    )
    choice_text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=1)
    
    class Meta:
        db_table = 'choices'
        ordering = ['question', 'order']
    
    def __str__(self):
        return f"{self.question.question_text[:50]}... - {self.choice_text}"


class QuizResult(models.Model):
    """
    Quiz result model storing student quiz attempts and scores.
    """
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quiz_results',
        limit_choices_to={'role': 'student'}
    )
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='results'
    )
    enrollment = models.ForeignKey(
        'enrollments.Enrollment',
        on_delete=models.CASCADE,
        related_name='quiz_results'
    )
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00
    )
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    is_passed = models.BooleanField(default=False)
    attempt_number = models.PositiveIntegerField(default=1)
    time_taken_minutes = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'quiz_results'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.student.username} - {self.quiz.title} - Attempt {self.attempt_number}"
    
    def calculate_score(self, answers):
        """
        Calculate score based on submitted answers.
        answers format: {question_id: answer_data}
        """
        total_points = 0
        earned_points = 0
        
        for question in self.quiz.questions.all():
            total_points += question.points
            question_id = str(question.id)
            
            if question_id not in answers:
                continue
            
            answer_data = answers[question_id]
            is_correct = False
            
            if question.question_type == 'multiple_choice':
                # For multiple choice, answer should be choice ID
                choice_id = answer_data
                try:
                    choice = Choice.objects.get(id=choice_id, question=question)
                    is_correct = choice.is_correct
                except Choice.DoesNotExist:
                    is_correct = False
            
            elif question.question_type == 'true_false':
                # For true/false, answer should be boolean
                is_correct = question.choices.filter(
                    is_correct=True,
                    choice_text__iexact=str(answer_data)
                ).exists()
            
            elif question.question_type == 'short_answer':
                # For short answer, compare with correct answer (case-insensitive)
                correct_answer = question.choices.filter(is_correct=True).first()
                if correct_answer:
                    is_correct = correct_answer.choice_text.lower().strip() == str(answer_data).lower().strip()
            
            if is_correct:
                earned_points += question.points
        
        self.score = earned_points
        self.percentage = (earned_points / total_points * 100) if total_points > 0 else 0
        self.is_passed = self.percentage >= self.quiz.passing_score
        self.save()
        
        return {
            'score': float(self.score),
            'total_points': total_points,
            'percentage': float(self.percentage),
            'is_passed': self.is_passed
        }


class Answer(models.Model):
    """
    Answer model storing individual question answers in a quiz attempt.
    """
    result = models.ForeignKey(
        QuizResult,
        on_delete=models.CASCADE,
        related_name='answers'
    )
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(
        Choice,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        help_text="For multiple choice and true/false questions"
    )
    answer_text = models.TextField(
        blank=True,
        null=True,
        help_text="For short answer questions"
    )
    is_correct = models.BooleanField(default=False)
    points_earned = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    class Meta:
        db_table = 'answers'
        unique_together = ['result', 'question']
    
    def __str__(self):
        return f"{self.result} - {self.question.question_text[:50]}..."





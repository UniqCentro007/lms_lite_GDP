from django.contrib import admin
from .models import Quiz, Question, Choice, QuizResult, Answer


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'passing_score', 'max_attempts', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'description', 'course__title')
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'quiz', 'question_type', 'points', 'order')
    list_filter = ('question_type', 'quiz')
    search_fields = ('question_text',)
    inlines = [ChoiceInline]


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('choice_text', 'question', 'is_correct', 'order')
    list_filter = ('is_correct',)


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    readonly_fields = ('is_correct', 'points_earned')


@admin.register(QuizResult)
class QuizResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'quiz', 'score', 'percentage', 'is_passed', 'attempt_number', 'completed_at')
    list_filter = ('is_passed', 'completed_at', 'quiz')
    search_fields = ('student__username', 'quiz__title')
    readonly_fields = ('started_at', 'completed_at')
    inlines = [AnswerInline]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('result', 'question', 'is_correct', 'points_earned')
    list_filter = ('is_correct',)
    readonly_fields = ('is_correct', 'points_earned')





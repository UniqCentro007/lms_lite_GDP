from django.contrib import admin
from .models import Enrollment, Progress


class ProgressInline(admin.TabularInline):
    model = Progress
    extra = 0
    readonly_fields = ('completed_at', 'last_accessed_at')


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at', 'is_completed', 'completed_at')
    list_filter = ('is_completed', 'enrolled_at', 'course')
    search_fields = ('student__username', 'course__title')
    readonly_fields = ('enrolled_at', 'completed_at')
    inlines = [ProgressInline]


@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'lesson', 'is_completed', 'completed_at', 'time_spent_minutes')
    list_filter = ('is_completed', 'completed_at')
    search_fields = ('enrollment__student__username', 'lesson__title')
    readonly_fields = ('completed_at', 'last_accessed_at')





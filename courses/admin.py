from django.contrib import admin
from .models import Course, Module, Lesson


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1


class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'difficulty_level', 'is_published', 'created_at')
    list_filter = ('is_published', 'difficulty_level', 'created_at')
    search_fields = ('title', 'description', 'instructor__username')
    inlines = [ModuleInline]


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'created_at')
    list_filter = ('course', 'created_at')
    search_fields = ('title', 'description')
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'content_type', 'order', 'duration_minutes', 'created_at')
    list_filter = ('content_type', 'is_free', 'created_at')
    search_fields = ('title', 'description')





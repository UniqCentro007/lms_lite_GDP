from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Enrollment(models.Model):
    """
    Enrollment model tracking student enrollments in courses.
    """
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments',
        limit_choices_to={'role': 'student'}
    )
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'enrollments'
        unique_together = ['student', 'course']
        ordering = ['-enrolled_at']
    
    def __str__(self):
        return f"{self.student.username} - {self.course.title}"
    
    @property
    def progress_percentage(self):
        """Calculate overall progress percentage for the course."""
        total_lessons = self.course.total_lessons
        if total_lessons == 0:
            return 0
        completed_lessons = self.progresses.filter(is_completed=True).count()
        return round((completed_lessons / total_lessons) * 100, 2)
    
    def update_completion_status(self):
        """Update enrollment completion status based on lesson progress."""
        total_lessons = self.course.total_lessons
        completed_lessons = self.progresses.filter(is_completed=True).count()
        
        if total_lessons > 0 and completed_lessons == total_lessons:
            self.is_completed = True
            from django.utils import timezone
            if not self.completed_at:
                self.completed_at = timezone.now()
            self.save()


class Progress(models.Model):
    """
    Progress model tracking student progress at lesson level.
    """
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='progresses'
    )
    lesson = models.ForeignKey(
        'courses.Lesson',
        on_delete=models.CASCADE,
        related_name='progresses'
    )
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)
    last_accessed_at = models.DateTimeField(auto_now=True)
    time_spent_minutes = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'progress'
        unique_together = ['enrollment', 'lesson']
        ordering = ['lesson__module__order', 'lesson__order']
    
    def __str__(self):
        return f"{self.enrollment.student.username} - {self.lesson.title}"
    
    def save(self, *args, **kwargs):
        if self.is_completed and not self.completed_at:
            from django.utils import timezone
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)
        # Update enrollment completion status
        self.enrollment.update_completion_status()





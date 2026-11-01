# apps/enrollments/models.py
from django.db import models
from django.conf import settings
from apps.courses.models import Course, Lesson
import uuid

class Enrollment(models.Model):
    """Tracks a student's enrollment in a course."""
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    progress_percent = models.FloatField(default=0.0)

    class Meta:
        verbose_name = "اشتراك"
        verbose_name_plural = "الاشتراكات"
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student} - {self.course}"

class LessonProgress(models.Model):
    """Tracks progress for individual lessons."""
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='lesson_progresses')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progresses')
    is_completed = models.BooleanField(default=False)
    watched_seconds = models.PositiveIntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "تقدم الدرس"
        verbose_name_plural = "تقدم الدروس"
        unique_together = ('enrollment', 'lesson')

    def __str__(self):
        return f"{self.enrollment.student} - {self.lesson.title}"

class Certificate(models.Model):
    """Certificate issued upon course completion."""
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name='certificate')
    issued_at = models.DateTimeField(auto_now_add=True)
    certificate_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        verbose_name = "شهادة"
        verbose_name_plural = "الشهادات"

    def __str__(self):
        return f"Certificate {self.certificate_id} - {self.enrollment}"

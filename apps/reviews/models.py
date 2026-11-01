# apps/reviews/models.py
from django.db import models
from django.conf import settings
from apps.courses.models import Course

class Review(models.Model):
    """Student reviews for courses."""
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews', verbose_name="الطالب")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews', verbose_name="الكورس")
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)], verbose_name="التقييم (1-5)")
    comment = models.TextField(verbose_name="التعليق")
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True, verbose_name="معتمد")

    class Meta:
        verbose_name = "تقييم"
        verbose_name_plural = "التقييمات"
        unique_together = ('student', 'course')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student} - {self.course} ({self.rating}/5)"

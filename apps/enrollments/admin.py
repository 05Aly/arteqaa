# apps/enrollments/admin.py
from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Enrollment, LessonProgress, Certificate

@admin.register(Enrollment)
class EnrollmentAdmin(ModelAdmin):
    list_display = ('student', 'course', 'progress_percent', 'is_completed', 'enrolled_at')
    list_filter = ('is_completed', 'course')
    search_fields = ('student__email', 'student__first_name', 'course__title')
    readonly_fields = ('enrolled_at', 'completed_at')

@admin.register(LessonProgress)
class LessonProgressAdmin(ModelAdmin):
    list_display = ('enrollment', 'lesson', 'is_completed', 'watched_seconds')
    list_filter = ('is_completed',)
    search_fields = ('enrollment__student__email', 'lesson__title')

@admin.register(Certificate)
class CertificateAdmin(ModelAdmin):
    list_display = ('certificate_id', 'enrollment', 'issued_at')
    search_fields = ('certificate_id', 'enrollment__student__email')
    readonly_fields = ('certificate_id', 'issued_at')

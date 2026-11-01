# apps/reviews/admin.py
from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Review

@admin.register(Review)
class ReviewAdmin(ModelAdmin):
    list_display = ('student', 'course', 'rating', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_approved', 'course')
    search_fields = ('student__email', 'course__title', 'comment')
    list_editable = ('is_approved',)

# apps/courses/admin.py
from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline, StackedInline
from .models import Course, Section, Lesson, Resource

class ResourceInline(TabularInline):
    model = Resource
    extra = 1

class LessonInline(StackedInline):
    model = Lesson
    extra = 1
    show_change_link = True

class SectionInline(StackedInline):
    model = Section
    extra = 1
    show_change_link = True

@admin.register(Course)
class CourseAdmin(ModelAdmin):
    list_display = ('title', 'instructor', 'category', 'price', 'status', 'level', 'is_featured')
    list_filter = ('status', 'level', 'category', 'is_featured')
    search_fields = ('title', 'description', 'instructor__email')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')
    inlines = [SectionInline]

@admin.register(Section)
class SectionAdmin(ModelAdmin):
    list_display = ('title', 'course', 'order')
    list_filter = ('course',)
    search_fields = ('title', 'course__title')
    inlines = [LessonInline]

@admin.register(Lesson)
class LessonAdmin(ModelAdmin):
    list_display = ('title', 'section', 'duration_seconds', 'is_preview', 'order')
    list_filter = ('is_preview', 'section__course')
    search_fields = ('title', 'section__title')
    inlines = [ResourceInline]

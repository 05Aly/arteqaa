from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline, StackedInline
from .models import (Category, Course, Module, Lesson, Enrollment,
                     Quiz, Question, Answer, Review, Announcement, Comment)


class LessonInline(TabularInline):
    model = Lesson
    extra = 1
    fk_name = 'module'
    fields = ('title', 'order', 'duration', 'is_preview', 'video_url')

class DirectLessonInline(TabularInline):
    model = Lesson
    extra = 1
    fk_name = 'course'
    fields = ('title', 'order', 'duration', 'is_preview', 'video_url')


class ModuleInline(StackedInline):
    model = Module
    extra = 0
    fields = ('title', 'order')
    show_change_link = True


class AnnouncementInline(StackedInline):
    model = Announcement
    extra = 0
    fields = ('title', 'content', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ('name', 'slug', 'description')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    list_fullwidth = True


@admin.register(Course)
class CourseAdmin(ModelAdmin):
    list_display = ('title', 'instructor', 'category', 'price', 'created_at')
    list_filter = ('category', 'instructor')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ModuleInline, DirectLessonInline, AnnouncementInline]
    list_fullwidth = True
    date_hierarchy = 'created_at'


@admin.register(Module)
class ModuleAdmin(ModelAdmin):
    list_display = ('title', 'course', 'order')
    list_filter = ('course',)
    search_fields = ('title', 'course__title')
    inlines = [LessonInline]
    list_fullwidth = True


@admin.register(Lesson)
class LessonAdmin(ModelAdmin):
    list_display = ('title', 'course', 'module', 'order', 'duration', 'is_preview')
    list_filter = ('is_preview', 'course', 'module__course')
    search_fields = ('title', 'course__title', 'module__title')
    list_editable = ('order', 'is_preview')
    list_fullwidth = True


@admin.register(Enrollment)
class EnrollmentAdmin(ModelAdmin):
    list_display = ('student', 'course', 'is_active', 'enrolled_at', 'progress')
    list_filter = ('is_active', 'course')
    search_fields = ('student__email', 'course__title')
    list_editable = ('is_active',)
    readonly_fields = ('enrolled_at',)
    list_fullwidth = True
    date_hierarchy = 'enrolled_at'


@admin.register(Announcement)
class AnnouncementAdmin(ModelAdmin):
    list_display = ('title', 'course', 'created_at')
    list_filter = ('course',)
    search_fields = ('title', 'content', 'course__title')
    readonly_fields = ('created_at',)
    list_fullwidth = True


@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ('user', 'lesson', 'content', 'created_at')
    list_filter = ('lesson__module__course',)
    search_fields = ('user__email', 'content')
    readonly_fields = ('created_at',)
    list_fullwidth = True


@admin.register(Review)
class ReviewAdmin(ModelAdmin):
    list_display = ('student', 'course', 'rating', 'created_at')
    list_filter = ('rating', 'course')
    search_fields = ('student__email', 'course__title', 'review_text')
    readonly_fields = ('created_at',)
    list_fullwidth = True


@admin.register(Quiz)
class QuizAdmin(ModelAdmin):
    list_display = ('title', 'course')
    list_filter = ('course',)
    search_fields = ('title',)
    list_fullwidth = True


@admin.register(Question)
class QuestionAdmin(ModelAdmin):
    list_display = ('question_text', 'quiz', 'type')
    list_filter = ('type', 'quiz')
    search_fields = ('question_text',)
    list_fullwidth = True


@admin.register(Answer)
class AnswerAdmin(ModelAdmin):
    list_display = ('answer_text', 'question', 'is_correct')
    list_filter = ('is_correct',)
    list_fullwidth = True

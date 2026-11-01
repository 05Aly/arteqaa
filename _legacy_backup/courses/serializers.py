from rest_framework import serializers
from .models import (Category, Course, Module, Lesson, Enrollment, 
                     Review, Quiz, Question, Answer, Announcement, Comment)

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.full_name')
    class Meta:
        model = Comment
        fields = ('id', 'lesson', 'user', 'user_name', 'content', 'created_at')
        extra_kwargs = {'user': {'read_only': True}}

class LessonSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    class Meta:
        model = Lesson
        fields = ('id', 'course', 'module', 'title', 'video_url', 'pdf_file', 'content', 'duration', 'order', 'is_preview', 'comments')

class ModuleSerializer(serializers.ModelSerializer):
    lessons = serializers.SerializerMethodField()
    class Meta:
        model = Module
        fields = ('id', 'course', 'title', 'order', 'lessons')
        
    def get_lessons(self, obj):
        return LessonSerializer(obj.module_lessons.all(), many=True).data

class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)
    lessons = serializers.SerializerMethodField()
    announcements = AnnouncementSerializer(many=True, read_only=True)
    instructor_name = serializers.ReadOnlyField(source='instructor.full_name')
    category_name = serializers.ReadOnlyField(source='category.name')

    class Meta:
        model = Course
        fields = ('id', 'title', 'slug', 'description', 'price', 'thumbnail', 'category', 'category_name', 
                  'instructor', 'instructor_name', 'modules', 'lessons', 'announcements', 'created_at', 'updated_at')
        extra_kwargs = {'instructor': {'read_only': True}}
        
    def get_lessons(self, obj):
        # Return only lessons that are not assigned to a module
        direct_lessons = obj.lessons.filter(module__isnull=True)
        return LessonSerializer(direct_lessons, many=True).data

class EnrollmentSerializer(serializers.ModelSerializer):
    course_title = serializers.ReadOnlyField(source='course.title')
    class Meta:
        model = Enrollment
        fields = ('id', 'student', 'course', 'course_title', 'is_active', 'enrolled_at', 'progress')
        extra_kwargs = {'student': {'read_only': True}}

class ReviewSerializer(serializers.ModelSerializer):
    student_name = serializers.ReadOnlyField(source='student.full_name')
    class Meta:
        model = Review
        fields = ('id', 'student', 'student_name', 'course', 'rating', 'review_text', 'created_at')
        extra_kwargs = {'student': {'read_only': True}}

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ('id', 'answer_text', 'is_correct')

class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)
    class Meta:
        model = Question
        fields = ('id', 'question_text', 'type', 'answers')

class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    class Meta:
        model = Quiz
        fields = ('id', 'course', 'title', 'questions')

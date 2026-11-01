from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import get_object_or_404
import os
from .models import (Category, Course, Module, Lesson, Enrollment, Review, 
                     Quiz, Question, Answer, Announcement, Comment)
from .serializers import (CategorySerializer, CourseSerializer, ModuleSerializer, 
                            LessonSerializer, EnrollmentSerializer, ReviewSerializer, 
                            QuizSerializer, AnnouncementSerializer, CommentSerializer)
from .permissions import IsInstructorOrReadOnly, IsOwnerOrReadOnly
from .tasks import generate_certificate

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'price']
    lookup_field = 'slug'

    def get_permissions(self):
        if self.action in ['create']:
            return [permissions.IsAuthenticated(), IsInstructorOrReadOnly()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)

class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.action in ['create']:
            return [permissions.IsAuthenticated(), IsInstructorOrReadOnly()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]
        return [permissions.AllowAny()]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        course = instance.course if instance.course else instance.module.course
        
        # Paywall Logic
        if not instance.is_preview:
            is_enrolled = Enrollment.objects.filter(
                student=request.user, 
                course=course, 
                is_active=True
            ).exists()
            
            if not is_enrolled and not request.user.is_staff and request.user != course.instructor:
                return Response({
                    "detail": "You must be enrolled in this course to view this lesson.",
                    "is_preview": False,
                    "buy_url": f"/courses/{course.slug}/"
                }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        lesson = serializer.validated_data['lesson']
        course = lesson.course if lesson.course else lesson.module.course
        is_enrolled = Enrollment.objects.filter(
            student=self.request.user, 
            course=course, 
            is_active=True
        ).exists()
        
        if not is_enrolled and not self.request.user.is_staff:
            raise permissions.PermissionDenied("Only enrolled students can comment.")
        
        serializer.save(user=self.request.user)

class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class EnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Enrollment.objects.filter(student=self.request.user)

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)

    @action(detail=True, methods=['get'])
    def download_certificate(self, request, pk=None):
        enrollment = self.get_object()
        if enrollment.progress < 100:
            return Response({'error': 'Course not completed'}, status=400)
        
        filename = f"certificate_{enrollment.id}.pdf"
        filepath = os.path.join(settings.MEDIA_ROOT, 'certificates', filename)
        
        if not os.path.exists(os.path.dirname(filepath)):
            os.makedirs(os.path.dirname(filepath))
            
        generate_certificate(request.user.full_name, enrollment.course.title, filepath)
        
        with open(filepath, 'rb') as pdf:
            response = HttpResponse(pdf.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.action in ['create']:
            return [permissions.IsAuthenticated()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)

class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def submit(self, request, pk=None):
        quiz = self.get_object()
        user_answers = request.data.get('answers', [])
        
        total_questions = quiz.questions.count()
        correct_answers = 0
        
        for ua in user_answers:
            try:
                question = quiz.questions.get(id=ua['question_id'])
                answer = question.answers.get(id=ua['answer_id'])
                if answer.is_correct:
                    correct_answers += 1
            except (Question.DoesNotExist, Answer.DoesNotExist):
                continue
        
        score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        
        return Response({
            'score': score,
            'correct_answers': correct_answers,
            'total_questions': total_questions
        })

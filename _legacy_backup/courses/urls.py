from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (CategoryViewSet, CourseViewSet, ModuleViewSet, LessonViewSet, 
                    EnrollmentViewSet, ReviewViewSet, QuizViewSet, AnnouncementViewSet, CommentViewSet)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'modules', ModuleViewSet)
router.register(r'lessons', LessonViewSet)
router.register(r'quizzes', QuizViewSet)
router.register(r'enrollments', EnrollmentViewSet, basename='enrollment')
router.register(r'reviews', ReviewViewSet)
router.register(r'announcements', AnnouncementViewSet)
router.register(r'comments', CommentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

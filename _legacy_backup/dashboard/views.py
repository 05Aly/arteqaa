from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from courses.models import Course, Enrollment, Announcement, Lesson
from django.db.models import Count

class StudentDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        enrollments = Enrollment.objects.filter(student=request.user)
        completed_courses = enrollments.filter(progress=100).count()
        total_courses = enrollments.count()
        
        enrolled_course_ids = enrollments.values_list('course_id', flat=True)
        
        announcements = Announcement.objects.filter(course_id__in=enrolled_course_ids).order_by('-created_at')[:5]
        recent_lessons = Lesson.objects.filter(module__course_id__in=enrolled_course_ids).order_by('-id')[:5]
        recommended_courses = Course.objects.exclude(id__in=enrolled_course_ids).order_by('?')[:3]
        
        return Response({
            'total_enrolled': total_courses,
            'completed_courses': completed_courses,
            'learning_progress': [
                {'course': e.course.title, 'progress': e.progress} for e in enrollments
            ],
            'announcements': [
                {'title': a.title, 'course': a.course.title, 'content': a.content, 'date': a.created_at} for a in announcements
            ],
            'recent_lessons': [
                {'title': l.title, 'course': l.module.course.title, 'id': l.id} for l in recent_lessons
            ],
            'recommended_courses': [
                {'title': c.title, 'slug': c.slug, 'price': c.price, 'thumbnail': c.thumbnail.url if c.thumbnail else None} for c in recommended_courses
            ]
        })

class InstructorDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'INSTRUCTOR':
            return Response({'error': 'Not authorized'}, status=403)
            
        courses = Course.objects.filter(instructor=request.user)
        total_students = Enrollment.objects.filter(course__in=courses).count()
        
        return Response({
            'total_courses': courses.count(),
            'total_students': total_students,
            'course_stats': courses.annotate(student_count=Count('enrollments')).values('title', 'student_count')
        })

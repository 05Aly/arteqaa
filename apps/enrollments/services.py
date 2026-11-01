# apps/enrollments/services.py
from django.utils import timezone
from apps.enrollments.models import Enrollment, LessonProgress, Certificate
from apps.courses.models import Course, Lesson
from apps.accounts.models import InstructorProfile
from django.db.models import Count, Avg

class EnrollmentService:
    """Service layer for handling enrollment logic."""

    @staticmethod
    def enroll(user, course: Course) -> Enrollment:
        """Enroll a user in a course if not already enrolled."""
        enrollment, created = Enrollment.objects.get_or_create(
            student=user,
            course=course
        )
        if created:
            EnrollmentService.sync_instructor_stats(course.instructor)
        return enrollment

    @staticmethod
    def sync_instructor_stats(instructor):
        """Recalculate and update instructor profile statistics."""
        if not instructor or instructor.role != 'instructor':
            return
        profile, _ = InstructorProfile.objects.get_or_create(user=instructor)
        published_courses = Course.objects.filter(instructor=instructor, status='published')
        profile.total_courses = published_courses.count()
        profile.total_students = Enrollment.objects.filter(course__instructor=instructor).values('student').distinct().count()
        from apps.reviews.models import Review
        avg = Review.objects.filter(course__instructor=instructor, is_approved=True).aggregate(avg=Avg('rating'))['avg']
        profile.rating_avg = round(avg, 2) if avg else 0.00
        profile.save()

    @staticmethod
    def toggle_lesson_complete(user, lesson: Lesson, force_complete=False) -> LessonProgress:
        """Toggle or mark a specific lesson as completed for the user, update progress, issue cert if done."""
        course = lesson.section.course
        enrollment = Enrollment.objects.filter(student=user, course=course).first()
        if not enrollment:
            # If instructor or superuser is testing player, auto-enroll them so progress works seamlessly
            if user.is_superuser or user == course.instructor:
                enrollment = EnrollmentService.enroll(user, course)
            else:
                raise ValueError("يجب الاشتراك في الكورس أولاً لتسجيل تقدمك.")

        progress, created = LessonProgress.objects.get_or_create(
            enrollment=enrollment,
            lesson=lesson
        )
        
        if force_complete:
            progress.is_completed = True
            progress.completed_at = timezone.now()
        else:
            progress.is_completed = not progress.is_completed
            progress.completed_at = timezone.now() if progress.is_completed else None
            
        progress.save()
        
        # Update overall progress
        EnrollmentService.calculate_progress(enrollment)
        return progress

    @staticmethod
    def mark_lesson_complete(user, lesson: Lesson) -> LessonProgress:
        """Mark a specific lesson as completed for the user, update progress, issue cert if done."""
        return EnrollmentService.toggle_lesson_complete(user, lesson, force_complete=True)

    @staticmethod
    def calculate_progress(enrollment: Enrollment) -> float:
        """Calculate and update the completion percentage of the course."""
        course = enrollment.course
        total_lessons = Lesson.objects.filter(section__course=course).count()
        if total_lessons == 0:
            enrollment.progress_percent = 0.0
            enrollment.save()
            return 0.0

        completed_lessons = LessonProgress.objects.filter(
            enrollment=enrollment,
            lesson__section__course=course,
            is_completed=True
        ).count()

        percent = min(round((completed_lessons / total_lessons) * 100, 1), 100.0)
        enrollment.progress_percent = percent
        
        # Check completion
        if percent >= 100.0:
            if not enrollment.is_completed:
                enrollment.is_completed = True
                enrollment.completed_at = timezone.now()
            Certificate.objects.get_or_create(enrollment=enrollment)
        else:
            enrollment.is_completed = False
            enrollment.completed_at = None
            
        enrollment.save()
        return percent


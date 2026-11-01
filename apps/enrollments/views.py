# apps/enrollments/views.py
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib import messages
import json

from apps.courses.models import Course, Lesson
from apps.enrollments.models import Enrollment, Certificate
from apps.enrollments.services import EnrollmentService


@login_required
@require_POST
def enroll_view(request, course_id):
    """Enroll a student in a course."""
    course = get_object_or_404(Course, id=course_id, status='published')

    if course.enrollments.filter(student=request.user).exists():
        messages.info(request, "أنت مشترك في هذا الكورس بالفعل.")
        return redirect('courses:detail', slug=course.slug)

    # NOTE: Payment gateway should be called here if course.price > 0
    EnrollmentService.enroll(request.user, course)
    messages.success(request, f"🎉 تم اشتراكك بنجاح في كورس «{course.title}»!")

    # Redirect to first lesson
    first_section = course.sections.order_by('order').first()
    if first_section:
        first_lesson = first_section.lessons.order_by('order').first()
        if first_lesson:
            return redirect('courses:player', course_slug=course.slug, lesson_slug=first_lesson.slug)

    return redirect('courses:detail', slug=course.slug)


@login_required
@require_POST
def mark_lesson_complete(request, lesson_id):
    """AJAX: Toggle or mark a lesson as completed and return updated progress."""
    try:
        lesson = get_object_or_404(Lesson, id=lesson_id)
        force_complete = False
        if request.body:
            try:
                body_data = json.loads(request.body)
                force_complete = bool(body_data.get('force_complete', False))
            except json.JSONDecodeError:
                pass
        progress = EnrollmentService.toggle_lesson_complete(request.user, lesson, force_complete=force_complete)
        enrollment = progress.enrollment
        cert_id = None
        if enrollment.is_completed and hasattr(enrollment, 'certificate'):
            cert_id = str(enrollment.certificate.certificate_id)
        return JsonResponse({
            'success': True,
            'is_completed': progress.is_completed,
            'progress': enrollment.progress_percent,
            'is_course_completed': enrollment.is_completed,
            'certificate_id': cert_id,
        })
    except ValueError as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=403)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def my_courses_view(request):
    """Student dashboard: list of enrolled courses."""
    enrollments = Enrollment.objects.filter(student=request.user).select_related(
        'course__instructor', 'course__category', 'certificate'
    ).prefetch_related('course__sections__lessons')
    certificates = Certificate.objects.filter(enrollment__student=request.user).select_related('enrollment__course')
    context = {
        'enrollments': enrollments,
        'completed_count': enrollments.filter(is_completed=True).count(),
        'active_count': enrollments.filter(is_completed=False).count(),
        'certificates': certificates,
    }
    return render(request, 'accounts/student_dashboard.html', context)



@login_required
def certificate_view(request, certificate_id):
    """Display certificate page."""
    cert = get_object_or_404(
        Certificate.objects.select_related('enrollment__course', 'enrollment__student'),
        certificate_id=certificate_id,
        enrollment__student=request.user
    )
    return render(request, 'enrollments/certificate.html', {'cert': cert})

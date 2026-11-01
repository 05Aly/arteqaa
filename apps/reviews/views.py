# apps/reviews/views.py
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST, require_GET
import json

from apps.courses.models import Course
from apps.enrollments.models import Enrollment
from .models import Review

@login_required
@require_POST
def create_review_view(request, course_id):
    """AJAX: Create or update a review for an enrolled student."""
    course = get_object_or_404(Course, id=course_id, status='published')

    # Only enrolled students can review
    if not Enrollment.objects.filter(student=request.user, course=course).exists():
        return JsonResponse({'success': False, 'error': 'يجب أن تكون مشتركاً في الكورس لتتمكن من تقييمه.'}, status=403)

    try:
        data = json.loads(request.body)
        rating = int(data.get('rating', 0))
        comment = data.get('comment', '').strip()
    except (ValueError, json.JSONDecodeError):
        return JsonResponse({'success': False, 'error': 'بيانات غير صحيحة.'}, status=400)

    if not (1 <= rating <= 5):
        return JsonResponse({'success': False, 'error': 'التقييم يجب أن يكون بين 1 و5.'}, status=400)

    review, created = Review.objects.update_or_create(
        student=request.user,
        course=course,
        defaults={'rating': rating, 'comment': comment}
    )

    from apps.enrollments.services import EnrollmentService
    EnrollmentService.sync_instructor_stats(course.instructor)

    return JsonResponse({
        'success': True,
        'created': created,
        'message': 'تم إضافة تقييمك بنجاح!' if created else 'تم تحديث تقييمك بنجاح!',
        'avg_rating': course.average_rating,
        'reviews_count': course.reviews_count,
        'review': {
            'rating': review.rating,
            'comment': review.comment,
            'author': review.student.display_name,
            'date': review.created_at.strftime('%Y-%m-%d'),
        }
    })


@require_GET
def course_reviews_view(request, course_id):
    """AJAX: Return paginated approved reviews for a course."""
    course = get_object_or_404(Course, id=course_id)
    reviews = Review.objects.filter(course=course, is_approved=True).select_related('student').order_by('-created_at')[:10]

    data = [
        {
            'author': r.student.get_full_name() or r.student.email,
            'rating': r.rating,
            'comment': r.comment,
            'date': r.created_at.strftime('%Y-%m-%d'),
        }
        for r in reviews
    ]
    return JsonResponse({'success': True, 'reviews': data})

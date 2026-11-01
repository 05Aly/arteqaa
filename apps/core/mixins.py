# apps/core/mixins.py
from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from apps.courses.models import Course

class InstructorRequiredMixin(AccessMixin):
    """Verify that the current user is an instructor."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'instructor':
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

class CourseOwnerMixin(AccessMixin):
    """Verify that the current user is the instructor of the course."""
    def dispatch(self, request, *args, **kwargs):
        course = get_object_or_404(Course, slug=kwargs.get('slug'))
        if course.instructor != request.user and not request.user.is_superuser:
            raise PermissionDenied("ليس لديك الصلاحية لتعديل هذا الكورس.")
        return super().dispatch(request, *args, **kwargs)

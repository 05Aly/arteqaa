from django.db.models import Count, Sum
from django.utils.translation import gettext_lazy as _


def admin_environment_callback(request):
    return _("Development"), "warning"


def dashboard_badge(request):
    from courses.models import Enrollment
    count = Enrollment.objects.filter(is_active=True).count()
    return str(count) if count else ""


def dashboard_callback(request, context):
    """
    Inject extra stats into the admin dashboard context.
    """
    try:
        from courses.models import Course, Enrollment
        from users.models import User
        from payments.models import Payment

        context.update({
            "stats": [
                {
                    "label": _("Total Students"),
                    "metric": User.objects.filter(role="STUDENT").count(),
                    "icon": "group",
                    "description": _("Registered learners"),
                    "color": "success",
                },
                {
                    "label": _("Total Courses"),
                    "metric": Course.objects.count(),
                    "icon": "menu_book",
                    "description": _("Published courses"),
                    "color": "info",
                },
                {
                    "label": _("Active Enrollments"),
                    "metric": Enrollment.objects.filter(is_active=True).count(),
                    "icon": "school",
                    "description": _("Students currently learning"),
                    "color": "warning",
                },
                {
                    "label": _("Total Revenue"),
                    "metric": f"${Payment.objects.filter(status='COMPLETED').aggregate(total=Sum('amount'))['total'] or 0:.0f}",
                    "icon": "payments",
                    "description": _("From completed payments"),
                    "color": "danger",
                },
            ],
        })
    except Exception:
        pass

    return context

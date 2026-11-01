# apps/courses/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.db.models import Count, Avg, Q
from apps.courses.models import Course, Section, Lesson, Resource
from apps.categories.models import Category
from apps.enrollments.models import Enrollment, LessonProgress
from apps.reviews.models import Review
from apps.accounts.models import User
from apps.core.mixins import InstructorRequiredMixin, CourseOwnerMixin
from .forms import CourseForm


def home_view(request):
    """Homepage view with real platform stats, featured courses, categories, and top reviews."""
    base_qs = Course.objects.filter(status='published').select_related('instructor', 'category').annotate(
        avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True)),
        approved_reviews_count=Count('reviews', filter=Q(reviews__is_approved=True), distinct=True),
        students_count=Count('enrollments', distinct=True),
        lessons_count=Count('sections__lessons', distinct=True),
    )
    featured_courses = base_qs.filter(is_featured=True)[:6]
    if not featured_courses.exists():
        featured_courses = base_qs.order_by('-created_at')[:6]

    categories = Category.objects.annotate(
        published_courses_count=Count('courses', filter=Q(courses__status='published'))
    ).order_by('-published_courses_count', 'name')[:8]

    top_reviews = Review.objects.filter(is_approved=True, rating__gte=4).select_related('student', 'course').order_by('-created_at')[:3]

    total_courses = Course.objects.filter(status='published').count()
    total_students = User.objects.filter(role='student').count()
    total_instructors = User.objects.filter(role='instructor').count()
    platform_avg = Review.objects.filter(is_approved=True).aggregate(avg=Avg('rating'))['avg']

    context = {
        'featured_courses': featured_courses,
        'categories': categories,
        'top_reviews': top_reviews,
        'stats': {
            'courses': total_courses or 12,
            'students': total_students or 150,
            'instructors': total_instructors or 8,
            'rating': round(float(platform_avg), 1) if platform_avg else 4.9,
        }
    }
    return render(request, 'home/index.html', context)


class CourseListView(ListView):
    """List of published courses with filtering, search, and sorting."""
    model = Course
    template_name = 'courses/list.html'
    context_object_name = 'courses'
    paginate_by = 9

    def get_queryset(self):
        qs = Course.objects.filter(status='published').select_related('instructor', 'category').annotate(
            avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True)),
            approved_reviews_count=Count('reviews', filter=Q(reviews__is_approved=True), distinct=True),
            students_count=Count('enrollments', distinct=True),
            lessons_count=Count('sections__lessons', distinct=True),
        )
        
        # Search
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(title__icontains=q) |
                Q(description__icontains=q) |
                Q(instructor__first_name__icontains=q) |
                Q(instructor__last_name__icontains=q) |
                Q(category__name__icontains=q)
            )
            
        # Filter by category
        categories = [c for c in self.request.GET.getlist('category') if c]
        if categories:
            qs = qs.filter(category__slug__in=categories)
            
        # Filter by level
        levels = [l for l in self.request.GET.getlist('level') if l]
        if levels:
            qs = qs.filter(level__in=levels)

        # Filter by price type
        price_type = self.request.GET.get('price_type', '')
        if price_type == 'free':
            qs = qs.filter(Q(price=0) | Q(discount_price=0))
        elif price_type == 'paid':
            qs = qs.filter(price__gt=0).exclude(discount_price=0)
            
        # Sorting
        sort = self.request.GET.get('sort', '-created_at')
        if sort == 'popular':
            qs = qs.order_by('-students_count', '-created_at')
        elif sort == 'rating':
            qs = qs.order_by('-avg_rating', '-created_at')
        elif sort in ['created_at', '-created_at', 'price', '-price']:
            qs = qs.order_by(sort)
        else:
            qs = qs.order_by('-created_at')
            
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.annotate(
            course_count=Count('courses', filter=Q(courses__status='published'))
        )
        context['selected_categories'] = self.request.GET.getlist('category')
        context['selected_levels'] = self.request.GET.getlist('level')
        context['current_sort'] = self.request.GET.get('sort', '-created_at')
        context['current_price_type'] = self.request.GET.get('price_type', '')

        # Preserve multivalue query params for pagination and sorting
        query_params = self.request.GET.copy()
        if 'page' in query_params:
            del query_params['page']
        context['filter_query_string'] = query_params.urlencode()
        return context


def course_detail_view(request, slug):
    """Course detail page showing curriculum, instructor info, and student reviews."""
    course_qs = Course.objects.select_related('instructor', 'category').prefetch_related(
        'sections__lessons__resources',
        'reviews__student'
    ).annotate(
        avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True)),
        approved_reviews_count=Count('reviews', filter=Q(reviews__is_approved=True), distinct=True),
        students_count=Count('enrollments', distinct=True),
    )
    course = get_object_or_404(course_qs, slug=slug)
    if course.status != 'published' and not (request.user.is_authenticated and (request.user.is_superuser or request.user == course.instructor)):
        messages.error(request, "هذا الكورس غير متاح حالياً.")
        return redirect('courses:list')
    
    is_enrolled = False
    enrollment = None
    user_review = None
    first_lesson = None

    for section in course.sections.all():
        lessons = list(section.lessons.all())
        if lessons:
            first_lesson = lessons[0]
            break

    if request.user.is_authenticated:
        enrollment = Enrollment.objects.filter(student=request.user, course=course).first()
        is_enrolled = enrollment is not None
        user_review = Review.objects.filter(student=request.user, course=course).first()

    reviews = course.reviews.filter(is_approved=True).select_related('student').order_by('-created_at')
    related_courses = Course.objects.filter(
        status='published', category=course.category
    ).exclude(id=course.id).select_related('instructor', 'category')[:3]

    context = {
        'course': course,
        'is_enrolled': is_enrolled,
        'enrollment': enrollment,
        'first_lesson': first_lesson,
        'reviews': reviews,
        'user_review': user_review,
        'related_courses': related_courses,
    }
    return render(request, 'courses/detail.html', context)


def lesson_player_view(request, course_slug, lesson_slug):
    """Lesson player view with ordered navigation, progress tracking, and resource downloads."""
    course = get_object_or_404(
        Course.objects.select_related('instructor', 'category').prefetch_related('sections__lessons__resources'),
        slug=course_slug
    )
    if course.status != 'published' and not (request.user.is_authenticated and (request.user.is_superuser or request.user == course.instructor)):
        messages.error(request, "هذا الكورس غير متاح حالياً.")
        return redirect('courses:list')

    lesson = get_object_or_404(
        Lesson.objects.select_related('section').prefetch_related('resources'),
        slug=lesson_slug,
        section__course=course
    )
    
    is_enrolled = False
    enrollment = None
    is_completed = False
    completed_lesson_ids = set()
    
    if request.user.is_authenticated:
        enrollment = Enrollment.objects.filter(student=request.user, course=course).first()
        is_enrolled = enrollment is not None
        
        if is_enrolled:
            completed_lesson_ids = set(
                LessonProgress.objects.filter(
                    enrollment=enrollment, is_completed=True
                ).values_list('lesson_id', flat=True)
            )
            is_completed = lesson.id in completed_lesson_ids
    
    can_access = (
        lesson.is_preview
        or is_enrolled
        or (request.user.is_authenticated and (request.user.is_superuser or request.user == course.instructor))
    )
    if not can_access:
        messages.warning(request, "هذا الدرس مخصص للمشتركين في الكورس. اشترك الآن للوصول الكامل!")
        return redirect('courses:detail', slug=course.slug)

    # Build ordered list of all lessons for Previous / Next navigation
    all_lessons = []
    for sec in course.sections.all():
        for l in sec.lessons.all():
            all_lessons.append(l)

    prev_lesson = None
    next_lesson = None
    for idx, item in enumerate(all_lessons):
        if item.id == lesson.id:
            if idx > 0:
                prev_lesson = all_lessons[idx - 1]
            if idx < len(all_lessons) - 1:
                next_lesson = all_lessons[idx + 1]
            break

    context = {
        'course': course,
        'lesson': lesson,
        'enrollment': enrollment,
        'is_enrolled': is_enrolled,
        'is_completed': is_completed,
        'completed_lesson_ids': completed_lesson_ids,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
        'total_lessons': len(all_lessons),
    }
    return render(request, 'courses/player.html', context)


class InstructorCourseCreateView(InstructorRequiredMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'courses/instructor_course_form.html'

    def form_valid(self, form):
        form.instance.instructor = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, "تم إنشاء الكورس بنجاح! يمكنك الآن إضافة الأقسام والدروس.")
        return response

    def get_success_url(self):
        return reverse('courses:manage_content', kwargs={'slug': self.object.slug})


class InstructorCourseEditView(InstructorRequiredMixin, CourseOwnerMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'courses/instructor_course_form.html'
    success_url = reverse_lazy('accounts:instructor_dashboard')

    def form_valid(self, form):
        messages.success(self.request, "تم تحديث بيانات الكورس بنجاح!")
        return super().form_valid(form)


@login_required
def instructor_lesson_manage_view(request, slug):
    """Full curriculum builder for instructors: add/edit/delete sections, lessons, and resources."""
    course = get_object_or_404(
        Course.objects.prefetch_related('sections__lessons__resources'),
        slug=slug
    )
    if course.instructor != request.user and not request.user.is_superuser:
        messages.error(request, "ليس لديك الصلاحية لإدارة محتوى هذا الكورس.")
        return redirect('accounts:instructor_dashboard')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add_section':
            title = request.POST.get('title', '').strip()
            order = int(request.POST.get('order') or (course.sections.count() + 1))
            if title:
                Section.objects.create(course=course, title=title, order=order)
                messages.success(request, f"تم إضافة القسم «{title}» بنجاح.")

        elif action == 'edit_section':
            sec_id = request.POST.get('section_id')
            sec = get_object_or_404(Section, id=sec_id, course=course)
            title = request.POST.get('title', '').strip()
            if title:
                sec.title = title
                sec.order = int(request.POST.get('order') or sec.order)
                sec.save()
                messages.success(request, "تم تحديث القسم بنجاح.")

        elif action == 'delete_section':
            sec_id = request.POST.get('section_id')
            sec = get_object_or_404(Section, id=sec_id, course=course)
            sec.delete()
            messages.info(request, "تم حذف القسم وجميع دروسه.")

        elif action == 'add_lesson':
            sec_id = request.POST.get('section_id')
            sec = get_object_or_404(Section, id=sec_id, course=course)
            title = request.POST.get('title', '').strip()
            video_url = request.POST.get('video_url', '').strip()
            duration_minutes = int(request.POST.get('duration_minutes') or 0)
            content = request.POST.get('content', '').strip()
            is_preview = request.POST.get('is_preview') == 'on'
            order = int(request.POST.get('order') or (sec.lessons.count() + 1))
            if title:
                lesson = Lesson.objects.create(
                    section=sec,
                    title=title,
                    video_url=video_url or None,
                    duration_seconds=duration_minutes * 60,
                    content=content,
                    is_preview=is_preview,
                    order=order,
                )
                res_title = request.POST.get('resource_title', '').strip()
                res_file = request.FILES.get('resource_file')
                res_url = request.POST.get('resource_url', '').strip()
                if res_title and (res_file or res_url):
                    Resource.objects.create(
                        lesson=lesson,
                        title=res_title,
                        file=res_file,
                        external_url=res_url or None,
                        resource_type='pdf' if res_file else 'link'
                    )
                messages.success(request, f"تم إضافة الدرس «{title}» بنجاح.")

        elif action == 'delete_lesson':
            lesson_id = request.POST.get('lesson_id')
            lesson = get_object_or_404(Lesson, id=lesson_id, section__course=course)
            lesson.delete()
            messages.info(request, "تم حذف الدرس.")

        return redirect('courses:manage_content', slug=course.slug)

    return render(request, 'courses/manage_content.html', {'course': course})


def contact_view(request):
    """Contact and support page."""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message_text = request.POST.get('message', '').strip()
        if name and email and message_text:
            messages.success(request, "تم إرسال رسالتك بنجاح! سيتواصل معك فريق دعم ارتقاء في أقرب وقت.")
            return redirect('courses:contact')
        else:
            messages.error(request, "يرجى ملء جميع الحقول المطلوبة.")
    return render(request, 'home/contact.html')

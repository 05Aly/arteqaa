# apps/accounts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.db.models import Count, Avg, Sum, Q
from apps.accounts.models import User, InstructorProfile
from apps.courses.models import Course, Lesson
from apps.enrollments.models import Enrollment, Certificate
from apps.reviews.models import Review

def login_view(request):
    """Handle user login."""
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        remember = request.POST.get('remember')
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            if not remember:
                request.session.set_expiry(0)
            messages.success(request, f"مرحباً بعودتك، {user.display_name}!")
            next_url = request.GET.get('next') or request.POST.get('next') or 'home'
            return redirect(next_url)
        else:
            messages.error(request, "البريد الإلكتروني أو كلمة المرور غير صحيحة.")
            
    return render(request, 'accounts/login.html')

def register_view(request):
    """Handle user registration."""
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        role = request.POST.get('role', 'student')
        if role not in ['student', 'instructor']:
            role = 'student'
        
        if not full_name or not email or not password:
            messages.error(request, "يرجى ملء جميع الحقول المطلوبة.")
            return render(request, 'accounts/register.html', {'full_name': full_name, 'email': email, 'role': role})
            
        if password != confirm_password:
            messages.error(request, "كلمتا المرور غير متطابقتين.")
            return render(request, 'accounts/register.html', {'full_name': full_name, 'email': email, 'role': role})
            
        if User.objects.filter(Q(email__iexact=email) | Q(username__iexact=email)).exists():
            messages.error(request, "هذا البريد الإلكتروني مسجل مسبقاً.")
            return render(request, 'accounts/register.html', {'full_name': full_name, 'email': email, 'role': role})
            
        try:
            validate_password(password)
        except ValidationError as errs:
            for err in errs.messages:
                messages.error(request, err)
            return render(request, 'accounts/register.html', {'full_name': full_name, 'email': email, 'role': role})
            
        parts = full_name.split()
        first_name = parts[0] if parts else ''
        last_name = ' '.join(parts[1:]) if len(parts) > 1 else ''
        
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        
        if role == 'instructor':
            title = request.POST.get('instructor_title', '').strip() or 'مدرب معتمد في منصة ارتقاء'
            InstructorProfile.objects.update_or_create(user=user, defaults={'title': title})
        
        login(request, user)
        messages.success(request, "تم إنشاء الحساب بنجاح! أهلاً بك في منصة ارتقاء.")
        if role == 'instructor':
            return redirect('accounts:instructor_dashboard')
        return redirect('home')
        
    return render(request, 'accounts/register.html')

def logout_view(request):
    """Handle user logout."""
    logout(request)
    messages.info(request, "تم تسجيل الخروج بنجاح. نراك قريباً!")
    return redirect('home')

@login_required
def student_dashboard(request):
    """Student dashboard showing enrolled courses, certificates, and stats."""
    if request.user.role == 'instructor' and not request.GET.get('view_as_student'):
        return redirect('accounts:instructor_dashboard')
            
    enrollments = Enrollment.objects.filter(student=request.user).select_related(
        'course__instructor', 'course__category', 'certificate'
    ).prefetch_related('course__sections__lessons').order_by('-enrolled_at')
    
    certificates = Certificate.objects.filter(enrollment__student=request.user).select_related('enrollment__course')
    
    context = {
        'enrollments': enrollments,
        'completed_count': enrollments.filter(is_completed=True).count(),
        'active_count': enrollments.filter(is_completed=False).count(),
        'certificates': certificates,
    }
    return render(request, 'accounts/student_dashboard.html', context)

@login_required
def instructor_dashboard(request):
    """Instructor dashboard showing courses, students, ratings, and management tools."""
    if request.user.role != 'instructor' and not request.user.is_superuser:
        messages.error(request, "غير مصرح لك بالدخول لهذه الصفحة.")
        return redirect('home')
        
    courses = Course.objects.filter(instructor=request.user).select_related('category').annotate(
        students_count=Count('enrollments', distinct=True),
        avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True)),
        lessons_count=Count('sections__lessons', distinct=True),
    ).order_by('-created_at')
    
    total_students = Enrollment.objects.filter(course__instructor=request.user).values('student').distinct().count()
    published_count = courses.filter(status='published').count()
    draft_count = courses.filter(status='draft').count()
    avg_rating = Review.objects.filter(course__instructor=request.user, is_approved=True).aggregate(avg=Avg('rating'))['avg'] or 0.0
    recent_enrollments = Enrollment.objects.filter(course__instructor=request.user).select_related('student', 'course').order_by('-enrolled_at')[:6]
    
    context = {
        'courses': courses,
        'total_students': total_students,
        'published_count': published_count,
        'draft_count': draft_count,
        'avg_rating': round(float(avg_rating), 1),
        'recent_enrollments': recent_enrollments,
    }
    return render(request, 'accounts/instructor_dashboard.html', context)

@login_required
def edit_profile_view(request):
    """Allow users (students and instructors) to edit their personal profile and settings."""
    user = request.user
    instructor_profile = None
    if user.role == 'instructor':
        instructor_profile, _ = InstructorProfile.objects.get_or_create(user=user)
        
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        bio = request.POST.get('bio', '').strip()
        
        user.first_name = first_name
        user.last_name = last_name
        user.bio = bio
        
        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']
            
        # Social links
        social_links = {}
        for platform in ['website', 'linkedin', 'github', 'twitter', 'youtube']:
            val = request.POST.get(f'social_{platform}', '').strip()
            if val:
                social_links[platform] = val
        user.social_links = social_links
        user.save()
        
        if instructor_profile:
            instructor_profile.title = request.POST.get('title', '').strip() or instructor_profile.title
            instructor_profile.expertise = request.POST.get('expertise', '').strip()
            instructor_profile.save()
            
        messages.success(request, "تم تحديث ملفك الشخصي بنجاح!")
        if user.role == 'instructor':
            return redirect('accounts:instructor_dashboard')
        return redirect('accounts:student_dashboard')
        
    context = {
        'instructor_profile': instructor_profile,
    }
    return render(request, 'accounts/edit_profile.html', context)

def instructors_list_view(request):
    """Public directory of instructors."""
    instructors = User.objects.filter(role='instructor', is_active=True).select_related('instructor_profile').annotate(
        published_courses_count=Count('courses', filter=Q(courses__status='published'), distinct=True),
        students_total=Count('courses__enrollments__student', distinct=True),
        avg_course_rating=Avg('courses__reviews__rating', filter=Q(courses__reviews__is_approved=True)),
    ).order_by('-published_courses_count', '-date_joined')
    
    return render(request, 'accounts/instructors_list.html', {'instructors': instructors})

def profile_view(request, username):
    """Public profile view for students and instructors."""
    profile_user = get_object_or_404(User, username=username)
    instructor_courses = []
    published_courses_count = 0
    total_students_count = 0
    avg_rating = 0.0
    
    if profile_user.role == 'instructor':
        instructor_courses = profile_user.courses.filter(status='published').select_related('category').annotate(
            avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True)),
            students_count=Count('enrollments', distinct=True),
        )
        published_courses_count = instructor_courses.count()
        total_students_count = Enrollment.objects.filter(course__instructor=profile_user).values('student').distinct().count()
        agg = Review.objects.filter(course__instructor=profile_user, is_approved=True).aggregate(avg=Avg('rating'))['avg']
        avg_rating = round(float(agg), 1) if agg else 4.9
        
    context = {
        'profile_user': profile_user,
        'instructor_courses': instructor_courses,
        'published_courses_count': published_courses_count,
        'total_students_count': total_students_count,
        'avg_rating': avg_rating,
    }
    return render(request, 'accounts/profile.html', context)


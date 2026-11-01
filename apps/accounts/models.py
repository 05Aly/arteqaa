# apps/accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver

class User(AbstractUser):
    """Custom user model supporting different roles (Student, Instructor, Admin)."""
    ROLE_CHOICES = (
        ('student', 'طالب'),
        ('instructor', 'مدرس'),
        ('admin', 'مسؤول'),
    )
    
    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student', verbose_name="الدور")
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name="الصورة الشخصية")
    bio = models.TextField(blank=True, verbose_name="نبذة تعريفية")
    social_links = models.JSONField(default=dict, blank=True, verbose_name="روابط التواصل")
    is_verified = models.BooleanField(default=False, verbose_name="حساب موثق")

    # Use email for login instead of username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = "مستخدم"
        verbose_name_plural = "المستخدمين"

    def __str__(self):
        return self.get_full_name() or self.email

    @property
    def display_name(self):
        return self.get_full_name() or self.username or self.email.split('@')[0]

class InstructorProfile(models.Model):
    """Extended profile for users with instructor role."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='instructor_profile', limit_choices_to={'role': 'instructor'})
    title = models.CharField(max_length=150, default="مدرب معتمد", verbose_name="المسمى الوظيفي (مثال: خبير تسويق)")
    expertise = models.CharField(max_length=255, blank=True, verbose_name="مجالات الخبرة")
    total_students = models.PositiveIntegerField(default=0, verbose_name="إجمالي الطلاب")
    total_courses = models.PositiveIntegerField(default=0, verbose_name="إجمالي الكورسات")
    rating_avg = models.DecimalField(max_digits=3, decimal_places=2, default=0.00, verbose_name="متوسط التقييم")

    class Meta:
        verbose_name = "ملف المدرس"
        verbose_name_plural = "ملفات المدرسين"

    def __str__(self):
        return f"Instructor: {self.user.display_name}"

@receiver(post_save, sender=User)
def ensure_instructor_profile(sender, instance, created, **kwargs):
    """Automatically create InstructorProfile when a user is assigned the instructor role."""
    if instance.role == 'instructor':
        InstructorProfile.objects.get_or_create(user=instance)


# apps/courses/models.py
import uuid
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.db.models import Avg
from apps.categories.models import Category


def generate_unique_slug(model_class, value, instance=None, scope_kwargs=None):
    """Generate a unique slug supporting Arabic/Unicode with fallback and collision suffix."""
    base_slug = slugify(value, allow_unicode=True)
    if not base_slug:
        base_slug = uuid.uuid4().hex[:8]
    slug = base_slug
    counter = 1
    qs = model_class.objects.all()
    if scope_kwargs:
        qs = qs.filter(**scope_kwargs)
    if instance and instance.pk:
        qs = qs.exclude(pk=instance.pk)
    while qs.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug


class Course(models.Model):
    """Main course entity representing a learning program."""
    LEVEL_CHOICES = (
        ('beginner', 'مبتدئ'),
        ('intermediate', 'متوسط'),
        ('advanced', 'متقدم'),
    )
    STATUS_CHOICES = (
        ('draft', 'مسودة'),
        ('published', 'منشور'),
        ('archived', 'مؤرشف'),
    )

    title = models.CharField(max_length=255, verbose_name="عنوان الكورس")
    slug = models.SlugField(unique=True, blank=True, max_length=255, allow_unicode=True)
    description = models.TextField(verbose_name="وصف الكورس")
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='courses', limit_choices_to={'role': 'instructor'}, verbose_name="المدرس")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='courses', verbose_name="التصنيف")
    thumbnail = models.ImageField(upload_to='courses/thumbnails/', null=True, blank=True, verbose_name="صورة الغلاف")
    preview_video = models.URLField(blank=True, null=True, verbose_name="فيديو تعريفي")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="السعر الأساسي")
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="السعر بعد الخصم")
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner', verbose_name="المستوى")
    language = models.CharField(max_length=50, default='العربية', verbose_name="لغة الشرح")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="الحالة")
    is_featured = models.BooleanField(default=False, verbose_name="مميز (يظهر في الرئيسية)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "كورس"
        verbose_name_plural = "الكورسات"
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(Course, self.title, instance=self)
        super().save(*args, **kwargs)

    @property
    def effective_price(self):
        if self.discount_price is not None and self.discount_price < self.price:
            return self.discount_price
        return self.price

    @property
    def has_discount(self):
        return self.discount_price is not None and self.discount_price < self.price

    @property
    def discount_percentage(self):
        if self.has_discount and self.price > 0:
            return int(round(((self.price - self.discount_price) / self.price) * 100))
        return 0

    @property
    def average_rating(self):
        if hasattr(self, 'avg_rating') and self.avg_rating is not None:
            return round(float(self.avg_rating), 1)
        agg = self.reviews.filter(is_approved=True).aggregate(avg=Avg('rating'))['avg']
        return round(float(agg), 1) if agg else 0.0

    @property
    def reviews_count(self):
        if hasattr(self, 'approved_reviews_count') and self.approved_reviews_count is not None:
            return self.approved_reviews_count
        return self.reviews.filter(is_approved=True).count()

    @property
    def total_lessons_count(self):
        return Lesson.objects.filter(section__course=self).count()

    @property
    def total_duration_display(self):
        total_sec = sum(
            lesson.duration_seconds
            for section in self.sections.all()
            for lesson in section.lessons.all()
        )
        if total_sec <= 0:
            return "غير محدد"
        hours = total_sec // 3600
        minutes = (total_sec % 3600) // 60
        if hours > 0:
            return f"{hours} س و {minutes} د" if minutes > 0 else f"{hours} ساعات"
        if minutes > 0:
            return f"{minutes} دقيقة"
        return f"{total_sec} ثانية"

    def __str__(self):
        return self.title

class Section(models.Model):
    """A module/section containing multiple lessons within a course."""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=255, verbose_name="عنوان القسم")
    order = models.PositiveIntegerField(default=0, verbose_name="الترتيب")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "قسم"
        verbose_name_plural = "الأقسام"
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Lesson(models.Model):
    """An individual lesson unit (video/text)."""
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255, verbose_name="عنوان الدرس")
    slug = models.SlugField(blank=True, max_length=255, allow_unicode=True)
    video_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="رابط الفيديو")
    duration_seconds = models.PositiveIntegerField(default=0, verbose_name="مدة الدرس بالثواني")
    content = models.TextField(blank=True, verbose_name="المحتوى النصي")
    is_preview = models.BooleanField(default=False, verbose_name="درس مجاني (معاينة)")
    order = models.PositiveIntegerField(default=0, verbose_name="الترتيب")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "درس"
        verbose_name_plural = "الدروس"
        ordering = ['order', 'id']

    def save(self, *args, **kwargs):
        if not self.slug:
            scope = {'section__course': self.section.course} if self.section_id else None
            self.slug = generate_unique_slug(Lesson, self.title, instance=self, scope_kwargs=scope)
        super().save(*args, **kwargs)

    @property
    def duration_formatted(self):
        if not self.duration_seconds:
            return "00:00"
        mins, secs = divmod(self.duration_seconds, 60)
        hours, mins = divmod(mins, 60)
        if hours > 0:
            return f"{hours:02d}:{mins:02d}:{secs:02d}"
        return f"{mins:02d}:{secs:02d}"

    @property
    def youtube_embed_url(self):
        """Extract YouTube embed URL if video_url is a YouTube link."""
        if not self.video_url:
            return None
        url = self.video_url.strip()
        if 'youtube.com/watch?v=' in url:
            video_id = url.split('watch?v=')[1].split('&')[0]
            return f"https://www.youtube.com/embed/{video_id}"
        if 'youtu.be/' in url:
            video_id = url.split('youtu.be/')[1].split('?')[0]
            return f"https://www.youtube.com/embed/{video_id}"
        if 'youtube.com/embed/' in url:
            return url
        return None

    def __str__(self):
        return self.title

class Resource(models.Model):
    """Downloadable files or external links attached to a lesson."""
    TYPE_CHOICES = (
        ('pdf', 'PDF ملف'),
        ('video', 'فيديو'),
        ('link', 'رابط خارجي'),
    )
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=255, verbose_name="عنوان المرفق")
    file = models.FileField(upload_to='lessons/resources/', blank=True, null=True, verbose_name="الملف")
    external_url = models.URLField(blank=True, null=True, verbose_name="الرابط الخارجي")
    resource_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='pdf', verbose_name="النوع")

    class Meta:
        verbose_name = "مرفق"
        verbose_name_plural = "المرفقات"

    def __str__(self):
        return self.title


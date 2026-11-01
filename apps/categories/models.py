# apps/categories/models.py
import uuid
from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    """Categorization for courses."""
    name = models.CharField(max_length=100, verbose_name="اسم التصنيف")
    slug = models.SlugField(unique=True, blank=True, allow_unicode=True)
    icon = models.CharField(max_length=50, blank=True, default="category", help_text="Material icon name or CSS class", verbose_name="الأيقونة")
    color = models.CharField(max_length=20, default="#6366f1", verbose_name="اللون المميِز")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories', verbose_name="التصنيف الأب")

    class Meta:
        verbose_name = "تصنيف"
        verbose_name_plural = "التصنيفات"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name, allow_unicode=True) or uuid.uuid4().hex[:8]
            slug = base_slug
            counter = 1
            qs = Category.objects.all()
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            while qs.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


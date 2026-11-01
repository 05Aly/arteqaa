# apps/categories/admin.py
from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Category

@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ('name', 'slug', 'parent', 'color')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    list_filter = ('parent',)

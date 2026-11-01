# apps/accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin
from .models import User, InstructorProfile

@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    list_display = ('email', 'username', 'get_full_name', 'role', 'is_active', 'is_verified')
    list_filter = ('role', 'is_active', 'is_verified', 'is_staff')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    # Custom fieldsets for User
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'avatar', 'bio', 'social_links')}),
        ('Permissions', {'fields': ('role', 'is_verified', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

@admin.register(InstructorProfile)
class InstructorProfileAdmin(ModelAdmin):
    list_display = ('user', 'title', 'total_students', 'total_courses', 'rating_avg')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'title')
    list_filter = ('rating_avg',)

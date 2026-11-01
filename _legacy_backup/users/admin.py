from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import User, Profile

@admin.register(Profile)
class ProfileAdmin(ModelAdmin):
    list_display = ('user', 'joined_at')
    search_fields = ('user__email',)


@admin.register(User)
class CustomUserAdmin(ModelAdmin):
    list_display = ('email', 'full_name', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('email', 'full_name')
    ordering = ('email',)
    readonly_fields = ('last_login', 'date_joined')
    list_fullwidth = True
    list_display_links = ('email', 'full_name')

    fieldsets = (
        (None, {
            'fields': ('email', 'password'),
        }),
        ('Personal Info', {
            'fields': ('full_name', 'profile_image', 'bio', 'role'),
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',),
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined'),
        }),
    )

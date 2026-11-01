from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(ModelAdmin):
    list_display = ('id', 'student', 'course', 'amount', 'status', 'transaction_id', 'created_at')
    list_filter = ('status',)
    search_fields = ('student__email', 'course__title', 'transaction_id')
    readonly_fields = ('transaction_id', 'created_at')
    list_editable = ('status',)
    list_fullwidth = True
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

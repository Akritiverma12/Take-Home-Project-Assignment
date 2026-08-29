from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, ExpenseReport, ExpenseLine, ReportHistory, AlertDismissal

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Role Info', {'fields': ('role',)}),
    )
    list_display = ['username', 'email', 'role', 'is_staff']

admin.site.register(User, CustomUserAdmin)
admin.site.register(ExpenseReport)
admin.site.register(ExpenseLine)
admin.site.register(ReportHistory)
admin.site.register(AlertDismissal)
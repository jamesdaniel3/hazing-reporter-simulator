from django.contrib import admin
from .models import CustomUser, Report, ReportFile
from django.contrib.auth.admin import UserAdmin
# Register your models here.

admin.site.register(Report)
admin.site.register(ReportFile)

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'is_site_admin']
    list_filter = [ 'is_site_admin']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_site_admin', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_superuser', 'is_active', 'is_site_admin')}
        ),
    )


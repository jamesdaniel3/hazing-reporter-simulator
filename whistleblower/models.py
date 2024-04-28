from django.contrib.auth.models import AbstractUser, Permission, Group
from django.db import models
from django.http import HttpResponse


class CustomUser(AbstractUser):
    # Add any additional fields here
    is_site_admin = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def add_custom_permission(self, permission_name):
        permission = Permission.objects.get(name=permission_name)
        self.user_permissions.add(permission)

    def remove_custom_permission(self, permission_name):
        permission = Permission.objects.get(name=permission_name)
        self.user_permissions.remove(permission)

    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        related_name='custom_user_set',
        help_text='permissions for this user',
    )

    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        related_name='custom_user_set',
        help_text='groups for this user',
    )

class Report(models.Model):
    user_name = models.TextField(null=True)
    user_email = models.TextField(null=True)
    report_file_name = models.TextField(null=True)
    description = models.TextField(default="NOT PROVIDED")
    date = models.DateField(default="NOT PROVIDED")
    time = models.TimeField(default="NOT PROVIDED")
    status = models.CharField(max_length=1, default='n')
    admin_notes = models.TextField(null=True)
    #def __str__(self):
    #    return self.report_file.name

class ReportFile(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    report_file = models.FileField(upload_to='uploads/')
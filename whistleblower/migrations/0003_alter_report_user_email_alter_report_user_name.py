# Generated by Django 5.0.2 on 2024-03-16 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('whistleblower', '0002_report'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='user_email',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='report',
            name='user_name',
            field=models.TextField(null=True),
        ),
    ]

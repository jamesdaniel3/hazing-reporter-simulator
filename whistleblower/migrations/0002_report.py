# Generated by Django 5.0.2 on 2024-03-16 11:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('whistleblower', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_name', models.TextField()),
                ('user_email', models.TextField()),
                ('report_file', models.FileField(upload_to='')),
            ],
        ),
    ]

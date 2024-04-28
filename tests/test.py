import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

import django
django.setup()

from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase, override_settings, Client
from unittest.mock import patch, MagicMock
from whistleblower.views import submit_report_action, view_report
from whistleblower.models import Report, ReportFile
from allauth.socialaccount.models import SocialApp
from django.urls import reverse


# Exporting environmental variables to not affect actual s3
os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
os.environ['AWS_SECURITY_TOKEN'] = 'testing'
os.environ['AWS_SESSION_TOKEN'] = 'testing'
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

client_id = os.getenv('SECRET_GOOGLE_CLIENT_ID')
client_secret = os.getenv('SECRET_GOOGLE_CLIENT_SECRET')


class S3UploadTests(TestCase):
    @override_settings(SOCIALACCOUNT_PROVIDERS={
        'google': {
            "SCOPE": [
                "profile",
                "email"
            ],
            "AUTH_PARAMS": {
                "access_type": "online",
                'prompt': 'select_account',
            },
            'APP': {
                'client_id': client_id,
                'secret': client_secret,
            }
        }
    })
    def setUp(self):
        self.factory = RequestFactory()
        Report.objects.all().delete()

        # Create socialapp for OAuth
        SocialApp.objects.create(provider='google',
                                 name='Google',
                                 client_id='your_testing_client_id',
                                 secret='your_testing_secret')

        # Mocking boto3.client to return a MagicMock
        self.mock_boto3_client = patch('whistleblower.views.boto3.client').start()
        self.mock_s3_client = MagicMock()
        self.mock_boto3_client.return_value = self.mock_s3_client

    def tearDown(self):
        # Clean up the patches
        patch.stopall()

    def create_mock_request(self, file_path, description='Test Description', date='2024-03-30', time='12:00:00'):
        request = self.factory.post('/submit_report_action/')
        request.user = AnonymousUser()
        request.FILES['reportFile'] = file_path
        request.POST = request.POST.copy()
        request.POST['description'] = description
        request.POST['date'] = date
        request.POST['time'] = time
        return request

    def test_submit_report_action(self):
        # Create a real Report instance
        report_instance = Report(user_name='test_user', user_email='test@example.com',
                                 report_file_name='file.jpg', description='Test Description',
                                 date='2024-03-30', time='12:00:00', status='n')

        # Create a mock request
        request = self.create_mock_request('path/to/your/file.jpg')

        # Using patch to not access the db and hopefully resolve table issues
        with patch('whistleblower.views.Report.objects.get', return_value=report_instance) as mock_get:
            response = submit_report_action(request)

        # Check that the report was saved
        self.assertEqual(Report.objects.count(), 1)

        # Checking user fields
        self.assertEqual(report_instance.user_name, 'test_user')
        self.assertEqual(report_instance.user_email, 'test@example.com')

        # Checking report details
        self.assertEqual(report_instance.description, 'Test Description')
        self.assertEqual(report_instance.date, '2024-03-30')
        self.assertEqual(report_instance.time, '12:00:00')
        self.assertEqual(report_instance.status, 'n')

        # Check that the file was uploaded to S3
        self.assertEqual(response.status_code, 200)


class ViewTestCase(TestCase):
    @override_settings(SOCIALACCOUNT_PROVIDERS={
        'google': {
            "SCOPE": [
                "profile",
                "email"
            ],
            "AUTH_PARAMS": {
                "access_type": "online",
                'prompt': 'select_account',
            },
            'APP': {
                'client_id': client_id,
                'secret': client_secret,
            }
        }
    })
    def setUp(self):
        self.client = Client()
        self.home_url = reverse('home')
        self.site_admin_url = reverse('site_admin')
        self.user_model = get_user_model()

        SocialApp.objects.create(provider='google',
                                 name='Google',
                                 client_id='your_testing_client_id',
                                 secret='your_testing_secret')

        # Create a common user
        self.common_user = self.user_model.objects.create_user(username='first_user', email='common@example.com', is_site_admin=False)

        # Create a site admin user
        self.site_admin_user = self.user_model.objects.create_user(username='second_user', email='admin@example.com', is_site_admin=True)

    def test_home_not_authenticated(self):
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('<!-- HOME PAGE -->', response.content.decode())

    def test_home_authenticated_common_user(self):
        self.client.force_login(self.common_user)
        response = self.client.get(self.home_url)
        self.assertIn('<!-- HOME PAGE -->', response.content.decode())

    def test_home_authenticated_site_admin(self):
        self.client.force_login(self.site_admin_user)
        response = self.client.get(self.home_url)
        self.assertRedirects(response, self.site_admin_url)

    def test_site_admin_access_by_common_user(self):
        self.client.force_login(self.common_user)
        response = self.client.get(self.site_admin_url)
        self.assertEqual(response.status_code, 200)

    def test_site_admin_access_by_site_admin(self):
        self.client.force_login(self.site_admin_user)
        response = self.client.get(self.site_admin_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('<!-- SITE ADMIN PAGE -->', response.content.decode())


class ReportStatusTests(TestCase):
    @override_settings(SOCIALACCOUNT_PROVIDERS={
        'google': {
            "SCOPE": [
                "profile",
                "email"
            ],
            "AUTH_PARAMS": {
                "access_type": "online",
                'prompt': 'select_account',
            },
            'APP': {
                'client_id': client_id,
                'secret': client_secret,
            }
        }
    })
    def setUp(self):
        self.factory = RequestFactory()
        Report.objects.all().delete()

        self.client = Client()
        self.user_model = get_user_model()

        # Create socialapp for OAuth
        SocialApp.objects.create(provider='google',
                                 name='Google',
                                 client_id='your_testing_client_id',
                                 secret='your_testing_secret')

        self.common_user = self.user_model.objects.create_user(username='first_user', email='common@example.com',
                                                               is_site_admin=False)

        self.site_admin_user = self.user_model.objects.create_user(username='second_user', email='admin@example.com',
                                                                   is_site_admin=True)

        # Create a sample report to test with
        self.report = Report.objects.create(user_name='testuser', user_email='test@example.com',
                                       report_file_name='test_report.txt', description='Test description',
                                       date='2024-04-14', time='12:00', status='n', admin_notes=None)


    def test_initial_status(self):
        # Create a sample report
        report = Report.objects.create(user_name='testuser', user_email='test@example.com',
                                       report_file_name='test_report.txt', description='Test description',
                                       date='2024-04-14', time='12:00', admin_notes=None)
        created_report = Report.objects.get(id=report.id)
        # Check that its status is new
        self.assertEqual(created_report.status, 'n')

    def test_report_status_change(self):
        # Admin login
        self.client.force_login(self.site_admin_user)

        self.client.post(reverse('resolve_report', kwargs={'report_id': self.report.id}))
        updated_report = Report.objects.get(id=self.report.id)

        # Resolving the report and checking its status
        self.assertEqual(updated_report.status, 'r')

    def test_report_in_progress_review(self):
        # Report instance w. all information to focus on status update + associated file
        report = Report.objects.create(user_name='test_user', user_email='test@example.com',
                                       report_file_name='test_report.txt', description='Test description',
                                       date='2024-04-14', time='12:00', status='n', admin_notes=None)
        report_file = ReportFile.objects.create(report=report, report_file='test_file.txt')

        # Request w. site admin
        request = self.factory.get(reverse('view_report', kwargs={'report_id': report.id}))
        request.user = self.site_admin_user

        # Calling view_report function
        response = view_report(request, report_id=report.id)

        # Reloading the report
        updated_report = Report.objects.get(pk=report.id)

        # Checking that the status ge
        self.assertEqual(updated_report.status, 'i')

    def test_set_report_notes(self):
        # Admin login
        self.client.force_login(self.site_admin_user)

        # Checking if setting notes works
        notes = 'Test notes'
        response = self.client.post(
            reverse('set_report_notes', kwargs={'report_id': self.report.id}),
            {'notes': notes},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'  # Include this header to mimic an AJAX request
        )
        updated_report = Report.objects.get(id=self.report.id)
        self.assertEqual(updated_report.admin_notes, notes)
        self.assertEqual(response.status_code, 200)  # Optionally check that the response status code is 200



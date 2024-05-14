import os
import pathlib
import boto3
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import logout, get_user_model
from django.contrib.auth.decorators import login_required
from .models import CustomUser, Report, ReportFile
from django.contrib import messages
from django.template import loader


def home(request):
    if request.user.is_authenticated:
        if request.user.is_site_admin:
            return redirect('/site_admin')
    return render(request, 'whistleblower/home.html')


def logout_view(request):
    logout(request)
    return redirect("/")


def make_report(request):
    return render(request, 'whistleblower/file_submission.html')


def my_reports(request):
    user = get_user_model()
    users = user.objects.exclude(id=request.user.id)
    num_users = users.count()

    reports_list = Report.objects.all()
    new_reports = reports_list.filter(status='n')
    in_progress_reports = reports_list.filter(status='i')
    resolved_reports = reports_list.filter(status='r')

    context = {
        'user': request.user,
        'num_users': num_users,
        'users': users,
        'reports_list': reports_list,
        'new_reports': new_reports,
        'in_progress_reports': in_progress_reports,
        'resolved_reports': resolved_reports,
    }

    if request.method == 'POST':
        user_id = request.POST.get('user')
        user = CustomUser.objects.get(id=user_id)
        user.is_admin = True
        user.save()
        messages.success(request, f"{user.username} is now a site admin")

    return render(request, 'whistleblower/my_reports.html', context)


def submit_report_action(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            user_name = request.user.username
            user_email = request.user.email
        else:
            user_name = "anon"
            user_email = "anon"

        report_file_submission = request.FILES.get('reportFile')

        if report_file_submission:
            report_file_name = str(report_file_submission)
        else:
            report_file_name = None
        description = request.POST.get('description')
        date = request.POST.get('date')
        time = request.POST.get('time')
        report_status = 'n'

        report = Report(user_name=user_name, user_email=user_email, report_file_name=report_file_name,
                        description=description, date=date, time=time, status=report_status)
        report.save()

        if report_file_submission:
            # Running on Heroku
            if 'cs3240-project-b-24' in request.build_absolute_uri('url'):
                if report_file_name:
                    report_file_content_type = get_content_type(pathlib.Path(str(report_file_submission)).suffix)

                    s3_bucket = 'cs3240-project-b-24-reports'
                    s3 = boto3.client('s3')
                    s3.upload_fileobj(
                        Fileobj=report_file_submission,
                        Bucket=s3_bucket,
                        Key='uploaded-files/' + (str(report.id) + '_' + str(report.report_file_name)),
                        ExtraArgs={'ContentDisposition': 'inline', 'ContentType': report_file_content_type})
            # Running locally
            else:
                report_file = ReportFile(report=report, report_file=report_file_submission)
                report_file.save()

    return render(request, 'whistleblower/home.html')


def get_content_type(file_type):
    if file_type == ".jpg" or file_type == ".jpeg":
        return "image/jpeg"
    elif file_type == ".png":
        return "image/png"
    elif file_type == ".txt":
        return "text/plain"
    elif file_type == ".pdf":
        return "application/pdf"

    return "binary/octet-stream"


def view_report(request, report_id):
    template = loader.get_template("whistleblower/report_view.html")
    current_report = get_object_or_404(Report, pk=report_id)
    current_report_file = "Not Provided"
    current_report_file_type = None

    # Running on Heroku
    if 'cs3240-project-b-24' in request.build_absolute_uri('url'):
        if current_report.report_file_name:
            current_report_file_name, current_report_file_type = os.path.splitext(current_report.report_file_name)
            # Get report from S3 using URL hotlink
            s3_bucket = 'cs3240-project-b-24-reports'
            s3_url = 'https://' + s3_bucket + '.s3.amazonaws.com/'
            current_report_file = s3_url + 'uploaded-files/' + str(current_report.id) + '_' + current_report.report_file_name

    # Running locally
    else:
        if current_report.report_file_name:
            current_report_file_name, current_report_file_type = os.path.splitext(current_report.report_file_name)
            file = get_object_or_404(ReportFile, report_id=current_report.id)
            current_report_file = request.scheme + '://' + request.get_host() + file.report_file.url

    if request.user.is_site_admin:
        if current_report.status == 'n':
            current_report.status = 'i'
            current_report.save()

    context = {
        "current_report": current_report,
        "current_report_file_type": current_report_file_type,
        "current_report_file": current_report_file
    }

    response = HttpResponse(template.render(context, request))

    return response


def delete_report(request, report_id):
    current_report = get_object_or_404(Report, pk=report_id)
    current_report.delete()
    return redirect('/my_reports')


def resolve_report(request, report_id):
    current_report = get_object_or_404(Report, pk=report_id)

    new_notes = request.POST.get('notes')
    if current_report.admin_notes != new_notes:
        current_report.admin_notes = new_notes

    current_report.status = 'r'
    current_report.save()
    return redirect('/site_admin')


def reopen_report(request, report_id):
    current_report = get_object_or_404(Report, pk=report_id)

    new_notes = request.POST.get('notes')
    if current_report.admin_notes != new_notes:
        current_report.admin_notes = new_notes

    current_report.status = 'i'
    current_report.save()
    return redirect('/site_admin')


def set_report_notes(request, report_id):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        current_report = get_object_or_404(Report, pk=report_id)
        current_report.admin_notes = request.POST.get('notes')
        current_report.save()
        return JsonResponse({'notes': current_report.admin_notes}, status=200)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def site_admin(request):
    user = get_user_model()
    users = user.objects.exclude(id=request.user.id)
    num_users = users.count()

    reports_list = Report.objects.all()

    if request.method == 'POST':
        user_id = request.POST.get('user')
        user = CustomUser.objects.get(id=user_id)
        user.is_admin = True
        user.save()
        messages.success(request, f"{user.username} is now a site admin")

    context = {
        'user': request.user,
        'num_users': num_users,
        'users': users,
        'reports_list': reports_list,
    }

    return render(request, 'whistleblower/site_admin.html', context)

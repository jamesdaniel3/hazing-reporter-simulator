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
        else:
            return render(request, 'whistleblower/home.html')
    return render(request, 'whistleblower/home.html')


def logout_view(request):
    logout(request)
    return redirect("/")


def make_report(request):
    return render(request, 'whistleblower/file_submission.html')


def my_reports(request):
    User = get_user_model()
    users = User.objects.exclude(id=request.user.id)  # all users except the current
    num_users = users.count()  # count to make sure displaying right num, debugging

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
        messages.success(request, f"{user.username} is now a site admin")  # success message

    return render(request, 'whistleblower/my_reports.html', context)


def submit_report_action(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            userName = request.user.username
            userEmail = request.user.email
        else:
            userName = "anon"
            userEmail = "anon"

        reportFileSubmission = request.FILES.get('reportFile')

        if reportFileSubmission:
            reportFileName =str(reportFileSubmission)
        else:
            reportFileName = None
        description = request.POST.get('description')
        date = request.POST.get('date')
        time = request.POST.get('time')
        reportStatus ='n'
        
        #admin notes will be null for now, since it has just been created

        report = Report(user_name=userName, user_email=userEmail, report_file_name=reportFileName,
                        description=description, date=date, time=time, status=reportStatus)
        report.save()

        if reportFileSubmission:
            # Running on Heroku
            if 'cs3240-project-b-24' in request.build_absolute_uri('url'):
                if reportFileName:
                    report_file_content_type = get_content_type(pathlib.Path(str(reportFileSubmission)).suffix)

                    S3_BUCKET = 'cs3240-project-b-24-reports'
                    s3 = boto3.client('s3')
                    s3.upload_fileobj(
                        Fileobj=reportFileSubmission,
                        Bucket=S3_BUCKET,
                        Key='uploaded-files/' + (str(report.id) + '_' + str(report.report_file_name)),
                        ExtraArgs={'ContentDisposition': 'inline', 'ContentType': report_file_content_type})
            # Running locally
            else:
                reportFile = ReportFile(report=report, report_file=reportFileSubmission)
                reportFile.save()

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


def view_report(request, report_id, *args, **kwargs):
    template = loader.get_template("whistleblower/report_view.html")
    current_report = get_object_or_404(Report, pk=report_id)
    current_report_file = "Not Provided"
    current_report_file_type = None

    # Running on Heroku
    if 'cs3240-project-b-24' in request.build_absolute_uri('url'):
        if current_report.report_file_name:
            current_report_file_name, current_report_file_type = os.path.splitext(current_report.report_file_name)
            # Get report from S3 using URL hotlink
            S3_BUCKET = 'cs3240-project-b-24-reports'
            S3_URL = 'https://' + S3_BUCKET + '.s3.amazonaws.com/'
            current_report_file = S3_URL + 'uploaded-files/' + str(current_report.id) + '_' + current_report.report_file_name

    #Running locally
    else:
        #Get report from database
        if current_report.report_file_name:
            current_report_file_name, current_report_file_type = os.path.splitext(current_report.report_file_name)
            file = get_object_or_404(ReportFile, report_id=current_report.id)
            current_report_file = request.scheme + '://' + request.get_host() + file.report_file.url

    if(request.user.is_site_admin): 
        if(current_report.status=='n'):
            current_report.status='i'
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
        # Return the updated notes in the response
        return JsonResponse({'notes': current_report.admin_notes}, status=200)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def site_admin(request):
    User = get_user_model()
    users = User.objects.exclude(id=request.user.id)  # all users except the current
    num_users = users.count()  # count to make sure displaying right num, debugging

    reports_list = Report.objects.all()

    if request.method == 'POST':
        user_id = request.POST.get('user')
        user = CustomUser.objects.get(id=user_id)
        user.is_admin = True
        user.save()
        messages.success(request, f"{user.username} is now a site admin")  # success message

    context = {
        'user': request.user,
        'num_users': num_users,
        'users': users,
        'reports_list': reports_list,
    }

    return render(request, 'whistleblower/site_admin.html', context)
    # pass all necessary info to display


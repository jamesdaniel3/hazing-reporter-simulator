from django import template

register = template.Library()

@register.filter
def filter_status(reports_list, status):
    return [report for report in reports_list if report.status == status]

@register.filter
def filter_user(reports_list, username):
    return [report for report in reports_list if report.user_name == username]
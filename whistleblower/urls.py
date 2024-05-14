from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("", views.home, name="home"),
    path("logout", views.logout_view),
    path("make_report", views.make_report),
    path("my_reports", views.my_reports),
    path("site_admin", views.site_admin, name="site_admin"),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path("submitted_report", views.submit_report_action, name="submit_report_action"),
    path("report_view/<int:report_id>", views.view_report, name="view_report"),
    path("set_report_notes/<int:report_id>", views.set_report_notes, name="set_report_notes"),
    path("delete_report/<int:report_id>", views.delete_report, name="delete_report"),
    path("resolve_report/<int:report_id>", views.resolve_report, name="resolve_report"),
    path("reopen_report/<int:report_id>", views.reopen_report, name="reopen_report"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
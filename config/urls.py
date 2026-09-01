from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from expenses import views

urlpatterns = [
    path('admin/', admin.site.urls),
    # Adds Django's built-in login/logout URLs under /accounts/
    path('accounts/', include('django.contrib.auth.urls')), 

    path('', views.dashboard, name='dashboard'),
    path('report/new/', views.create_report, name='create_report'),
    path('report/<int:pk>/', views.report_detail, name='report_detail'),
    path('report/<int:pk>/submit/', views.submit_report, name='submit_report'),
    path('report/<int:pk>/archive/', views.archive_report, name='archive_report'),
    path('report/<int:pk>/restore/', views.restore_report, name='restore_report'),
    path('report/<int:pk>/approve/', views.approve_report, name='approve_report'),
    path('report/<int:pk>/reject/', views.reject_report, name='reject_report'),
    path('report/<int:pk>/mark-paid/', views.mark_as_paid, name='mark_as_paid'),
    path('report/<int:pk>/assign-approvers/', views.assign_approvers, name='assign_approvers'),
    path('report/<int:pk>/dismiss-alert/', views.dismiss_alert, name='dismiss_alert'),
    path('reports/<int:report_id>/line/<int:line_id>/edit/', views.edit_line, name='edit_line'),
    path('report/<int:report_pk>/line/<int:line_pk>/delete/', views.delete_line, name='delete_line'),
    path('reports/bulk-action/', views.bulk_report_action, name='bulk_report_action'),
    path('reports/export-csv/', views.export_unpaid_csv, name='export_unpaid_csv'),
    path('reports/<int:pk>/comment/', views.add_timeline_comment, name='add_timeline_comment'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
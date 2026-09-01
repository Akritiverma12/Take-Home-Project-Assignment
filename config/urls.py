"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from expenses import views

urlpatterns = [
    path('admin/', admin.site.urls),
    # Adds Django's built-in login/logout URLs
    path('', include('django.contrib.auth.urls')), 

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
    path('report/<int:report_pk>/line/<int:line_pk>/edit/', views.edit_line, name='edit_line'),
    path('report/<int:report_pk>/line/<int:line_pk>/delete/', views.delete_line, name='delete_line'),
    path('reports/bulk-action/', views.bulk_report_action, name='bulk_report_action'),
    path('reports/export-csv/', views.export_unpaid_csv, name='export_unpaid_csv'),
    path('reports/<int:pk>/comment/', views.add_timeline_comment, name='add_timeline_comment'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
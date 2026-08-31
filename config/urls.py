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
]

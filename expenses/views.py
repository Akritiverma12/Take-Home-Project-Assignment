import csv
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from .models import ExpenseReport, ExpenseLine, ReportHistory, User,AlertDismissal
from .forms import ExpenseReportForm, ExpenseLineForm
from django.utils import timezone
from datetime import timedelta

def get_active_stale_alerts(approver, stale_days=3, return_days=3):
    if not hasattr(approver, 'role') or approver.role != 'APPROVER':
        return ExpenseReport.objects.none()

    stale_cutoff = timezone.now() - timedelta(days=stale_days)
    return_cutoff = timezone.now() - timedelta(days=return_days)

    # Fetch submitted reports pending >= stale_days (excluding approver's own reports)
    submitted_reports = ExpenseReport.objects.filter(
        status='SUBMITTED',
        submitted_at__lte=stale_cutoff
    ).exclude(owner=approver)

    active_alert_ids = []
    for report in submitted_reports:
        dismissal = AlertDismissal.objects.filter(report=report, approver=approver).first()
        # Active if never dismissed or if dismissal expired (> return_days)
        if not dismissal or (dismissal.dismissed_at and dismissal.dismissed_at <= return_cutoff):
            active_alert_ids.append(report.id)

    return ExpenseReport.objects.filter(id__in=active_alert_ids)
@login_required
def dashboard(request):
    show_archived = request.GET.get('archived') == 'true'
    queue_filter = request.GET.get('queue', 'all')
    search_query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()
    
    if request.user.role == 'APPROVER':
        reports = ExpenseReport.objects.exclude(status='DRAFT')
        if queue_filter == 'assigned':
            reports = reports.filter(assigned_approvers=request.user)
    else:
        # Fixed: Initialize queryset properly for employees
        reports = ExpenseReport.objects.filter(owner=request.user)
        
    # Archive filter
    if show_archived:
        reports = reports.filter(is_archived=True)
    else:
        reports = reports.filter(is_archived=False)

    # Search filter (Title or Owner's Username)
    if search_query:
        reports = reports.filter(
            Q(title__icontains=search_query) | 
            Q(owner__username__icontains=search_query)
        )

    # Status filter
    if status_filter:
        reports = reports.filter(status=status_filter)
        
    reports = reports.order_by('-created_at')

    # Pagination (5 reports per page)
    paginator = Paginator(reports, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    approvers = User.objects.filter(role='APPROVER')
    # Goal 10: Fetch stale alerts for approver
    alerts = []
    if request.user.role == 'APPROVER':
        alerts = get_active_stale_alerts(request.user, stale_days=3, return_days=3)
    return render(request, 'expenses/dashboard.html', {
        'page_obj': page_obj,
        'reports': page_obj.object_list,
        'show_archived': show_archived,
        'queue_filter': queue_filter,
        'search_query': search_query,
        'status_filter': status_filter,
        'approvers': approvers,
        'status_choices': ExpenseReport.STATUS_CHOICES,
        'alerts': alerts,
    })
@login_required
def dismiss_alert(request, pk):
    if request.user.role != 'APPROVER':
        return HttpResponseForbidden("Only approvers can dismiss alerts.")
        
    report = get_object_or_404(ExpenseReport, pk=pk)
    if request.method == 'POST':
        AlertDismissal.objects.get_or_create(report=report, approver=request.user)
    return redirect('dashboard')
@login_required
def create_report(request):
    if request.method == 'POST':
        form = ExpenseReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.owner = request.user
            report.save()
            return redirect('dashboard')
    else:
        form = ExpenseReportForm()
    return render(request, 'expenses/create_report.html', {'form': form})

@login_required
def report_detail(request, pk):
    if request.user.role == 'APPROVER':
        report = get_object_or_404(ExpenseReport, pk=pk)
    else:
        report = get_object_or_404(ExpenseReport, pk=pk, owner=request.user)
    
    if request.method == 'POST':
        form = ExpenseLineForm(request.POST,request.FILES)
        if form.is_valid():
            line = form.save(commit=False)
            line.report = report
            line.save()
            return redirect('report_detail', pk=report.pk)
    else:
        form = ExpenseLineForm()
        
    approvers = User.objects.filter(role='APPROVER')
    return render(request, 'expenses/report_detail.html', {
        'report': report, 
        'form': form,
        'approvers': approvers
    })

@login_required
def assign_approvers(request, pk):
    report = get_object_or_404(ExpenseReport, pk=pk)
    if request.method == 'POST':
        approver_ids = request.POST.getlist('approvers')
        report.assigned_approvers.set(approver_ids)
        report.save()
    return redirect('report_detail', pk=report.pk)

@login_required
def submit_report(request, pk):
    report = get_object_or_404(ExpenseReport, pk=pk, owner=request.user)
    
    if report.status not in ['DRAFT', 'REJECTED']:
        return HttpResponseBadRequest(f"Goal 4 Rule Violation: Cannot submit a report in '{report.status}' status.")
    if not report.lines.exists():
        return HttpResponseBadRequest("Goal 4 Rule Violation: Cannot submit a report without any expense lines.")

    if request.method == 'POST':
        comment_text = "Resubmitted for approval." if report.status == 'REJECTED' else "Submitted for approval."
        ReportHistory.objects.create(
            report=report,
            changed_by=request.user,
            old_status=report.status,
            new_status='SUBMITTED',
            comment=comment_text
        )
        report.status = 'SUBMITTED'
        report.submitted_at = timezone.now()  # <--- Added for Stale Alerts (Goal 10)
        report.rejection_reason = ""
        report.save()
    return redirect('report_detail', pk=report.pk)

@login_required
def approve_report(request, pk):
    if request.user.role != 'APPROVER':
        return HttpResponseForbidden("Only approvers can perform this action.")
        
    report = get_object_or_404(ExpenseReport, pk=pk)
    if report.owner == request.user:
        return HttpResponseForbidden("Goal 1 Rule Violation: Approvers cannot approve their own reports.")
        
    # Goal 4 Lifecycle Guard
    if report.status != 'SUBMITTED':
        return HttpResponseBadRequest(f"Goal 4 Rule Violation: Cannot approve a report in '{report.status}' status. Must be 'SUBMITTED'.")
        
    if request.method == 'POST':
        ReportHistory.objects.create(
            report=report,
            changed_by=request.user,
            old_status=report.status,
            new_status='APPROVED',
            comment="Report approved."
        )
        report.status = 'APPROVED'
        report.save()
    return redirect('report_detail', pk=report.pk)

@login_required
def reject_report(request, pk):
    if request.user.role != 'APPROVER':
        return HttpResponseForbidden("Only approvers can perform this action.")
        
    report = get_object_or_404(ExpenseReport, pk=pk)
    if report.owner == request.user:
        return HttpResponseForbidden("Goal 1 Rule Violation: Approvers cannot reject their own reports.")
        
    # Goal 4 Lifecycle Guard
    if report.status != 'SUBMITTED':
        return HttpResponseBadRequest(f"Goal 4 Rule Violation: Cannot reject a report in '{report.status}' status. Must be 'SUBMITTED'.")
        
    reason = request.POST.get('rejection_reason', '').strip()
    if not reason:
        return HttpResponseBadRequest("Goal 4 Rule Violation: A specific rejection reason is required.")

    if request.method == 'POST':
        ReportHistory.objects.create(
            report=report,
            changed_by=request.user,
            old_status=report.status,
            new_status='REJECTED',
            comment=f"Report rejected: {reason}"
        )
        report.status = 'REJECTED'
        report.rejection_reason = reason
        report.save()
    return redirect('report_detail', pk=report.pk)

@login_required
def mark_as_paid(request, pk):
    if request.user.role != 'APPROVER':
        return HttpResponseForbidden("Only approvers can mark reports as paid.")
        
    report = get_object_or_404(ExpenseReport, pk=pk)
    if report.owner == request.user:
        return HttpResponseForbidden("Goal 1 Rule Violation: Approvers cannot mark their own report as paid.")
        
    # Goal 4 Lifecycle Guard
    if report.status != 'APPROVED':
        return HttpResponseBadRequest(f"Goal 4 Rule Violation: Cannot mark report as paid from '{report.status}' status. Must be 'APPROVED'.")
        
    if request.method == 'POST':
        ReportHistory.objects.create(
            report=report,
            changed_by=request.user,
            old_status=report.status,
            new_status='PAID',
            comment="Reimbursement marked as PAID."
        )
        report.status = 'PAID'
        report.save()
    return redirect('report_detail', pk=report.pk)

@login_required
def archive_report(request, pk):
    report = get_object_or_404(ExpenseReport, pk=pk, owner=request.user)
    if request.method == 'POST':
        report.is_archived = True
        report.save()
    return redirect('dashboard')

@login_required
def restore_report(request, pk):
    report = get_object_or_404(ExpenseReport, pk=pk, owner=request.user)
    if request.method == 'POST':
        report.is_archived = False
        report.save()
    return redirect('dashboard')

@login_required
def edit_line(request, report_pk, line_pk):
    report = get_object_or_404(ExpenseReport, pk=report_pk, owner=request.user)
    if report.status not in ['DRAFT', 'REJECTED']:
        return HttpResponseForbidden("Goal 3 Violation: Lines can only be edited on Draft or Rejected reports.")
        
    line = get_object_or_404(ExpenseLine, pk=line_pk, report=report)
    if request.method == 'POST':
        form = ExpenseLineForm(request.POST, request.FILES,instance=line)
        if form.is_valid():
            form.save()
            return redirect('report_detail', pk=report.pk)
    else:
        form = ExpenseLineForm(instance=line)
        
    return render(request, 'expenses/edit_line.html', {'form': form, 'report': report, 'line': line})

@login_required
def delete_line(request, report_pk, line_pk):
    report = get_object_or_404(ExpenseReport, pk=report_pk, owner=request.user)
    if report.status not in ['DRAFT', 'REJECTED']:
        return HttpResponseForbidden("Goal 3 Violation: Lines can only be deleted on Draft or Rejected reports.")
        
    line = get_object_or_404(ExpenseLine, pk=line_pk, report=report)
    if request.method == 'POST':
        line.delete()
    return redirect('report_detail', pk=report.pk)
@login_required
def bulk_report_action(request):
    if request.user.role != 'APPROVER':
        return HttpResponseForbidden("Only approvers can perform bulk actions.")

    if request.method == 'POST':
        action = request.POST.get('action')
        report_ids = request.POST.getlist('selected_reports')
        rejection_reason = request.POST.get('bulk_rejection_reason', 'Bulk rejected').strip()

        if not report_ids:
            messages.warning(request, "No reports were selected for bulk action.")
            return redirect('dashboard')

        reports = ExpenseReport.objects.filter(id__in=report_ids)

        for report in reports:
            # Check Rule 1: Cannot approve or reject your own report
            if report.owner == request.user:
                messages.error(
                    request, 
                    f"Refused '{report.title}': You are the owner of this report (Approvers cannot decide on their own reports)."
                )
                continue

            # Check Rule 2: Report must be in SUBMITTED state
            if report.status != 'SUBMITTED':
                messages.warning(
                    request, 
                    f"Skipped '{report.title}': Report is currently in '{report.status}' state."
                )
                continue

            # Apply Action
            old_status = report.status
            if action == 'approve':
                report.status = 'APPROVED'
                report.save()
                ReportHistory.objects.create(
                    report=report,
                    changed_by=request.user,
                    old_status=old_status,
                    new_status='APPROVED',
                    comment='Bulk approved via dashboard'
                )
                messages.success(request, f"Approved '{report.title}'.")

            elif action == 'reject':
                report.status = 'REJECTED'
                report.rejection_reason = rejection_reason
                report.save()
                ReportHistory.objects.create(
                    report=report,
                    changed_by=request.user,
                    old_status=old_status,
                    new_status='REJECTED',
                    comment=f"Bulk rejected: {rejection_reason}"
                )
                messages.success(request, f"Rejected '{report.title}'.")

    return redirect('dashboard')

@login_required
def export_unpaid_csv(request):
    if request.user.role != 'APPROVER':
        return HttpResponseForbidden("Only approvers can export reimbursements.")

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="unpaid_reimbursements.csv"'

    writer = csv.writer(response)
    writer.writerow(['Report ID', 'Title', 'Owner Email/Username', 'Start Date', 'End Date', 'Total Amount ($)', 'Status'])

    approved_reports = ExpenseReport.objects.filter(status='APPROVED').order_by('-created_at')

    for report in approved_reports:
        writer.writerow([
            report.id,
            report.title,
            report.owner.username,
            report.start_date,
            report.end_date,
            report.total_amount,
            report.status
        ])

    return response
@login_required
def add_timeline_comment(request, pk):
    report = get_object_or_404(ExpenseReport, pk=pk)
    
    # Permission check: owner or approver
    if report.owner != request.user and request.user.role != 'APPROVER':
        return HttpResponseForbidden(" You cannot comment on this report.")

    if request.method == 'POST':
        comment_text = request.POST.get('comment', '').strip()
        if comment_text:
            ReportHistory.objects.create(
                report=report,
                changed_by=request.user,
                old_status=report.status,
                new_status=report.status,
                comment=comment_text
            )
            messages.success(request, "Comment added to audit timeline.")

    return redirect('report_detail', pk=pk)
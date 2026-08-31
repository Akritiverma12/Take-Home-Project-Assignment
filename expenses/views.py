from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from .models import ExpenseReport, ExpenseLine, ReportHistory, User
from .forms import ExpenseReportForm, ExpenseLineForm

@login_required
def dashboard(request):
    show_archived = request.GET.get('archived') == 'true'
    queue_filter = request.GET.get('queue', 'all')  # 'all' or 'assigned'
    
    if request.user.role == 'APPROVER':
        # Approvers see submitted/reviewed reports
        reports = ExpenseReport.objects.exclude(status='DRAFT')
        if queue_filter == 'assigned':
            reports = reports.filter(assigned_approvers=request.user)
    else:
        # Employees see only their own reports
        reports = ExpenseReport.objects.filter(owner=request.user)
        
    if show_archived:
        reports = reports.filter(is_archived=True)
    else:
        reports = reports.filter(is_archived=False)
        
    reports = reports.order_by('-created_at')
    
    # Pass all approvers for assignment dropdowns
    approvers = User.objects.filter(role='APPROVER')
    
    return render(request, 'expenses/dashboard.html', {
        'reports': reports, 
        'show_archived': show_archived,
        'queue_filter': queue_filter,
        'approvers': approvers
    })

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
        form = ExpenseLineForm(request.POST)
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
    
    # Goal 4 Lifecycle Guard
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
        form = ExpenseLineForm(request.POST, instance=line)
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
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ExpenseReport, ExpenseLine, ReportHistory
from .forms import ExpenseReportForm, ExpenseLineForm

@login_required
def dashboard(request):
    if request.user.role == 'APPROVER':
        reports = ExpenseReport.objects.exclude(status='DRAFT').order_by('-updated_at')
    else:
        reports = ExpenseReport.objects.filter(owner=request.user).order_by('-created_at')
        
    return render(request, 'expenses/dashboard.html', {'reports': reports})

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
        
    return render(request, 'expenses/report_detail.html', {'report': report, 'form': form})

@login_required
def submit_report(request, pk):
    report = get_object_or_404(ExpenseReport, pk=pk, owner=request.user)
    # Allow submitting if status is DRAFT or REJECTED
    if request.method == 'POST' and report.status in ['DRAFT', 'REJECTED'] and report.lines.exists():
        comment_text = "Resubmitted for approval after changes." if report.status == 'REJECTED' else "Submitted for approval."
        
        ReportHistory.objects.create(
            report=report,
            changed_by=request.user,
            old_status=report.status,
            new_status='SUBMITTED',
            comment=comment_text
        )
        report.status = 'SUBMITTED'
        report.rejection_reason = ""  # Clear previous rejection reason
        report.save()
    return redirect('report_detail', pk=report.pk)

@login_required
def approve_report(request, pk):
    if request.user.role != 'APPROVER':
        return redirect('dashboard')
        
    report = get_object_or_404(ExpenseReport, pk=pk)
    if request.method == 'POST' and report.status == 'SUBMITTED':
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
        return redirect('dashboard')
        
    report = get_object_or_404(ExpenseReport, pk=pk)
    if request.method == 'POST' and report.status == 'SUBMITTED':
        reason = request.POST.get('rejection_reason', 'No reason provided.')
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
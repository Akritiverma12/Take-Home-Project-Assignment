from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ExpenseReport, ExpenseLine
from .forms import ExpenseReportForm, ExpenseLineForm

@login_required
def dashboard(request):
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
    # Fetch the specific report, ensuring the logged-in user actually owns it
    report = get_object_or_404(ExpenseReport, pk=pk, owner=request.user)
    
    if request.method == 'POST':
        form = ExpenseLineForm(request.POST)
        if form.is_valid():
            line = form.save(commit=False)
            line.report = report  # Link the expense line to this report
            line.save()
            return redirect('report_detail', pk=report.pk)
    else:
        form = ExpenseLineForm()
        
    return render(request, 'expenses/report_detail.html', {'report': report, 'form': form})
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import ExpenseReport
from .forms import ExpenseReportForm

@login_required
def dashboard(request):
    # Fetch reports owned by the logged-in user
    reports = ExpenseReport.objects.filter(owner=request.user).order_by('-created_at')
    return render(request, 'expenses/dashboard.html', {'reports': reports})

@login_required
def create_report(request):
    if request.method == 'POST':
        form = ExpenseReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.owner = request.user  # Assign the logged-in user as the owner
            report.save()
            return redirect('dashboard')
    else:
        form = ExpenseReportForm()
    
    return render(request, 'expenses/create_report.html', {'form': form})
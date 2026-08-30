from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    # This view requires the user to be logged in
    return render(request, 'expenses/dashboard.html')

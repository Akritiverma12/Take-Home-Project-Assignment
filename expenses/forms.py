from django import forms
from .models import ExpenseReport

class ExpenseReportForm(forms.ModelForm):
    class Meta:
        model = ExpenseReport
        fields = ['title', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
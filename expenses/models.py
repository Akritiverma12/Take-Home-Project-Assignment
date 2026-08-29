
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    class Role(models.TextChoices):
        EMPLOYEE = 'EMPLOYEE', 'Employee'
        APPROVER = 'APPROVER', 'Approver'

    role = models.CharField(
        max_length=20, 
        choices=Role.choices, 
        default=Role.EMPLOYEE
    )

class ExpenseReport(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        SUBMITTED = 'SUBMITTED', 'Submitted'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        PAID = 'PAID', 'Paid'

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    title = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    is_archived = models.BooleanField(default=False)
    rejection_reason = models.TextField(blank=True, null=True)
    assigned_approvers = models.ManyToManyField(User, related_name='assigned_reports', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_amount(self):
        """Calculates total expense report amount on the server."""
        return sum(line.amount for line in self.lines.all())

class ExpenseLine(models.Model):
    class Category(models.TextChoices):
        TRAVEL = 'TRAVEL', 'Travel'
        MEALS = 'MEALS', 'Meals'
        SUPPLIES = 'SUPPLIES', 'Supplies'
        OTHER = 'OTHER', 'Other'

    report = models.ForeignKey(ExpenseReport, on_delete=models.CASCADE, related_name='lines')
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=Category.choices)
    description = models.TextField()

class ReportHistory(models.Model):
    report = models.ForeignKey(ExpenseReport, on_delete=models.CASCADE, related_name='history')
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    comment = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

class AlertDismissal(models.Model):
    report = models.ForeignKey(ExpenseReport, on_delete=models.CASCADE)
    approver = models.ForeignKey(User, on_delete=models.CASCADE)
    dismissed_at = models.DateTimeField(auto_now=True)
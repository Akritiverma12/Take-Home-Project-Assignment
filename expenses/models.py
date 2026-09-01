from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta

class User(AbstractUser):
    ROLE_CHOICES = (
        ('EMPLOYEE', 'Employee'),
        ('APPROVER', 'Approver'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='EMPLOYEE')

class ExpenseReport(models.Model):
    STATUS_CHOICES = (
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Submitted'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('PAID', 'Paid'),
    )

    title = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    assigned_approvers = models.ManyToManyField(User, related_name='assigned_reports', blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    rejection_reason = models.TextField(blank=True, null=True)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(blank=True, null=True)

    def total_amount(self):
        return sum(line.amount for line in self.lines.all())

    def is_stale(self, days=3):
        if self.status == 'SUBMITTED' and self.submitted_at:
            return timezone.now() >= self.submitted_at + timedelta(days=days)
        return False

    def __str__(self):
        return f"{self.title} - {self.owner.username} ({self.status})"


CATEGORY_LIMITS = {
    'MEALS': 100.00,
    'TRAVEL': 500.00,
    'SUPPLIES': 250.00,
    'LODGING': 300.00,
    'OTHER': 150.00,
}

class ExpenseLine(models.Model):
    CATEGORY_CHOICES = (
        ('TRAVEL', 'Travel'),
        ('MEALS', 'Meals'),
        ('SUPPLIES', 'Supplies'),
        ('LODGING', 'Lodging'),
        ('OTHER', 'Other'),
    )

    report = models.ForeignKey(ExpenseReport, on_delete=models.CASCADE, related_name='lines')
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField()
    receipt = models.FileField(upload_to='receipts/', blank=True, null=True)

    @property
    def policy_limit(self):
        return CATEGORY_LIMITS.get(self.category.upper(), 200.00)

    @property
    def exceeds_policy(self):
        return float(self.amount) > float(self.policy_limit)

    def __str__(self):
        return f"{self.category}: ${self.amount} ({self.date})"


class ReportHistory(models.Model):
    report = models.ForeignKey(ExpenseReport, on_delete=models.CASCADE, related_name='history')
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    comment = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def save(self, *args, **kwargs):
        if self.pk:
            raise PermissionError("Goal 9 Enforcement: Audit history entries are immutable and cannot be updated.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise PermissionError("Goal 9 Enforcement: Audit history entries are immutable and cannot be deleted.")

    def __str__(self):
        return f"{self.report.title}: {self.old_status} -> {self.new_status} by {self.changed_by.username}"


class AlertDismissal(models.Model):
    report = models.ForeignKey(ExpenseReport, on_delete=models.CASCADE, related_name='dismissals')
    approver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dismissed_alerts')
    dismissed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('report', 'approver')

    def is_expired(self, return_days=3):
        return timezone.now() >= self.dismissed_at + timedelta(days=return_days)
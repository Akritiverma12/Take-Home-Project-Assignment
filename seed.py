import os
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from expenses.models import ExpenseReport, ExpenseLine

User = get_user_model()

def run_seed():
    print("Clearing database...")
    ExpenseLine.objects.all().delete()
    ExpenseReport.objects.all().delete()
    User.objects.exclude(is_superuser=True).delete()

    print("Creating user accounts...")
    
    # 1. Admin Account
    admin, created = User.objects.get_or_create(username='akriti')
    admin.set_password('0204')
    admin.is_staff = True
    admin.is_superuser = True
    if hasattr(admin, 'role'):
        admin.role = 'ADMIN'
    admin.save()

    # 2. Approver Account
    approver, _ = User.objects.get_or_create(username='approver1')
    approver.set_password('password123!')
    if hasattr(approver, 'role'):
        approver.role = 'APPROVER'
    approver.save()

    # 3. Employee Account
    employee, _ = User.objects.get_or_create(username='employee1')
    employee.set_password('password123!')
    if hasattr(employee, 'role'):
        employee.role = 'EMPLOYEE'
    employee.save()

    print("Creating sample expense reports...")

    # Report 1: Draft Status
    report1 = ExpenseReport.objects.create(
        owner=employee,
        title="Q3 Client Onboarding Travel",
        start_date=date.today() - timedelta(days=10),
        end_date=date.today() - timedelta(days=2),
        status='DRAFT'
    )

    ExpenseLine.objects.create(
        report=report1,
        date=date.today() - timedelta(days=8),
        category='Travel',
        amount=250.00,
        description='Flight tickets to client headquarters'
    )

    ExpenseLine.objects.create(
        report=report1,
        date=date.today() - timedelta(days=5),
        category='Meals',
        amount=45.50,
        description='Client dinner meeting'
    )

    # Report 2: Submitted Status (Assigned to Approver)
    report2 = ExpenseReport.objects.create(
        owner=employee,
        title="Software & Office Supplies",
        start_date=date.today() - timedelta(days=20),
        end_date=date.today() - timedelta(days=15),
        status='SUBMITTED'
    )
    if hasattr(report2, 'assigned_approvers'):
        report2.assigned_approvers.add(approver)

    ExpenseLine.objects.create(
        report=report2,
        date=date.today() - timedelta(days=18),
        category='Supplies',
        amount=120.00,
        description='Developer monitor stand and cables'
    )

    print("Database seeding completed successfully!")

if __name__ == '__main__':
    run_seed()
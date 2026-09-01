# Django Expense Reimbursement System

A full-stack expense reimbursement platform built with Django. Supports multi-role approval workflows, spending policy enforcement, receipt uploads, soft archiving, and audit history tracking.

## Core Features
* **Role-Based Access Control:** Distinct workflows for Admins, Approvers, and Employees.
* **Policy Enforcement:** Automated flags for category limit exceedances (e.g., Meals over $50).
* **Receipt Uploads:** Attach and view receipt files/PDFs per line item.
* **Audit Trail:** Immutable timeline logging state transitions and comments.
* **Archiving:** Soft-archive and restore old expense reports.

## Quick Start Setup

1. **Activate Environment & Install Dependencies:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   pip install django pillow
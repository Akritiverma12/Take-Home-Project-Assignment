# System Architecture

## Overview
The Expense Reimbursement System is built as a Django monolithic application utilizing Model-View-Template (MVT) architecture for server-side rendering, role-based access control, and state management.

## Key Components
* **Authentication & RBAC:** Extends Django's `AbstractUser` with standard roles (`ADMIN`, `APPROVER`, `EMPLOYEE`).
* **Data Processing Layer:** Handles state transitions (`DRAFT` -> `SUBMITTED` -> `APPROVED` / `REJECTED` -> `PAID`), budget policy checks, and stale approval tracking.
* **Storage & File Handling:** Handles file uploads for receipts via `FileField` powered by Pillow, stored in `/media/receipts/`.
* **Audit Trail Engine:** Maintains an immutable `ReportHistory` model capturing state changes, timestamps, user actions, and contextual comments.
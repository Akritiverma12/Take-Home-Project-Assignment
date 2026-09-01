# Architecture Decision Log

## Decision 1: Monolithic Architecture over REST API
* **Context:** Need rapid implementation of core goals and admin workflows.
* **Decision:** Built using standard Django views and HTML templates rather than a decoupled Django REST Framework + React setup.
* **Outcome:** Simplified authentication state, reduced setup overhead, and faster iteration.

## Decision 2: Soft Deletion via Archiving
* **Context:** Historical auditability requires that user-deleted/archived reports maintain structural integrity.
* **Decision:** Implemented an `is_archived` boolean flag on `ExpenseReport` instead of performing database deletions.
* **Outcome:** Reports remain safely stored for auditing while being hidden from standard employee/approver active views.
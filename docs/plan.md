# Work Plan & Sequencing

## Phase 1: Setup & Data Modeling (Hours 1–3)
* Extended standard `User` model with custom `ROLE_CHOICES` (`ADMIN`, `APPROVER`, `EMPLOYEE`).
* Designed `ExpenseReport`, `ExpenseLine`, and `ReportHistory` models with appropriate relational fields and statuses.

## Phase 2: Core Workflows & Business Logic (Hours 4–7)
* Implemented state machine transition logic (`DRAFT` -> `SUBMITTED` -> `APPROVED`/`REJECTED` -> `PAID`).
* Added spending threshold checks per line item (`CATEGORY_LIMITS`) and warning flags.
* Integrated `FileField` receipt attachments with media routing.

## Phase 3: Dashboard, Filters & Archiving (Hours 8–10)
* Built dashboard view supporting search, queue, and status filtering.
* Implemented soft-delete `is_archived` toggling and stale approval tracking (`get_active_stale_alerts`).

## Phase 4: Verification & Documentation (Hours 11–12)
* Wrote `seed.py` for automated environment seeding.
* Authored architectural documentation and completed `SUBMISSION.md`.
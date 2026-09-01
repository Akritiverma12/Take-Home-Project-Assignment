# Project Submission Form

# Project Submission Form

## 1. Project Overview & Links
* **GitHub Repository:** https://github.com/Akritiverma12/Take-Home-Project-Assignment
* **Live Application:** [https://AkritiVerma12.pythonanywhere.com]

## 2. Demo Credentials
| Role | Username | Password |
| :--- | :--- | :--- |
| **Admin** | `akriti` | `0204` |
| **Approver** | `approver1` | `password123!` |
| **Employee** | `employee1` | `password123!` |

## 3. Technology Stack
* **Backend:** Python 3.x, Django 5.x
* **Database:** SQLite (Development)
* **Storage / Imaging:** Pillow (Receipt processing)
* **Frontend:** Django MVT Templates, Inline CSS

## 4. Self-Assessment of 10 Core Goals
1. **Multi-Role RBAC:** Implemented (`ADMIN`, `APPROVER`, `EMPLOYEE`).
2. **State Machine Lifecycle:** Draft -> Submitted -> Approved/Rejected -> Paid supported.
3. **Receipt Management:** File upload (`FileField`) and viewing active across all roles.
4. **Policy Enforcement:** Category-based limits automatically flag over-limit entries.
5. **Audit History:** Immutable `ReportHistory` timeline captures status changes and comments.
6. **Soft Delete / Archiving:** Toggleable `is_archived` status with restore permissions.
7. **Dashboard Filtering:** Filter by status, search, and assigned queues.
8. **Stale Approvals:** Alert badge logic for reports pending action > 3 days.
9. **Automated Seeding:** `seed.py` handles complete sample data initialization.
10. **Role Security:** Strict ownership checks on edit, submit, archive, and delete views.
### Bonus / Extra Features Implemented
* **Timeline Commenting System:** Allows users to add discussion notes directly to the immutable audit timeline.
* **Granular Line Item Management:** Full support for editing and deleting individual line items before report finalization.
* **Actionable Rejection Feedback:** Prominently surfaces approver-entered rejection reasons to employees for quick revision.
* **Key Strengths:** Strict backend security rules, comprehensive policy enforcement badges, and seamless handling of receipt uploads.

## 5. Reflection & Closing Questions
* **Time Spent:** ~12 Hours.
* **Key Learning:** Structuring clean Django role-based permission checks within unified template views.
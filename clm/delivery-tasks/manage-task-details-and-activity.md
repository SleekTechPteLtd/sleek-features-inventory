# Manage Task Details and Activity

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Manage Task Details and Activity |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (Service Delivery Operator) |
| **Business Outcome** | Enables operators to enrich individual tasks with files, reference links, and comments while tracking a full audit trail of all actions, ensuring accountability and continuity across client service delivery engagements. |
| **Entry Point / Surface** | Sleek App > Delivery Tasks > click any task row → Task Details panel |
| **Short Description** | A side-panel dialog that exposes the full context of a single task: operators can reassign the task to a team member, attach files via drag-and-drop or file picker, add named reference links, post comments, and scroll through a timestamped activity log covering status changes, assignments, due-date edits, and deletions. |
| **Variants / Markets** | SG, HK (HK-only: PTR due date fetched from Company Tax Documents is shown in the detail panel) |
| **Dependencies / Related Flows** | sleek-service-delivery-api (tasks, task-activities); sleek-billings-api (customer subscriptions — used in the parent TasksList to resolve upgrade/downgrade links); Delivery Overview page (`/delivery/overview`); Company Task Assignments page (`/delivery/task-assignments`) |
| **Service / Repository** | sleek-billings-frontend |
| **DB - Collections** | Unknown (backend service; likely `tasks` and `task_activities` collections in sleek-service-delivery-api) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | 1. Which roles/permissions gate access to the assignee selector and delete actions? 2. Is file storage S3 or another provider (presigned URL returned by `/task-activities/{id}/file-url`)? 3. Are activity logs append-only on the backend, or is a hard delete performed? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Files
- `src/pages/DeliveryTasks/TaskDetailsDialog.jsx` — main dialog component
- `src/pages/DeliveryTasks/TasksList.jsx` — task table; opens `TaskDetailsDialog` on row click (`onClick={() => setOpenTaskDetailsDialog(task)}`)

### API calls (`sleekServiceDeliveryApi`)
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/tasks/{id}` | Load full task detail on dialog open |
| GET | `/task-activities?taskId=...&limit=1000&includeDeleted=true` | Load activity log (links, files, comments, system events) |
| PATCH | `/tasks/{id}` | Update assignee (`assignedUserId`) |
| POST | `/task-activities` | Add a COMMENT or LINK activity |
| POST | `/task-activities/upload` | Upload files (FILE or COMMENT_AND_FILE activity via multipart form-data) |
| PATCH | `/task-activities/{id}` | Edit an existing link |
| DELETE | `/task-activities/{id}` | Soft-delete a link, file, or comment |
| GET | `/task-activities/{id}/file-url` | Retrieve presigned URL to view an attached file |
| GET | `/users?limit=2000` | Populate assignee dropdown |
| GET | `/company-tax-documents/{companyId}` | HK only — fetch PTR due date from tax documents |

### Activity types tracked
`COMMENT`, `FILE`, `LINK`, `COMMENT_AND_FILE`, `ASSIGNMENT`, `DUE_DATE_CHANGE`, `COMPLETED_DATE_CHANGE`, `STATUS_CHANGE`, `COMMENT_DELETED`, `LINK_DELETED`, `FILE_DELETED`

### Task detail fields surfaced in the panel
Company name, company number (label varies by platform: SG/HK/UK/AU), subscription name, subscription external ref ID, delivery status, subscription period, financial year end, PTR due date (HK), task name, task status, assignee, due date, completion date, task description, completion requirements, priority labels, deliverable name.

### Platform detection
`localStorage.getItem("billingConfig")?.platform` determines HK-specific rendering (PTR field) and company number label (`COMPANY_NUMBER_LABEL_BY_PLATFORM`).

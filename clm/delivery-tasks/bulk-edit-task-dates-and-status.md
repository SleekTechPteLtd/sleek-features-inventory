# Bulk Edit Task Dates and Status

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Bulk Edit Task Dates and Status |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (Delivery Operator) |
| **Business Outcome** | Reduces repetitive data entry by letting operators update due dates, completion dates, or task status across multiple tasks in a single action during delivery execution. |
| **Entry Point / Surface** | Sleek App > Delivery Tasks > Task list (any tab) > Bulk action floating bar (appears when ≥1 task is selected) |
| **Short Description** | Operators select one or more tasks via checkboxes and use a persistent floating toolbar to change due dates, completion dates, or task status in bulk. Status changes handle supporting-document and task-reopen guard flows; date pickers enforce subscription-window constraints. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | sleekServiceDeliveryApi (updateTask, bulkChangeTaskStatus, searchTasks); sleekBillingsApi (getCustomerSubscriptionsByCompanyId — used for subscription context in task list); Task status constants (TASK_STATUS, TASK_STATUS_DISPLAY); proof-of-completion flow (isProofOfCompletionRequired flag per task); task reopen flow (requires reason visible to assignee) |
| **Service / Repository** | sleek-billings-frontend; sleek-service-delivery (backend, inferred) |
| **DB - Collections** | Unknown (frontend only; backend owns persistence) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | 1. Which markets/jurisdictions are in scope? No market branching found in code. 2. Does `bulkChangeTaskStatus` backend endpoint enforce any additional authorization checks beyond `updatedByUserId`? 3. When tasks require proof-of-completion and status=DONE, is there a separate upload flow that gets triggered automatically? Code currently skips those tasks and only updates the non-proof ones. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Entry point — TasksList.jsx

- `selectedTaskIds` state tracks checkbox selections; `toggleSelectTask` / `toggleSelectAll` manage the set.
- Floating action bar renders when `selectedTaskIds.length > 0` (lines 705–791); contains three actions:
  - **Change status** → opens `BulkChangeStatusModal`
  - **Edit due date** → opens `BulkEditDueDateModal`
  - **Edit completion date** → opens `BulkEditCompletionDateModal` (only visible when every selected task has status `DONE` or `NOT_REQUIRED`)
- Task data fetched via `sleekServiceDeliveryApi.searchTasks(...)` with pagination, sorting, and a rich filter set (assignedUserIds, companyIds, roleTypes, labels, deliveryStatuses, serviceFYEs, taskStatuses, searchTerm, subscriptionRefNumber).

### BulkEditDueDateModal.jsx

- Modal title: "Edit task due date".
- New due date validated per-task against:
  - **Min**: `max(subscriptionStartDate, task.dueDate)` across all selected tasks — cannot set a date before the latest current due date or subscription start.
  - **Max**: `min(subscriptionEndDate + 1 year)` across all selected tasks.
- Fires individual `sleekServiceDeliveryApi.updateTask(task.id, { dueDate, updatedBy })` calls in parallel via `Promise.allSettled`; reports partial failures via snackbar.
- Shows an info banner if selected tasks have mismatched current due dates.

### BulkEditCompletionDateModal.jsx

- Modal title: "Edit task completion date".
- Validation: completion date cannot be in the future; min date is `max(subscriptionStartDate)` across selected tasks (falls back to 2 years ago).
- Fires individual `sleekServiceDeliveryApi.updateTask(task.id, { completedDate, updatedBy })` calls via `Promise.allSettled`.
- Shows info banner if selected tasks have mismatched completion dates.

### BulkChangeStatusModal.jsx

- Statuses available: `TO_DO`, `DONE`, `NOT_REQUIRED` (from `TASK_STATUS` constants).
- Single API call: `sleekServiceDeliveryApi.bulkChangeTaskStatus({ taskIds, status, updatedByUserId, reason })`.
- Two guard steps:
  1. **Supporting documents confirmation** (step `confirmSupportingDocs`): fires when `status=DONE` and any selected task has `isProofOfCompletionRequired=true`. Proceeds only for tasks that do NOT require proof; proof-required tasks are skipped.
  2. **Reopen confirmation** (step `confirmReopen`): fires when `status=TO_DO` and any selected task is already in `DONE` or `NOT_REQUIRED`. Operator must provide a mandatory free-text reason; reason is sent to backend and noted as visible to assignees.

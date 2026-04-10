# Manage Delivery Task Status

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Manage Delivery Task Status |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (Operator) |
| **Business Outcome** | Operators can progress individual delivery tasks through their lifecycle — marking them complete with optional proof, waiving them as not required, or reopening them with a documented reason — so that delivery records accurately reflect real-world work status. |
| **Entry Point / Surface** | Sleek App > Delivery > Tasks (task list table, per-row status dropdown) |
| **Short Description** | Provides a status dropdown on each delivery task row (To Do → Done / Not Required, or reopen to To Do). Completing a milestone task or one requiring proof of completion opens a dialog to upload supporting documents and optionally bulk-close earlier tasks in the same deliverable. Reopening always requires a written reason visible to the assignee. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Deliverable task ordering (earlier-task check before milestone completion); Bulk Change Status (BulkChangeStatusModal); Task Activity / proof-of-completion uploads; Task details dialog; Due date and completion date editing |
| **Service / Repository** | sleek-billings-frontend, sleek-service-delivery-api |
| **DB - Collections** | tasks, task_activities, deliverables, subscriptions (PostgreSQL via TypeORM) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | 1. Are markets/geographies restricted at the API layer? 2. Is `isProofOfCompletionRequired` set per task template or per individual task? 3. What notification is sent to the task assignee when a task is reopened? 4. `@SleekBackAuth('admin')` — is the status-change endpoint called directly from the operator UI or only via an internal service? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Files

| File | Role |
|---|---|
| `src/pages/DeliveryTasks/TaskStatusAction.jsx` | Inline status selector rendered in each task row; routes to the correct dialog or calls `changeTaskStatus` directly |
| `src/pages/DeliveryTasks/TaskStatusCompletionDialog.jsx` | "Mark as Done" dialog — handles proof-of-completion file upload (drag & drop + click), optional comments, earlier-task bulk-completion checkbox for milestone tasks |
| `src/pages/DeliveryTasks/TaskStatusNotRequiredDialog.jsx` | "Mark as Not Required" dialog — for milestone tasks, offers bulk-closing of earlier tasks in the same deliverable |
| `src/pages/DeliveryTasks/TaskStatusReopenDialog.jsx` | "Reopen task" dialog — requires a free-text reason before submitting; reason is noted as visible to the assignee |
| `src/pages/DeliveryTasks/TasksList.jsx` | Hosts all dialogs; renders the task table with `TaskStatusAction` per row; also mounts `BulkChangeStatusModal` for multi-select status changes |

### API calls (`src/services/service-delivery-api.js`)

| Call | Endpoint | Purpose |
|---|---|---|
| `changeTaskStatus` | `POST /tasks/change-task-status` | Core status transition; payload includes `taskId`, `status`, `updatedByUserId`, optional `shouldMarkEarlierTasks`, `supportingDocumentTaskActivityIds`, `reason` |
| `createTaskActivityWithFiles` | `POST /task-activities/upload` | Uploads proof-of-completion files (multipart); returns activity IDs linked to the task status change |
| `getDeliverableById` | `GET /deliverables/:id` | Fetches sibling tasks to determine whether earlier TO_DO tasks exist before allowing a milestone to be closed without a dialog |

### Business logic highlights

- **Direct vs. dialog transition**: Simple (non-milestone, no proof required) DONE transitions call the API directly. Milestone tasks and tasks with `isProofOfCompletionRequired` open `TaskStatusCompletionDialog`.
- **Milestone bulk-close**: When closing a milestone task, the system checks for earlier TO_DO tasks in the same deliverable (`hasEarlierToDoTasks` utility). If found, the operator is offered a checkbox to mark all earlier tasks Done/Not Required in the same request (`shouldMarkEarlierTasks: true`).
- **Proof of completion**: Files (PDF, JPG, PNG, CSV, max 5 MB each) are uploaded first; returned activity IDs are passed alongside the status change so the backend can link evidence to the task record.
- **Reopening**: Always requires a non-empty reason; the API call sets `status: TO_DO` with the reason in the payload.
- **Status constants**: `TO_DO`, `DONE`, `NOT_REQUIRED` — only these three transitions are exposed in the UI dropdown. `ARCHIVED` exists in the enum but is not surfaced in the UI dropdown.

### Backend — `sleek-service-delivery-api`

#### Auth surface
All task endpoints are guarded by `@SleekBackAuth('admin')` (controller-level), meaning only admin-authenticated callers can perform status changes.

#### Endpoints (backend)

| Method | Path | Handler | Notes |
|---|---|---|---|
| `POST` | `/tasks/change-task-status` | `TasksController.changeTaskStatus` | Single task; accepts optional `shouldMarkEarlierTasks` and `supportingDocumentTaskActivityIds` |
| `POST` | `/tasks/bulk-change-task-status` | `TasksController.bulkChangeTaskStatus` | Up to 100 task IDs; batch update via TypeORM QueryBuilder |

#### Service logic — single task (`TasksService.changeTaskStatus`)

1. Fetches task by ID; throws `TaskNotFoundException` if missing.
2. Sets `task.status` and stamps `completedDate` when new status is `DONE` or `NOT_REQUIRED`.
3. Saves to `tasks` table.
4. If status actually changed, creates a `TaskActivity` record (`STATUS_CHANGE` type) with previous/new status, performer, and optional reason.
5. If `shouldMarkEarlierTasks=true` **and** the task `isMilestone`, calls `updateEarlierTasksStatusAndActivities` to cascade the new status to earlier sibling tasks in the same deliverable.
6. Fires `syncSubscriptionStatusAfterTaskChange` (async, non-blocking): checks if all non-archived tasks in the subscription are `DONE`/`NOT_REQUIRED`; if so, calls `SleekBillingsService.updateServiceDeliveryStatus(externalRefId, 'delivered')`; if a task is reopened, sets status back to `'active'`. Then calls `SubscriptionsService.findAndSyncSubscription`.

#### Service logic — bulk (`TasksService.bulkChangeTaskStatus`)

1. Deduplicates IDs; validates all exist (throws `TaskNotFoundException` on first missing ID).
2. Batch-updates `tasks` via a single `QueryBuilder.update()` call.
3. Enqueues `STATUS_CHANGE` activities via `TaskActivityCreationQueueService` (queue-based, non-blocking).
4. Calls `syncDeliverableStatusesAfterBulkTaskChange` → `TaskDeliverableStatusSyncService.syncDeliverableStatus` per unique deliverable.
5. Triggers `syncSubscriptionStatusAfterTaskChange` for each unique subscription represented in the task set.

#### DB tables touched

| Table | Operation |
|---|---|
| `tasks` | Read + Update (status, completedDate) |
| `task_activities` | Insert (STATUS_CHANGE activity) |
| `deliverables` | Read (subscription relations) |
| `subscriptions` | Read (external_ref_id, companyId for billing sync) |

#### Downstream effects

| System | Call | Trigger |
|---|---|---|
| SleekBillings | `updateServiceDeliveryStatus(externalRefId, 'delivered' \| 'active')` | All tasks done → delivered; task reopened → active |
| Subscriptions service | `findAndSyncSubscription(externalRefId, companyId)` | After billing status update |
| Task activity queue | `TaskActivityCreationQueueService.enqueue(...)` | Bulk path only (single path uses direct insert) |
| Deliverable sync queue | `TaskDeliverableStatusSyncService.syncDeliverableStatus(deliverableId)` | Bulk path only |

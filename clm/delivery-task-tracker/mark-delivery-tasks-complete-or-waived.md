# Mark Delivery Tasks Complete or Waived

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Mark Delivery Tasks Complete or Waived |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Operations staff close out individual or bulk delivery tasks (Done, Not Required, Archived), automatically advancing deliverable and subscription service-delivery statuses when all tasks under an engagement are resolved. |
| **Entry Point / Surface** | Back-office API — `POST /tasks/change-task-status` (single), `POST /tasks/bulk-change-task-status` (up to 100 tasks) |
| **Short Description** | Operations team changes task status to Done, Not Required, or Archived—individually or in bulk. Each change records an audit activity; on completion the service syncs the parent deliverable status and, if all subscription tasks are resolved, updates the subscription's service-delivery status in SleekBillings. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | SleekBillingsService (update service delivery status → `delivered` or `active`); SubscriptionsService (sync subscription after billing update); TaskActivitiesService / TaskActivityCreationQueueService (STATUS_CHANGE audit entries); TaskDeliverableStatusSyncService (sync deliverable on bulk change); Deliverable status workflow |
| **Service / Repository** | sleek-service-delivery-api |
| **DB - Collections** | PostgreSQL — `tasks`, `task_activities`, `deliverables`, `subscriptions` |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | 1. `updatedByUserId` falls back to `task.assignedUserId` rather than the authenticated caller — a TODO in the service notes this should use the auth user ID, so audit trail may be inaccurate. 2. The "mark earlier tasks" cascade (`shouldMarkEarlierTasks`) only fires when `task.isMilestone` is true; it is unclear whether callers know this constraint. 3. Bulk endpoint is capped at 100 task IDs — confirm whether this is sufficient for large client engagements. 4. No market-specific branching visible; confirm whether feature is active across all markets (SG, HK, UK, AU). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Endpoints
- `POST /tasks/change-task-status` — `TasksController.changeTaskStatus()` (`tasks/controllers/tasks.controller.ts:90`)
- `POST /tasks/bulk-change-task-status` — `TasksController.bulkChangeTaskStatus()` (`tasks/controllers/tasks.controller.ts:100`)
- Guard: `@SleekBackAuth('admin')` on the entire controller (line 28) — admin/operations users only.

### DTOs
- `ChangeTaskStatusDto` (`tasks/dto/change-task-status.dto.ts`) — single task; fields: `taskId`, `status` (enum), optional `updatedByUserId`, `updatedBy`, `reason`, `shouldMarkEarlierTasks`, `supportingDocumentTaskActivityIds`.
- `ChangeTaskStatusBulkDto` (`tasks/dto/change-task-status-bulk.dto.ts`) — bulk; fields: `taskIds[]` (max 100), `status`, optional `updatedByUserId`, `updatedBy`, `reason`.

### TaskStatus enum (`tasks/entities/task.entity.ts:11`)
```
TO_DO | NOT_REQUIRED | DONE | ARCHIVED
```
Setting status to `DONE` or `NOT_REQUIRED` stamps `completedDate = now()`.

### Service logic (`tasks/services/tasks.service.ts`)
- `changeTaskStatus` (line 1227): saves new status, creates `STATUS_CHANGE` `TaskActivity` if status changed, optionally cascades to earlier tasks in the same deliverable (milestone tasks only via `updateEarlierTasksStatusAndActivities`), fires async `syncSubscriptionStatusAfterTaskChange`.
- `bulkChangeTaskStatus` (line 1283): bulk-updates up to 100 tasks via query builder, enqueues STATUS_CHANGE activities per task through `taskActivityCreationQueueService`, fires `syncDeliverableStatusesAfterBulkTaskChange` and per-subscription `syncSubscriptionStatusAfterTaskChange`.
- `syncSubscriptionStatusAfterTaskChange` (line 1132): if all non-archived tasks under the subscription are Done/Not Required → calls `SleekBillingsService.updateServiceDeliveryStatus(externalRefId, "delivered")`; if a task is re-opened → sets status back to `"active"`. Then calls `SubscriptionsService.findAndSyncSubscription`.
- `syncDeliverableStatusesAfterBulkTaskChange` (line 1192): resolves unique deliverable IDs from the task batch and calls `TaskDeliverableStatusSyncService.syncDeliverableStatus` for each.

### DB tables touched
- `tasks` — status, completedDate updated
- `task_activities` — STATUS_CHANGE record inserted per changed task
- `deliverables` — status synced via `TaskDeliverableStatusSyncService`
- `subscriptions` — service delivery status updated via SleekBillings + local sync

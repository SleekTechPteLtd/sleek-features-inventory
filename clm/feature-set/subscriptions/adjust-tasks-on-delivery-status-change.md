# Adjust Tasks on Delivery Status Change

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Adjust Tasks on Delivery Status Change |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Keeps the operations team's task lists accurate by automatically marking open service tasks as not required when a client subscription is cancelled, deactivated, or discontinued — and restoring them if the subscription becomes active again. |
| **Entry Point / Surface** | Automated — triggered by MongoDB change stream events on subscription `serviceDeliveryStatus` field; also callable via internal API `POST /subscriptions/by-external-ref/:external_ref_id` |
| **Short Description** | When a subscription's delivery status changes to `inactive`, `discontinued`, or `deactivated`, all open (`TO_DO`) tasks under that subscription are batch-updated to `NOT_REQUIRED`. When the status changes back to `active`, `NOT_REQUIRED` tasks are restored to `TO_DO`, except when transitioning from `delivered` → `active` (which is skipped to avoid reverting intentionally closed tasks). A task activity record is created for each updated task. |
| **Variants / Markets** | SG, HK, AU |
| **Dependencies / Related Flows** | Upstream: SleekBillings (MongoDB) — subscription record and delivery status source; subscription-change BullMQ queue — change stream relay. Downstream: task-activity-creation BullMQ queue — audit trail per task update. Related: Deliverable lifecycle, subscription sync from SleekBillings. |
| **Service / Repository** | sleek-service-delivery-api |
| **DB - Collections** | `subscriptions` (read + sync upsert), `tasks` (batch status update, completedDate), `deliverables` (joined to resolve tasks per subscription), `task_activities` (written via BullMQ queue), `users` (read master user and updatedBy user) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | UK market support unclear — priority label enum covers SG/HK/AU but no UK-specific labels found. Exact statuses that trigger the `active` restore path are not documented beyond code; should confirm whether `toBeStarted` or `toOffboard` transitions ever expect task restoration. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Trigger path

1. **MongoDB change stream** → BullMQ queue `subscription-change` → `SubscriptionChangeProcessor.processChange()`
   - File: `src/subscriptions/queues/subscription-change.processor.ts:228–271`
   - Detects `updatedFields.serviceDeliveryStatus` on `update` operations and calls `SubscriptionsService.updateTasksByDeliveryStatus(documentId, newStatus, updatedBy.id)`
   - Concurrency: 1 — processes one change event at a time to prevent race conditions

2. **HTTP surface**: `POST /subscriptions/by-external-ref/:external_ref_id`
   - File: `src/subscriptions/controllers/subscriptions.controller.ts:69–90`
   - Guard: `@SleekBackAuth('admin')` — internal backend auth only, not user-facing
   - `@ApiOperation`: "Update task statuses based on subscription delivery status — Updates task statuses (TO_DO → NOT_REQUIRED) for a subscription based on its delivery status"

### Core business logic

- `SubscriptionsService.updateTasksByDeliveryStatus()` — `src/subscriptions/services/subscriptions.service.ts:456–508`
  - Fetches the existing subscription (Supabase) and the latest data from MongoDB via `SleekBillingsService.findCustomerSubscription()`
  - Syncs the latest subscription fields to Supabase via upsert on `external_ref_id`
  - Guard: skips task update when previous status was `delivered` and new status is `active` (line 491–498)
  - Delegates to `TasksService.updateTasksBySubscriptionDeliveryStatus()`

- `TasksService.updateTasksBySubscriptionDeliveryStatus()` — `src/tasks/services/tasks.service.ts:525–633`
  - **Statuses → NOT_REQUIRED**: `inactive`, `discontinued`, `deactivated` (TO_DO tasks → NOT_REQUIRED, sets `completedDate = now`)
  - **Status → TO_DO**: `active` (NOT_REQUIRED tasks → TO_DO, clears `completedDate`)
  - All other statuses (`none`, `delivered`, `toBeStarted`, `toOffboard`) are no-ops
  - Batch updates via TypeORM `createQueryBuilder().update()` with `whereInIds(taskIds)`
  - Enqueues a `TaskActivityType.STATUS_CHANGE` activity per task via `taskActivityCreationQueueService` with content: `"Billing Delivery Status changed to <status>"`

### DB tables

- `subscriptions` — entity: `Subscription` (`@Entity('subscriptions')`)
- `tasks` — entity: `Task` (`@Entity('tasks')`)
- `deliverables` — entity: `Deliverable` (`@Entity('deliverables')`)
- `task_activities` — written via BullMQ queue (`task-activity-creation`)
- `users` — read for master user (system actor) and `updatedBy` attribution

### External systems

- **MongoDB / SleekBillings** — `SleekBillingsService.findCustomerSubscription(externalRefId)` fetches authoritative subscription state
- **BullMQ / Redis** — two queues: `subscription-change` (inbound change stream relay), `task-activity-creation` (outbound audit log)

### ServiceDeliveryStatus enum (from `subscription.entity.ts`)

```
none | active | inactive | delivered | discontinued | toBeStarted | toOffboard | deactivated
```

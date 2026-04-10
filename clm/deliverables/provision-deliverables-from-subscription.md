# Provision Deliverables from Subscription

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Provision deliverables from subscription |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Ensures that when a client subscription is activated, all required service deliverables are automatically created from matching templates so the delivery team has a structured work plan ready without manual setup. |
| **Entry Point / Surface** | Internal API only: `POST /deliverables` (SleekBackAuth admin guard); invoked by subscription activation flow |
| **Short Description** | When a subscription is activated, the system matches it against deliverable templates and creates one deliverable (plus its child tasks) per matching template. Creation is queued per-company via BullMQ with a Redis distributed lock to prevent concurrent conflicts across replicas. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Upstream: subscription activation (SleekBillings / billing system), deliverable templates, task templates; Downstream: tasks created per deliverable; Related: Recreate Deliverables (`POST /deliverables/recreate/:externalRefId`), Sync Missing Deliverables (`POST /deliverables/sync-missing/:externalRefId`); External: SleekBillings service (MongoDB subscription lookup), Redis (BullMQ queue + per-company distributed lock) |
| **Service / Repository** | sleek-service-delivery-api |
| **DB - Collections** | PostgreSQL tables: `deliverables`, `deliverable_templates`, `tasks`, `task_activities`, `subscriptions`, `companies`, `team_assignments`, `subscription_fy_groups`; MongoDB (via SleekBillings): customer subscriptions |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | 1. What triggers `POST /deliverables` — a billing webhook, subscription service event, or Zapier/manual process? 2. Are deliverable templates market-specific (SG vs HK vs AU vs UK)? 3. Is the 5-minute Redis lock wait time acceptable under peak load? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Auth surface
- `@SleekBackAuth('admin')` on `DeliverablesController` — internal/admin service-to-service calls only; not user-facing.

### Entry points
- `POST /deliverables` — enqueues a `CREATE_DELIVERABLES` job via `DeliverablesQueueService.createDeliverables()`, waits synchronously for completion (`job.waitUntilFinished`).
- `POST /deliverables/recreate/:externalRefId` — archives all existing deliverables and tasks for a subscription, then recreates from current subscription data. Useful when billing data changes.
- `POST /deliverables/sync-missing/:externalRefId` — creates missing deliverables/tasks from newly added templates without archiving existing records.

### Queue & concurrency model
- Queue name: `deliverables` (BullMQ, `deliverables.queue.ts`)
- Job names: `CREATE_DELIVERABLES`, `RECREATE_DELIVERABLES`
- Processor concurrency: 10 overall (`@Processor(DELIVERABLES_QUEUE, { concurrency: 10 })`)
- Per-company serialization: Redis distributed lock keyed `deliverables:company:<companyId>`, TTL 5 min, wait max 5 min, retry every 500 ms.
- Atomic lock release via Lua compare-and-delete script (prevents releasing a lock owned by a newer job after TTL expiry).

### Input DTO (`create-deliverable.dto.ts`)
- `subscriptionId` (UUID) OR `externalRefId` (string) — at least one required.
- Optional: `name`, `description`, `status` (default `PENDING`), `dueDate`, `assignedUserId`, `createdBy`.

### Entity (`deliverable.entity.ts`, table `deliverables`)
- Statuses: `PENDING`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED`, `ARCHIVED`.
- Relations: belongs to `Subscription` (CASCADE delete), created from `DeliverableTemplate` (CASCADE delete), optionally assigned to `User`, has many `Task` (cascade), optionally linked to `SubscriptionFyGroup` (for monthly-paid annual subscriptions).

### Service dependencies (`deliverables.service.ts`)
- `SleekBillingsService` — resolves subscription by `externalRefId` from MongoDB when no local PG record exists.
- `CompaniesService.findOrCreateCompanyFromSleekBack()` — upserts company in PostgreSQL from MongoDB company data (used to normalise lock key to PG UUID).
- `SubscriptionsService`, `SubscriptionFyGroupsService` — FY group handling for annual billing cycles.
- `AutoMarkRulesService`, `AtoReportingRequirementsService` — post-creation automation (auto-mark rules, ATO reporting tasks).
- Repositories touched: `Deliverable`, `DeliverableTemplate`, `Task`, `TaskActivity`, `Subscription`, `Company`, `TeamAssignment`, `SubscriptionFyGroup`.

### Task generation logic
- Task count per deliverable is derived from `TaskTemplate.frequency` (`WEEKLY`, `BI_WEEKLY`, `MONTHLY`, `QUARTERLY`, `ONE_TIME`) relative to the subscription period (start/end dates via `moment`).
- Due dates computed by offsetting the first instance date by the frequency interval.

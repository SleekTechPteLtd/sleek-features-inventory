# Recreate Deliverables for Updated Subscription

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Recreate deliverables for updated subscription |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (admin-level internal operator) |
| **Business Outcome** | Enables operators to fully reset a client's service delivery records when billing data changes, ensuring all deliverables and tasks reflect the current subscription scope rather than stale billing state. |
| **Entry Point / Surface** | Internal API — `POST /deliverables/recreate/:externalRefId` (SleekBack admin auth only; no client-facing UI identified) |
| **Short Description** | Archives all active deliverables and tasks for a subscription, syncs the latest billing data from MongoDB to PostgreSQL, then regenerates deliverables and tasks from matching deliverable templates. The archive and creation steps are wrapped in a single database transaction to ensure atomicity. |
| **Variants / Markets** | Unknown (ATO reporting references suggest AU; broader market applicability not determinable from code alone) |
| **Dependencies / Related Flows** | SleekBillings (MongoDB) — authoritative subscription data source; SubscriptionsService.syncSubscription — pushes billing state to PostgreSQL; DeliverableTemplates — matched by subscription code; DeliverablesQueueService — Redis per-company job lock; AutoMarkRulesService — auto-completion rules applied to new tasks; AtoReportingRequirementsService — ATO task enrichment; Related features: Manage client deliverables, Sync missing deliverables and tasks |
| **Service / Repository** | sleek-service-delivery-api |
| **DB - Collections** | deliverables, tasks, task_activities, subscriptions, companies, deliverable_templates, team_assignments, subscription_fy_groups (all PostgreSQL / Supabase) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | What UI surface (if any) exposes this action to operators? Which markets does this apply to? Is the `createdBy` field used as an audit trail for accountability? How does FY-grouped subscription recreate differ from the standard path (delegates to `recreateDeliverablesForFyGroupedSubscription`)? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Entry point
- `src/deliverables/controllers/deliverables.controller.ts:97–118`
  - `POST /deliverables/recreate/:externalRefId`
  - Guard: `@SleekBackAuth('admin')` — internal admin only
  - Accepts optional `{ createdBy?: string }` body for attribution
  - Delegates to `DeliverablesService.recreateDeliverables(externalRefId, createdBy)`

### Core logic
- `src/deliverables/services/deliverables.service.ts:1681–1889` — `recreateDeliverables()`

**Step 1 — fetch latest billing state (outside transaction)**
- Calls `SleekBillingsService.findCustomerSubscription(externalRefId)` to retrieve the canonical subscription record from MongoDB
- Validates `subscriptionStartDate` / `subscriptionEndDate` are present
- Guards against `FINANCIAL_YEAR` grouping without a `financialYearEnd` (returns early with `[]`)

**Step 2 — sync billing → PostgreSQL (outside transaction)**
- `findOrCreateCompany(mongoCustomerSubscription.companyId)` — upserts company in PostgreSQL
- `SubscriptionsService.syncSubscription(externalRefId, company.id, mongoCustomerSubscription)` — writes latest billing state to `subscriptions` table

**Step 3 — FY-grouped branch**
- If `subscriptionGroupingCriteria === FINANCIAL_YEAR`, delegates to `recreateDeliverablesForFyGroupedSubscription(company, subscription, createdBy)` (separate path for monthly-paid annual subscriptions)

**Step 4 — transactional archive + recreate (standard path)**
- Opens a `DataSource` query runner and starts a PostgreSQL transaction
- Finds all active deliverables (`recordStatus = ACTIVE`) for `subscription.id` with their tasks
- Batch-updates all task IDs → `status: ARCHIVED, recordStatus: INACTIVE`
- Batch-updates all deliverable IDs → `status: ARCHIVED, recordStatus: INACTIVE`
- Queries `deliverable_templates` where `subscription.code = ANY(codes)` and `recordStatus = ACTIVE`, joining active `task_templates`
- For each matching template: creates a new `Deliverable`, then calls `createTasksFromTemplate()` to generate child tasks
- Commits transaction; rolls back on any error

### Related endpoint (for comparison)
- `POST /deliverables/sync-missing/:externalRefId` (`syncMissingDeliverablesAndTasks`) — additive-only variant: creates missing deliverables and tasks from newly added templates without archiving existing records

### DB tables touched
| Table | Operation |
|---|---|
| `subscriptions` | READ (find by externalRefId), WRITE (upsert via syncSubscription) |
| `companies` | READ / WRITE (upsert via findOrCreateCompany) |
| `deliverables` | READ (find active), WRITE (batch archive + insert new) |
| `tasks` | READ (via deliverable relations), WRITE (batch archive + insert new) |
| `task_activities` | WRITE (activity records for new tasks) |
| `deliverable_templates` | READ (match by subscription code) |
| `team_assignments` | READ (used in createTasksFromTemplate) |
| `subscription_fy_groups` | READ/WRITE (FY-grouped path only) |

### External service calls
- **SleekBillings (MongoDB)**: `findCustomerSubscription(externalRefId)` — reads canonical billing record
- **Redis**: per-company distributed lock via `DeliverablesQueueService` (prevents concurrent jobs for the same company across replicas)

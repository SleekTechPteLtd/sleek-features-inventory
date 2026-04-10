# Sync Missing Deliverables to Subscription

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Sync Missing Deliverables to Subscription |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (Admin) |
| **Business Outcome** | Keeps a subscription's deliverable set current when new templates are added, so operators can roll out newly defined work items to existing clients without losing progress already recorded against existing deliverables or tasks. |
| **Entry Point / Surface** | Internal Admin API — `POST /deliverables/sync-missing/:externalRefId` |
| **Short Description** | Compares active deliverable and task templates against an existing subscription's records and creates only the items that are missing. Existing deliverables and tasks are left untouched. Supports both standard subscriptions and financial-year-grouped (monthly-paid annual) subscriptions. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | SleekBillings (MongoDB customer subscription lookup); Subscription FY Groups service (for FINANCIAL_YEAR grouping criterion); Deliverable Templates + Task Templates (source of truth for what should exist); `Recreate Deliverables` flow (destructive alternative that archives first) |
| **Service / Repository** | sleek-service-delivery-api |
| **DB - Collections** | `deliverables`, `tasks`, `deliverable_templates`, `task_templates`, `subscriptions`, `companies`, `subscription_fy_groups` |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Which markets use this operation? No market-specific guard or filter is visible in the code. Is this triggered manually by ops or via an automation/webhook when templates change? The `createdBy` body param suggests it can be attributed to a specific operator or set to `"system"`, but the caller context is unclear. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Controller — `deliverables/controllers/deliverables.controller.ts`
- `POST /deliverables/sync-missing/:externalRefId` (line 120–141)
- `@SleekBackAuth('admin')` guard on the entire controller — internal admin-only surface
- `@ApiOperation` summary: *"Sync missing deliverables and tasks for a subscription"*
- `@ApiOperation` description: *"Creates missing deliverables from newly added deliverable templates and missing tasks from newly added task templates without archiving existing records."*
- Delegates to `DeliverablesService.syncMissingDeliverablesAndTasks(externalRefId, body?.createdBy)`

### Service — `deliverables/services/deliverables.service.ts`
**`syncMissingDeliverablesAndTasks` (line 1269)**
1. Fetches the MongoDB customer subscription via `SleekBillingsService.findCustomerSubscription(externalRefId)` — validates start/end date presence.
2. Guards against `FINANCIAL_YEAR` grouping without a `financialYearEnd` value (returns empty array with a warning log).
3. Syncs the local `subscriptions` record via `SubscriptionsService.syncSubscription`.
4. Branches on `subscriptionGroupingCriteria`:
   - `FINANCIAL_YEAR` → `syncMissingForFyGroupedSubscription`
   - Otherwise → `syncMissingForSubscription`

**`syncMissingForSubscription` (line 1388)**
- Loads active `deliverable_templates` matching the subscription's code.
- Loads existing active `deliverables` (with their `tasks`) for the subscription.
- For each template:
  - If no matching deliverable exists → creates a new `deliverable` row and all active task templates as `tasks`.
  - If a deliverable exists → computes the set of task templates not yet represented in the deliverable's active tasks and creates only those missing `tasks`.
- Returns the list of created or augmented deliverables.

**`syncMissingForFyGroupedSubscription` (line 1487)**
- Resolves or creates the FY group via `SubscriptionFyGroupsService.findOrCreateFyGroup`.
- Updates `primarySubscriptionId` based on earliest start date.
- Scopes existing deliverable lookup by `fyGroupId` instead of `subscriptionId`.
- Otherwise follows the same create-missing-only logic as the standard path, stamping new deliverables with `fyGroupId`.

### Key DB tables
| Table | Role |
|---|---|
| `deliverables` | Primary output — new rows created for missing deliverable templates |
| `tasks` | New task rows created for missing task templates within existing/new deliverables |
| `deliverable_templates` | Source of truth for which deliverables should exist for a subscription code |
| `task_templates` | Source of truth for which tasks should exist within each deliverable |
| `subscriptions` | Looked up/synced to resolve subscription metadata (code, FYE, billing cycle) |
| `companies` | Resolved or created via `findOrCreateCompany` |
| `subscription_fy_groups` | Used when `subscriptionGroupingCriteria = FINANCIAL_YEAR`; scopes deliverable ownership to the FY group rather than a single subscription |

### External service calls
- `SleekBillingsService.findCustomerSubscription` — reads subscription master data from MongoDB (SleekBillings service)

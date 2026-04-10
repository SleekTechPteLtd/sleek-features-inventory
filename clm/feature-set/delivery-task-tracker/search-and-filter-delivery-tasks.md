# Search and Filter Delivery Tasks

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Search and Filter Delivery Tasks |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Enables the ops team to pinpoint any task across all client engagements using up to 12 combinable filters so they can prioritise overdue work, monitor assignee load, and track delivery health without manually scanning every client record. |
| **Entry Point / Surface** | Sleek Admin App > Delivery > Task Tracker (search / filter panel) |
| **Short Description** | `POST /tasks/search` returns a paginated, sorted list of tasks matched by status, due-date urgency bucket (OVERDUE / DUE_SOON / NOT_DUE / COMPLETED), assignee, role type, unassigned flag, milestone flag, task template, subscription priority label, service-delivery status, financial year end, company, and subscription reference number. Milestone and template-ID filters combine with OR logic. Results sort by due date, completion date, company name, subscription period, or financial year end. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Subscriptions (ref-number → fyGroupId resolution), Deliverables (archived deliverables excluded), Companies, Task Templates (milestone/isMilestone flag), Users, Task Activities (audit trail); feeds delivery overview and analytics dashboards |
| **Service / Repository** | sleek-service-delivery-api |
| **DB - Collections** | tasks, deliverables, subscriptions, companies, task_templates, users, task_activities (PostgreSQL) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | 1. Which markets/regions use this feature (SG, HK, UK, AU)? 2. Is there a dedicated frontend view for this search endpoint, or does the same Task Tracker page that calls GET `/tasks` also use `POST /tasks/search`? 3. The `filterBySubscriptionRefNumber` path branches on `fyGroupId` presence — is this FY-group logic stable or still being refined? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Entry point
- `tasks/controllers/tasks.controller.ts:49` — `POST /tasks/search`, guarded by `@SleekBackAuth('admin')`; accepts `SearchTasksDto`, returns `PaginatedResponseDto<Task>`

### Filter dimensions (`tasks/dto/search-tasks.dto.ts`)
| Filter field | Type | Behaviour |
|---|---|---|
| `searchTerm` | string | Free-text ILIKE on `task.name` OR `company.name`; comma syntax to search company,task independently |
| `taskDueStatus` | `TaskDueStatus` enum | OVERDUE (past due + TO_DO), DUE_SOON (≤14 days + TO_DO), NOT_DUE (>14 days or null + TO_DO), COMPLETED (DONE or NOT_REQUIRED) |
| `taskStatuses` | `TaskStatus[]` | Explicit status filter: TO_DO, NOT_REQUIRED, DONE, ARCHIVED |
| `assignedUserIds` | `string[]` | Match tasks assigned to any of these users |
| `assignedRoleTypes` | `RoleType[]` | Match tasks whose template `roleAssigned` is in this list |
| `filterByUnassigned` | boolean | Return only tasks with no assignee |
| `filterByAssigned` | boolean | Return only tasks with an assignee |
| `filterMilestoneTasks` | boolean | Return only milestone tasks (`template.isMilestone = true`); OR'd with `taskTemplateIds` when both set |
| `taskTemplateIds` | `string[]` | Match tasks created from these template IDs; OR'd with `filterMilestoneTasks` when both set |
| `subscriptionLabels` | `SubscriptionPriorityLabel[]` | Filter by subscription priority label (array overlap) |
| `subscriptionDeliveryStatuses` | `ServiceDeliveryStatus[]` | Filter by subscription service-delivery status |
| `serviceFyeYears` | `string[]` | Filter by financial year end year (`EXTRACT(YEAR FROM subscription.financialYearEnd)`) |
| `companyIds` | `string[]` | Restrict to specific company IDs |
| `filterBySubscriptionRefNumber` | string | Resolves to fyGroupId (FY-grouped subscriptions) or subscriptionId; filters `deliverable.fyGroupId` or `deliverable.subscriptionId` accordingly |
| `sortBy` | `TaskSearchSortBy` enum | companyName, dueDate (default), completedDate, subscriptionPeriod, financialYearEnd |

### Task entity (`tasks/entities/task.entity.ts`)
- Table: `tasks`
- Key columns: `name`, `status`, `dueDate`, `completedDate`, `assignedUserId`, `companyId`, `deliverableId`, `templateId`, `taskStartDate`, `taskEndDate`
- Indexes on: `[templateId, status]`, `[templateId, status, deliverableId]`, `[deliverableId]`, `[companyId]`, `[assignedUserId]`, `[status, dueDate]`, `[status, completedDate]`
- Computed getters: `isMilestone`, `isProofOfCompletionRequired` (delegated to `template`)

### Service logic (`tasks/services/tasks.service.ts:635`)
- TypeORM QueryBuilder with left joins: `task → deliverable → subscription → company`, `task → template`, `task → assignedUser`
- Archived deliverables excluded (`deliverable.status != ARCHIVED`)
- `filterBySubscriptionRefNumber` triggers a pre-query to `subscriptionRepository` to resolve `fyGroupId` vs `subscriptionId` for FY-grouped clients
- Pagination: skip/take; default sort `task.dueDate ASC NULLS LAST`
- Downstream services injected: `SleekBillingsService`, `SubscriptionsService`, `TaskActivitiesService`, `TaskActivityCreationQueueService`, `TaskDeliverableStatusSyncService`

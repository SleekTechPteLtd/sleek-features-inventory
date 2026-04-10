# Staff Task Workload Distribution

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Staff Task Workload Distribution |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Core Ops User (Operations Manager / Delivery Manager) |
| **Business Outcome** | Enables Core Ops managers to identify workload imbalances and at-risk staff by surfacing overdue, due-soon, and not-due task counts per team member before delivery issues escalate. |
| **Entry Point / Surface** | Sleek App > Delivery > Analytics > Staff Task Distribution (`delivery/analytics/staff-task-distribution`) |
| **Short Description** | Displays a paginated table of per-staff task counts (overdue, due soon, not due, total) with four aggregate stat cards at the top. Filters by FYE, milestone, delivery status (multi-select), and company status; a configurable due-soon window (default 7 days, max 365) governs the due-soon bucket. Results can be exported to CSV. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Related Delivery screens: Task Tracker (`delivery/task-tracker`), Team Assignments (`delivery/task-assignments`), Delivery Overview, Staff Assignment Overview (`delivery/analytics/staff-assignment-overview`), SDS Usage Dashboard (`delivery/analytics/sds-usage-dashboard`) |
| **Service / Repository** | sleek-billings-frontend, sleek-service-delivery-api |
| **DB - Collections** | tasks, users, companies, task_templates, subscriptions, deliverables (PostgreSQL via TypeORM) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | 1. Company name filter is hardcoded-hidden (`SHOW_COMPANY_NAME_FILTER = false`) with comment "Temporary: hide company name filter" — when will it be re-enabled? 2. Which markets/regions use this view? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Frontend component
`sleek-billings-frontend/src/pages/Delivery/Analytics/StaffTaskDistribution.jsx`

- **Route**: `delivery/analytics/staff-task-distribution`
- **Subtitle**: "Core Ops view" — confirms intended audience
- **Stat cards** (aggregate, filtered): Overdue tasks (red), Due soon (amber), Not due (slate), Total tasks
- **Table columns**: Staff name (avatar + initials), Email, Overdue tasks, Due soon tasks, Not due tasks, Total tasks — paginated at 30 rows/page
- **Filters available**:
  - FYE (single-select, options from API)
  - Milestone name (single-select, options from API)
  - Staff name (single-select, options from API)
  - Company status: Active / Inactive
  - Delivery status (multi-select): Active, To Be Started, To Offboard, Delivered, Discontinued, Inactive, Deactivated
  - Due soon window: configurable integer 1–365 days (default 7)
  - Company name filter present in code but hidden (`SHOW_COMPANY_NAME_FILTER = false`, comment says "Temporary")
- **Export**: `handleExport` triggers a CSV download named `task-distribution-<date>.csv`
- **Stale-request guard**: `staffDistributionFetchGenRef` ref prevents out-of-order response race conditions

### API calls (all against `SERVICE_DELIVERY_API_URL`)
| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/analytics/task-distribution/summary` | Aggregate overdue/due-soon/not-due/total counts for stat cards |
| `GET` | `/analytics/task-distribution/staff` | Paginated per-staff task count rows (supports `page`, `limit`, and all filter params) |
| `GET` | `/analytics/task-distribution/filter-options` | Populates FYE, milestone, staff, and company filter dropdowns |
| `POST` | `/analytics/task-distribution/export` | Returns a CSV blob of the current filtered view |

### Backend controller
`sleek-service-delivery-api/src/analytics/controllers/task-distribution-analytics.controller.ts`

- **Route prefix**: `analytics/task-distribution`
- **Auth**: `@SleekBackAuth('admin')` — admin-only; entire controller is guarded
- **Tag**: `analytics/task-distribution`
- All four endpoints map directly to `TaskDistributionAnalyticsService` methods

### Backend service
`sleek-service-delivery-api/src/analytics/services/task-distribution-analytics.service.ts`

- **Caching**: All three read endpoints use `CACHE_MANAGER` with `buildAnalyticsCacheKey` + `ANALYTICS_CACHE_TTL_MS`; cache is keyed on serialised filter params
- **Due-soon logic**: `today = moment().startOf('day')`, `dueSoonDate = today + dueSoonDays`; only `TO_DO` tasks are bucketed into overdue/dueSoon/notDue; `DONE`/`NOT_REQUIRED`/`ARCHIVED` appear in `byStatus` only
- **Summary** (`getSummary`): Fetches all matching tasks, computes overdue/dueSoon/notDue/byStatus/avgTasksPerStaff/unassigned counts in-process; also returns top-10 templates via a grouped DB query
- **By-staff** (`getByStaff`): Joins `users → tasks`, applies all filters, paginates by total task count DESC; then runs secondary queries for per-staff template breakdown and company counts
- **Filter options** (`getFilterOptions`): Queries `users`, `companies`, `task_templates`, `subscriptions` to populate dropdown lists; FYE options extracted from `EXTRACT(YEAR FROM subscriptions.financialYearEnd)`
- **CSV export** (`exportCsv`): Streams a `StreamableFile`; by-staff export paginates internally using `ANALYTICS_CSV_EXPORT_PAGE_SIZE`

### DB tables accessed (PostgreSQL)
| Table | Entity | Purpose |
|---|---|---|
| `tasks` | `Task` | Primary data: assignedUserId, status, dueDate, companyId, templateId |
| `users` | `User` | Staff names, emails, recordStatus |
| `companies` | `Company` | Company name, recordStatus (for company status filter) |
| `task_templates` | `TaskTemplate` | Template/milestone name, milestone filter options |
| `subscriptions` | `Subscription` | serviceDeliveryStatus, financialYearEnd (FYE filter) |
| `deliverables` | `Deliverable` | Join path: task → deliverable → subscription (for delivery status + FYE filters) |

### Query DTOs
`sleek-service-delivery-api/src/analytics/dto/task-distribution-query.dto.ts`

Filter params: `staffIds` (CSV UUIDs), `companyIds`, `templateIds`, `statuses`, `staffId` (single, UI alias), `companyId` (single, UI alias), `dueSoonDays` (1–365, default 7), `deliveryStatus` (enum array), `fye` (string year), `milestone` (template name), `companyStatus` (`active`|`inactive`). By-staff query adds `page`, `limit`, `search`.

# Task Distribution Analytics

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Task Distribution Analytics |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin (Core Ops / Delivery Manager) |
| **Business Outcome** | Enables Core Ops managers to identify workload imbalances by surfacing per-staff task counts across overdue, due-soon, and not-due buckets — with filtering by FYE, milestone, delivery status, and company — so they can act before delivery issues escalate. |
| **Entry Point / Surface** | Sleek Admin App > Delivery > Analytics > Staff Task Distribution (API: `GET/POST /analytics/task-distribution/*`) |
| **Short Description** | Backend API that powers the staff task distribution analytics view. Provides summary metrics (overdue / due-soon / not-due / total / top templates), a paginated per-staff breakdown with template and company drill-downs, filter-option hydration, and CSV export for both summary and per-staff views. All read responses are cached via `CACHE_MANAGER`. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Frontend consumer: `sleek-billings-frontend` (StaffTaskDistribution.jsx); inventory peers: `clm/delivery-staff-task-distribution/staff-task-workload-distribution.md`, `clm/delivery-staff-task-distribution/export-staff-task-distribution-report.md`; upstream entities: Tasks, Users, Companies, TaskTemplates, Subscriptions, Deliverables |
| **Service / Repository** | sleek-service-delivery-api |
| **DB - Collections** | PostgreSQL tables: `tasks`, `users`, `companies`, `task_templates`, `subscriptions`, `deliverables` (joined for delivery-status and FYE filtering) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | 1. What is `ANALYTICS_CACHE_TTL_MS`? Affects result staleness and whether live dashboards are feasible. 2. No market-specific logic found — is this feature available in all markets (SG/HK/UK/AU)? 3. `SHOW_COMPANY_NAME_FILTER = false` on the frontend hides the company-name filter from UI even though the API supports `companyId` — is this a temporary toggle or a permanent removal? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Controller
`src/analytics/controllers/task-distribution-analytics.controller.ts`

- **Guard**: `@SleekBackAuth('admin')` applied at class level — all endpoints require an authenticated admin.
- **Tag**: `analytics/task-distribution`

| Method | Route | Handler | Purpose |
|---|---|---|---|
| `GET` | `/analytics/task-distribution/summary` | `getSummary` | Aggregate stats: overdue, due soon, not due, completed, unassigned, avg tasks/staff, top-10 templates |
| `GET` | `/analytics/task-distribution/staff` | `getByStaff` | Paginated per-staff rows with overdue / due-soon / not-due / completed counts, template breakdown, company count |
| `GET` | `/analytics/task-distribution/filter-options` | `getFilterOptions` | Dropdown options: staff, companies, templates, task statuses, FYE years, milestone names |
| `POST` | `/analytics/task-distribution/export` | `exportCsv` | Returns a `StreamableFile` (text/csv); `exportType` = `"summary"` or `"by-staff"` |

### Service
`src/analytics/services/task-distribution-analytics.service.ts`

**Repositories injected**: `Task`, `User`, `Company`, `TaskTemplate`, `Subscription`

**Caching**: `CACHE_MANAGER` (Redis-backed); key built via `buildAnalyticsCacheKey`; TTL from `ANALYTICS_CACHE_TTL_MS`. All three read methods (`getSummary`, `getByStaff`, `getFilterOptions`) check cache before querying.

**Filter logic** (`applyTaskDistributionTaskFiltersOnTaskAlias`):
- `deliveryStatus` and `fye` → joins `task.deliverable → deliverable.subscription`; filters on `tdSubscription.serviceDeliveryStatus` and `EXTRACT(YEAR FROM tdSubscription.financialYearEnd)`
- `milestone` → subquery on `task_templates.name`
- `companyStatus` → joins `task.company`; filters on `tdCompany.recordStatus`

**Due-soon window**: configurable `dueSoonDays` param (default 7 days); computed as `today + dueSoonDays`.

**Summary metrics computed in-memory** after fetching filtered task rows: overdue, due-soon, not-due, completed, unassigned, staffWithTasks set, avgTasksPerStaff.

**Top templates** (`getTopTemplates`): aggregated via SQL `SUM(CASE ...)` for overdue/due-soon; returns top 10 by count.

**Per-staff breakdown** (`getByStaffUncached`): staff ordered by total task count DESC, then name ASC; calls three sub-queries:
- `getTaskDistributionsByStaff` — overdue/due-soon/not-due/completed/byStatus per staff
- `getTemplateBreakdownsByStaff` — top templates per staff
- `getCompanyCountsByStaff` — distinct company count per staff

**CSV export**:
- `summary` type → inline CSV with metric rows + by-status block + top-templates block; filename `task-distribution-summary.csv`
- `by-staff` type → paginated loop using `ANALYTICS_CSV_EXPORT_PAGE_SIZE`; columns: UserID, First/Last Name, Email, Total/Overdue/DueSoon/NotDue/Completed, Companies, TO_DO/NOT_REQUIRED/DONE/ARCHIVED; filename `task-distribution-by-staff.csv`

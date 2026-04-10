# Export SDS Usage Reports

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM – Service Delivery |
| **Feature Name** | Export SDS usage reports |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin (internal Sleek ops admin, `@SleekBackAuth('admin')`) |
| **Business Outcome** | Enables operations admins to download SDS platform usage data as CSV for offline analysis, reporting, and staff performance review. |
| **Entry Point / Surface** | Internal admin tool > SDS Usage Analytics page (`delivery-sds-usage` module) |
| **Short Description** | Admins export SDS usage data as a CSV file in two modes: a summary report (platform-wide KPIs and 4-week engagement trends) or a per-staff engagement report (task assignments, completions, companies assigned, last activity date). Supports optional date-range filtering and single-user scoping. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Monitor SDS staff engagement and adoption (same module); Task management; Team assignment; User directory |
| **Service / Repository** | sleek-service-delivery-api |
| **DB - Collections** | PostgreSQL tables: `task`, `task_activity`, `user`, `team_assignment` |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Which front-end component triggers the export POST? Is there a download button in the delivery-sds-usage UI? Is this used operationally on a scheduled cadence or ad-hoc? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Controller
`src/analytics/controllers/sds-usage-analytics.controller.ts`

- `@Controller('analytics/sds-usage')` with `@SleekBackAuth('admin')` — all endpoints are internal admin-only.
- `POST /analytics/sds-usage/export` → `exportCsv(body: SdsUsageExportDto)` — returns a `StreamableFile` with `Content-Type: text/csv; charset=utf-8`.
- Supporting read endpoints (also admin-gated):
  - `GET /analytics/sds-usage/summary` — aggregated KPI metrics with weekly trends.
  - `GET /analytics/sds-usage/staff-engagement` — paginated per-staff engagement records.

### DTO
`src/analytics/dto/sds-usage-query.dto.ts` — `SdsUsageExportDto`:
- `exportType`: `'summary'` | `'staff-engagement'` (default: `'staff-engagement'`)
- `startDate` / `endDate`: optional date-range filter (YYYY-MM-DD)
- `userId`: optional single-user filter (staff engagement mode only)

### Service
`src/analytics/services/sds-usage-analytics.service.ts`

**Summary CSV** (`exportType: 'summary'`):
- Calls `getSummary()` (cached via `CACHE_MANAGER`).
- Output columns: `Metric, Value` — rows for total active staff, total tasks, total engagements, tasks completed/overdue/due-soon, avg engagements per staff, engagement trend %, plus a weekly breakdown section (week start, count, active users).
- Filename: `sds-usage-summary.csv`.

**Staff engagement CSV** (`exportType: 'staff-engagement'`):
- Paginates through `getStaffEngagement()` using `ANALYTICS_CSV_EXPORT_PAGE_SIZE` until exhausted.
- Output columns: `User ID, First Name, Last Name, Email, Total Engagements, Tasks Assigned, Tasks Completed, Companies Assigned, Last Activity Date`.
- Filename: `sds-usage-staff-engagement.csv`.

### Repositories / tables touched
| Repository | Table | Purpose |
|---|---|---|
| `TaskRepository` | `task` | Task totals, status counts, due dates |
| `TaskActivityRepository` | `task_activity` | Engagement counts, activity types, weekly breakdown |
| `UserRepository` | `user` | Staff list, names, emails |
| `TeamAssignmentRepository` | `team_assignment` | Companies-per-staff count |

### Caching
- `getSummary` and `getStaffEngagement` results are cached via `CACHE_MANAGER` using `buildAnalyticsCacheKey` with TTL `ANALYTICS_CACHE_TTL_MS`. Export bypasses display cache but internally calls the cached read methods.

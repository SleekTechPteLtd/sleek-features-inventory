# Export staff task distribution report

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Export staff task distribution report |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Core Ops user (internal admin) |
| **Business Outcome** | Enables Core Ops teams to download a filtered snapshot of per-staff task workload as a CSV for offline capacity planning, overdue risk analysis, and reporting. |
| **Entry Point / Surface** | Sleek Admin App > Delivery > Analytics > Staff Task Distribution > "Export report" button |
| **Short Description** | User applies filters (FYE, milestone, staff, company status, delivery status, due-soon window) on the Staff Task Distribution page and clicks "Export report". The frontend posts the active filter state to `POST /analytics/task-distribution/export`; the backend streams back a UTF-8 CSV blob (either an aggregate summary or a per-staff breakdown) which the browser saves as `task-distribution-{date}.csv`. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Staff Task Distribution analytics view (sibling GET endpoints: summary, by-staff, filter-options on the same controller); subscription FYE and service delivery status data; task template milestone data |
| **Service / Repository** | sleek-billings-frontend (frontend), sleek-service-delivery-api (backend) |
| **DB - Collections** | tasks, users, companies, task_templates, subscriptions (PostgreSQL via TypeORM) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | (1) `SHOW_COMPANY_NAME_FILTER` is hard-coded `false` in the frontend — company name filter is hidden from the UI; unclear if this is a temporary toggle or permanent removal, which affects what is exportable. (2) No market-specific logic found — market availability unknown. (3) Response results are cached via CACHE_MANAGER; TTL is `ANALYTICS_CACHE_TTL_MS` — cache invalidation strategy not reviewed. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Files — frontend
- `src/pages/Delivery/Analytics/StaffTaskDistribution.jsx` — React page component; contains the export handler (`handleExport`) and all filter state.
- `src/services/service-delivery-api.js` — Axios-based API client; contains `exportTaskDistribution`, `getTaskDistributionSummary`, `getTaskDistributionByStaff`, `getTaskDistributionFilterOptions`.

### Files — backend (`sleek-service-delivery-api`)
- `src/analytics/controllers/task-distribution-analytics.controller.ts` — NestJS controller; route prefix `analytics/task-distribution`; guarded by `@SleekBackAuth('admin')` (admin-only).
- `src/analytics/services/task-distribution-analytics.service.ts` — core service; implements `exportCsv`, `exportSummaryCsv`, `exportByStaffCsv`, plus `getSummary`, `getByStaff`, `getFilterOptions` with cache-aside pattern.
- `src/analytics/dto/task-distribution-query.dto.ts` — filter DTOs; `TaskDistributionExportDto` extends `TaskDistributionTaskFiltersDto`.
- `src/analytics/dto/task-distribution-response.dto.ts` — response shape DTOs.
- `src/analytics/analytics-csv-export.constant.ts` — `ANALYTICS_CSV_EXPORT_PAGE_SIZE = 5000` (internal page size for streaming all rows into one CSV).

### Export API
```
POST /analytics/task-distribution/export
Content-Type: application/json  →  Response: text/csv; charset=utf-8
Guard: @SleekBackAuth('admin')
```

**exportType = `by-staff`** (default):
- Paginates through all staff (5 000 rows/page) and emits one CSV row per staff member.
- CSV columns: `User ID, First Name, Last Name, Email, Total Tasks, Overdue, Due Soon, Not Due, Completed, Companies, TO_DO, NOT_REQUIRED, DONE, ARCHIVED`
- File name: `task-distribution-by-staff.csv`

**exportType = `summary`**:
- Emits aggregate metrics (total tasks, overdue, due soon, not due, completed, unassigned, avg per staff, by-status breakdown, top 10 templates).
- File name: `task-distribution-summary.csv`

### Filter parameters accepted by the export endpoint
| Param | Description |
|---|---|
| `staffIds` / `staffId` | Filter by assigned staff (comma-separated UUIDs or single UUID) |
| `companyIds` / `companyId` | Filter by company (comma-separated UUIDs or single UUID; UI currently hides this) |
| `templateIds` | Filter by task template IDs |
| `statuses` | Filter by task status (TO_DO, DONE, NOT_REQUIRED, ARCHIVED) |
| `deliveryStatus` | Filter by subscription service delivery status (ServiceDeliveryStatus enum) |
| `fye` | Financial year end year (e.g. `2024`) |
| `milestone` | Task template name (milestone) filter |
| `companyStatus` | `active` or `inactive` |
| `dueSoonDays` | Integer 1–365; default 7 |
| `exportType` | `summary` or `by-staff`; default `by-staff` |

### Database tables touched
| Table | Purpose |
|---|---|
| `tasks` | Primary data source — status, dueDate, assignedUserId, companyId, templateId |
| `users` | Staff identity — firstName, lastName, email |
| `companies` | Company filter and status joins |
| `task_templates` | Template name / milestone joins and top-template aggregation |
| `subscriptions` | FYE and serviceDeliveryStatus joins (via `deliverable → subscription`) |

### Frontend export flow
```
handleExport() [StaffTaskDistribution.jsx]
  → buildFilterParams()            // collects active filter state
  → sleekServiceDeliveryApi.exportTaskDistribution(params)
      POST /analytics/task-distribution/export   // responseType: "blob"
  → Blob([response], { type: "text/csv" })
  → <a download="task-distribution-{YYYY-MM-DD}.csv"> triggered programmatically
```

### API client setup (`service-delivery-api.js`)
- Base URL: `VITE_SERVICE_DELIVERY_API_URL` (env var)
- Auth: Bearer JWT (OAuth) or raw token from `localStorage["auth"]`
- App-Origin header: `"admin-sso"` (or `"admin"` when `alternate_login` flag is set)

### Related sibling API calls (same controller, same guard)
- `GET /analytics/task-distribution/summary` — aggregate stat cards (overdue, due soon, not due, total)
- `GET /analytics/task-distribution/staff` — paginated per-staff rows (page size 30)
- `GET /analytics/task-distribution/filter-options` — dropdown options (FYE, milestone, staff, company, templates, statuses)

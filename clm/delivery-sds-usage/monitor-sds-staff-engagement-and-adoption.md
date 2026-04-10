# Monitor SDS Staff Engagement and Adoption

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Monitor SDS Staff Engagement and Adoption |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin / Operations Manager |
| **Business Outcome** | Gives admins visibility into SDS platform adoption — how many staff are active, how engaged they are with tasks, and whether engagement is trending — so they can identify underutilisation and coach team performance. |
| **Entry Point / Surface** | Sleek App > Delivery > Analytics > SDS Usage Dashboard (`/delivery/analytics/sds-usage-dashboard`) |
| **Short Description** | Displays a summary dashboard and per-staff engagement table showing engagements, status changes, proofs added, tasks assigned, and companies worked on — filterable by time period and individual staff, with CSV export for both summary and staff-engagement views. Results are cached on the backend for performance. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Service Delivery API (`VITE_SERVICE_DELIVERY_API_URL`); sits alongside Staff Task Distribution and Staff Assignment Overview dashboards in the same Analytics nav group |
| **Service / Repository** | sleek-billings-frontend, sleek-service-delivery-api |
| **DB - Collections** | PostgreSQL (TypeORM): `tasks`, `task_activities`, `users`, `team_assignments` |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Are markets SG/HK/AU/UK all enabled or is this SG-only? Is the `exportType` extensible beyond `summary` / `staff-engagement`? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Frontend entry point (sleek-billings-frontend)
- `src/App.jsx:202` — lazy-loaded route: `<Route path="delivery/analytics/sds-usage-dashboard" element={<SdsUsageDashboard />} />`
- `src/data/nav-rail-items.js:166–168` — nav label `"SDS Usage Dashboard"` under Delivery > Analytics

### Frontend UI component
- `src/pages/Delivery/Analytics/SdsUsageDashboard.jsx`
  - Period selector: `["Daily", "Weekly", "Monthly"]` — maps to rolling date windows (today, −6 days, −29 days)
  - Staff filter dropdown: populated from `getStaffEngagement({ limit: 2000 })` on load
  - Summary stat cards: Total engagements (with trend %), Tasks completed, Active staff, Total tasks (period window)
  - Staff engagement table columns: Staff name · Companies assigned · Activity types (badge per `byActivityType` key) · Status changes · Proofs added · Tasks assigned · Total engagements
  - Pagination: 30 rows/page via `meta.total`
  - Export button: calls `exportSdsUsage`, downloads blob as `sds-usage-report-<date>.csv`

### Activity type keys observed
- `STATUS_CHANGE` — counts towards `statusChanges`
- `FILE` — counts towards `proofsAdded`
- `COMMENT_AND_FILE` — also counts towards `proofsAdded`
- Additional keys rendered dynamically via `humanizeActivityType(key)`

### Backend API (sleek-service-delivery-api)
- Controller: `src/analytics/controllers/sds-usage-analytics.controller.ts`
  - Guard: `@SleekBackAuth('admin')` — admin role required (back-office internal auth)
  - Tag: `analytics/sds-usage`

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/analytics/sds-usage/summary` | Aggregate metrics: active staff, total tasks/engagements, weekly trend %, avg engagements per staff |
| `GET` | `/analytics/sds-usage/staff-engagement` | Paginated per-staff breakdown with weekly time-series, task counts, company counts, last activity date |
| `POST` | `/analytics/sds-usage/export` | CSV export of summary or staff-engagement data; streams response |

- Service: `src/analytics/services/sds-usage-analytics.service.ts`
  - Caching: `CACHE_MANAGER` (Redis) with `ANALYTICS_CACHE_TTL_MS` TTL applied to both summary and staff-engagement results
  - Repositories (TypeORM / PostgreSQL):
    - `Task` — task status, due dates, assignee; statuses `DONE`, `TO_DO`; overdue = past due and not done; due-soon = within 14 days
    - `TaskActivity` — engagement events; grouped by `performedByUserId` and `activityType`; weekly bucketing via `date_trunc('week', createdAt)`
    - `User` — staff identity (id, firstName, lastName, email); active = has at least one `TeamAssignment`
    - `TeamAssignment` — maps staff to companies (`companyId`); used for `companiesAssigned` count
  - Weekly trend: compares last two ISO weeks; engagement trend % = `((lastWeek - prevWeek) / prevWeek) * 100`
  - Export: streams CSV via `StreamableFile`; staff-engagement export paginates internally using `ANALYTICS_CSV_EXPORT_PAGE_SIZE`
  - DTOs: `src/analytics/dto/sds-usage-query.dto.ts`, `src/analytics/dto/sds-usage-response.dto.ts`
